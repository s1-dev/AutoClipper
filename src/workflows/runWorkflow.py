from recording.obsClient import ObsClient
from postClipHandling.oAuthSetup import isOAuthSetup
from postClipHandling.youtubeUploader import uploadYoutubeVideo
from utils.fileUtils import FileUtils
from utils.dateUtils import getCurrentDateUserFacing, getCurrentEpoch
from postClipHandling.transcriptGenerator import genTranscript
from postClipHandling.ytDetailGenerator import generateYtDetails
from metrics.generalLogger import GeneralLogger
from metrics.workflowLog import WorkflowLog, ClipData, LocalClipState, UploadStatus
from postClipHandling.clipSavingConfig import ExternalPlatform
#from utils.asyncUtils import runCoroutine, creatTask, readOutputToThread, blockingTimer

import logging
import asyncio
import subprocess
import mss
import numpy as np
import cv2
import sys
from ultralytics import YOLO

MAX_YT_TITLE_LEN = 100
MAX_YT_DESC_LEN = 5000
MAX_YT_TAG_LEN = 500

SAVE_QUEUE_TASK_NAME = "saveQueueTask"
MODEL_DETECTION_TASK_NAME = "modelDetectionTask"


logging.getLogger("ultralytics").disabled = True # TODO - allow user to dictate if they want logs or not

class RunWorkflow:

    # TODO - before workflow runs, run some sort of verification that verifies the user has setup OAUTH and what not

    def __init__(
        self,
        clipConfig,
        configName,
    ):
        self.clipConfig = clipConfig
        self.obsClient = None
        self.targetedContentRef = None
        self.runningTasks = []
        self.saveQueue = asyncio.Queue(maxsize=20)
        self.clipCounter = 0
        self.logger = GeneralLogger(configName=configName)
        self.workflowLog = WorkflowLog(outputFolder=self.logger.getLoggingDir())
        self.finished = False

    def start(self):
        # TODO Validation workflow that validates clipping config contents before starting workflow    
        self.startObs()
        return self.finished
        
    def startObs(self):
        print("Please ensure that OBS is started") # Eventually have it automatically launch
        self.logger.logSync("Attempting OBS websocket connection")

        obsServerConfig = self.clipConfig.getObsServerConnectionConfig()
        obsClient = ObsClient(
            host=obsServerConfig['serverAddress'],
            port=obsServerConfig['serverPort'],
            password=obsServerConfig['serverPassword'],
        )

        obsSceneConfig = self.clipConfig.getObsSceneConfig()
        obsClient.setScene(obsSceneConfig['sceneName'])
        obsClient.setSource(
            sceneName=obsSceneConfig['sceneName'],
            itemId=obsSceneConfig['sourceItemId'],
        )

        clipSavingConfig = self.clipConfig.getClipSavingConfig()
        obsClient.setRecordDirectory(clipSavingConfig['savingPath'])

        self.obsClient = obsClient

        self.launchTargetContent()        

    def launchTargetContent(self):
        self.logger.logSync("Launching targeted content")

        seleniumCommand = self.clipConfig.getSeleniumCommand()
        args = seleniumCommand['baseCommand'].split(' ')
        args += seleniumCommand['args']
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        )
        self.targetedContentRef = process

        asyncio.run(self._handleTargetedContentOutput())

    async def _handleTargetedContentOutput(self):
        await self.logger.log("Waiting for targeted content to initialize")

        process = self.targetedContentRef
        while process.poll() is None:
            statusUpdate = await self._readOutputToThread(process.stdout)
            if statusUpdate == "INITIALIZED":
                await self.logger.log("Targeted content communicated that it is initialized")
                saveQueueTask = asyncio.create_task(self.saveQueueListener(), name=SAVE_QUEUE_TASK_NAME)
                modelDetectionTask = asyncio.create_task(self.launchDetectionModel(), name=MODEL_DETECTION_TASK_NAME)

                self.runningTasks.extend([saveQueueTask, modelDetectionTask])
            elif statusUpdate == "COMPLETED":
                await self.logger.log("Targeted content communicated that it is complete")
                await self.killAndFinishWorkflow()       

    async def _readOutputToThread(self, pipe):
        return (await asyncio.to_thread(pipe.readline)).strip()          

    async def _sendMessageToSubprocess(self, message: str):
        if self.targetedContentRef and self.targetedContentRef.stdin:
            self.targetedContentRef.stdin.write(message + '\n')
            await asyncio.to_thread(self.targetedContentRef.stdin.flush)
    
    async def launchDetectionModel(self):
        await self.logger.log("Image detection launching")

        config = self.clipConfig.getRecordingConfig()
        startOnDetect = bool(config['startRecordingOnDetection'])
        indefiniteClips = bool(config['indefiniteClips'])
        maxClips = int(config['numberOfClips'])
        minLength = int(config['minimumClipLength'])
        maxLength = int(config['maximumClipLength'])
        verbose = bool(config['verboseMode'])
        toggleThreshold = config['toggleThreshold']
        model = YOLO(config['pathToModel'], verbose=verbose)

        recordingToggleActionConfigs = config["recordingToggleActionConfigs"]
        onStopRecordActionConfig = recordingToggleActionConfigs.get("onStopRecordActionConfig")
        isOnStopRecordingActionEnabled = bool(onStopRecordActionConfig)

        onStartRecordActionConfig = recordingToggleActionConfigs.get("onStartRecordActionConfig")
        isOnStartRecordingActionEnabled = bool(onStartRecordActionConfig)

        screen = mss.mss()
        monitor = screen.monitors[1]
        confidenceThreshold = 0.7
        detectedCount = undetectedCount = 0
        recStartedActionDone = recStoppedActionDone = False
        isRecording = False
        minClipTime = maxClipTime = -1

        while True:
            if not indefiniteClips and self.clipCounter >= maxClips:
                await self.killAndFinishWorkflow()

            await asyncio.sleep(1)

            if isRecording and getCurrentEpoch() >= maxClipTime:
                await self.logger.log("Recording stopped because maximum clip length was hit")
                await self._stopRecordingAndQueue()
                await self.logger.log("Returned to detection loop after stopping recording")
                isRecording = False
                recStoppedActionDone = False
                minClipTime = maxClipTime = -1
                detectedCount = undetectedCount = 0
                recordingToggledTime = getCurrentEpoch()
                continue

            frame = self._captureFrame(screen, monitor)
            detectionTriggered = self._detectImage(model, frame, confidenceThreshold)

            if detectionTriggered and startOnDetect:
                if verbose:
                    print("Image detected")
                undetectedCount = 0
                detectedCount += 1

                if detectedCount >= toggleThreshold and not isRecording:
                    success = await self._startRecording()
                    if not success:
                        await self.abortWorkflow()
                    now = getCurrentEpoch()
                    minClipTime = now + minLength
                    maxClipTime = now + maxLength
                    isRecording = True
                    recStartedActionDone = False
                    recordingToggledTime = getCurrentEpoch()

            else:
                if verbose:
                    print("Image not detected")
                detectedCount = 0
                undetectedCount += 1

                if undetectedCount >= toggleThreshold and isRecording:
                    await self.logger.log(f"Stop recording since the image has not been detected for {undetectedCount} cycles")
                    
                    currentTime = getCurrentEpoch()
                    if currentTime < minClipTime:
                        await self._stopRecordingWithoutSaving()
                    else:
                        await self._stopRecordingAndQueue()

                    await self.logger.log("Returned to detection loop after stopping recording")
                    
                    isRecording = False
                    recordingToggledTime = getCurrentEpoch()
                    recStoppedActionDone = False
                    maxClipTime = -1
                    
            if isOnStartRecordingActionEnabled:
                if not recStartedActionDone and (recordingToggledTime + int(onStartRecordActionConfig["actionDelayTime"])) >= getCurrentEpoch():
                    await self._sendMessageToSubprocess(onStartRecordActionConfig["action"])
                    recStartedActionDone = True

            if isOnStopRecordingActionEnabled:
                if not recStoppedActionDone and (recordingToggledTime + int(onStopRecordActionConfig["actionDelayTime"])) >= getCurrentEpoch():
                    await self._sendMessageToSubprocess(str(onStopRecordActionConfig["action"]))
                    recStoppedActionDone = True

    def _captureFrame(self, screen, monitor):
        grab = screen.grab(monitor)
        frame = np.array(grab)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def _detectImage(self, model, frame, threshold):
        results = model(frame)
        for result in results:
            for box in result.boxes:
                if box.conf[0] > threshold:
                    return True
        return False

    async def _startRecording(self):
        await self.logger.log("Attempting to start recording")
        return await self.obsClient.startRecordingAsync()

    async def _stopRecordingAndQueue(self):
        outputPath = await self.obsClient.stopRecordingAsync()
        if outputPath is None:
            await self.abortWorkflow()
        self.clipCounter += 1

        await self.logger.log(f"Recording stopped for clip number {self.clipCounter}")
        self.workflowLog.addEntry(
            ClipData(
                clipNumber=self.clipCounter,
                localClipState=None,
                savedPath=None,
                platform=None,
                uploadStatus=None,
            )
        )  

        await self.saveQueue.put((outputPath, self.clipCounter))     

    async def _stopRecordingWithoutSaving(self):
        await self.logger.log("Recording stopping before the minimum clip threshold is surpassed")
        outputPath = await self.obsClient.stopRecordingAsync()
        if outputPath is None:
            await self.abortWorkflow()
        else:
            await self.logger.log(f"Recording stopped early and discarded: {outputPath}")
            try:
                FileUtils.deleteFile(outputPath)
                await self.logger.log(f"Clip discarded: {outputPath}")
            except Exception as e:
                await self.logger.log(f"Failed to delete discarded clip: {e}")

    async def saveQueueListener(self):
        while True:
            (videoOutputPath, clipNumber) = await self.saveQueue.get()
            await self.launchSave(videoOutputPath, clipNumber)
            self.saveQueue.task_done()
        
    async def launchSave(self, outputPath, clipNumber):
        await self.logger.log(f"Post clip saving/handling starting - clip number {clipNumber}")

        clipSavingConfig = self.clipConfig.getClipSavingConfig()
        externalPlatformConfig = clipSavingConfig["externalPlatformConfig"]
        externalPlatform = ExternalPlatform.fromValue(externalPlatformConfig["platform"])

        wasUploaded = False
        if externalPlatform == ExternalPlatform.YOUTUBE:
            wasUploaded = await self._startYoutubeUpload(outputPath, clipNumber, externalPlatformConfig)
        else:
            errorMsg = "Unsupported external platform"
            await self.logger.log(errorMsg)
            raise(errorMsg)

        keepVideosAfterUpload = bool(clipSavingConfig["keepVideosAfterUpload"])
        savingPath = str(clipSavingConfig["savingPath"])

        wasDeleted = False
        finalPath = outputPath

        if not keepVideosAfterUpload:
            try:
                FileUtils.deleteFile(outputPath)
                wasDeleted = True
                await self.logger.log(f"Clip {clipNumber} discarded: {outputPath}")
            except Exception as e:
                await self.logger.log(f"Failed to delete clip {clipNumber}: {e}")

        if savingPath != "" and not wasDeleted:
            try:
                FileUtils.moveFileToDir(outputPath, savingPath)
                finalPath = savingPath
                await self.logger.log(f"Clip {clipNumber} moved: {savingPath}")
            except Exception as e:
                await self.logger.log(f"Failed to move clip {clipNumber}: {e}")

        currClipData = self.workflowLog.getEntry(clipNumber)
        updatedClipData = ClipData(
            clipNumber=currClipData.clipNumber,
            localClipState=LocalClipState.SAVED if not wasDeleted else LocalClipState.DELETED,
            savedPath=finalPath,
            platform=externalPlatform,
            uploadStatus=UploadStatus.UPLOADED if wasUploaded else UploadStatus.FAILED,
        )

        self.workflowLog.updateEntry(clipNumber, updatedClipData)

    async def _startYoutubeUpload(
        self,
        outputPath: str, 
        clipNumber: int,
        youtubeConfig: dict,
    ) -> bool:
        await self.logger.log(f"Starting youtube uploading subworkflow for clip {clipNumber}")
        pathToOAuthConfig = str(youtubeConfig["pathToOAuthConfig"])

        defaultDetails = {
            'title': f"{youtubeConfig["videoTitle"]} {clipNumber} | {getCurrentDateUserFacing()}",
            'description': youtubeConfig["videoDesc"],
            'keywords': youtubeConfig["videoTags"],
            'categoryId' : youtubeConfig["categoryId"],
            'privacyStatus': youtubeConfig["privacyStatus"],
        }

        if not isOAuthSetup(pathToOAuthConfig):
            errorMsg = f"OAUTH config is not setup for clip {clipNumber}"
            await self.logger.log(errorMsg)
            raise Exception(errorMsg)
        else:
            await self.logger.log(f"OAUTH is configured for clip {clipNumber}")

        smartHandlingConfig = youtubeConfig["smartHandlingConfig"] 

        if smartHandlingConfig != None and smartHandlingConfig != "":
            return await self._uploadYoutubeVideoWithSmartDetails(clipNumber, outputPath, pathToOAuthConfig, smartHandlingConfig, defaultDetails)
        else: 
            return await self._uploadYoutubeVideo(clipNumber, outputPath, pathToOAuthConfig, defaultDetails)
    
    async def _uploadYoutubeVideoWithSmartDetails(
        self, 
        clipNumber: int,
        outputPath: str, 
        pathToOAuthConfig: str,
        smartHandlingConfig: dict, 
        fallbackDetails: dict
    ) -> bool:
        await self.logger.log(f"Attempting to generate transcript for clip {clipNumber}")
        videoTranscript = await genTranscript(outputPath)
        if videoTranscript == None:
             await self.logger.log(f"Failed to generate video transcript, uploading with default details for clip {clipNumber}")
             return await self._uploadYoutubeVideo(clipNumber, outputPath, pathToOAuthConfig, fallbackDetails)

        await self.logger.log(f"Attempting to generate smart details for clip {clipNumber}")
        smartDetails = await generateYtDetails(videoTranscript, smartHandlingConfig)
        print(f"smart details: {smartDetails}")
        if smartDetails == None:
            await self.logger.log(f"Failed to generate smart details, uploading with default details for clip {clipNumber}")
            return await self._uploadYoutubeVideo(clipNumber, outputPath, pathToOAuthConfig, fallbackDetails)
        
        # We should abstract AI query validation out of the workflow
        title = smartDetails["videoTitle"]
        if title and len(title) > MAX_YT_TITLE_LEN:
            title = title[:(MAX_YT_TITLE_LEN-3)] + "..." # LOL. We will want to just requery the AI until the len is less than 100
        
        description = smartDetails["videoDesc"]
        if description and len(description) > MAX_YT_DESC_LEN:
            description = description[:(MAX_YT_DESC_LEN-3)] + "..."

        keywords = smartDetails["videoTags"]
        if keywords and isinstance(keywords, list):
            # If it's a list, take off white leading/trailing whitespace in entries and join to csv
            keywords = ",".join([tag.strip() for tag in keywords if isinstance(tag, str)])
            keywords = keywords[:MAX_YT_TAG_LEN]

        videoDetails = {
            'title': title or fallbackDetails["videoTitle"],
            'description': description or fallbackDetails["videoDesc"],
            'keywords': keywords or fallbackDetails["videoTags"],
            'categoryId': fallbackDetails["categoryId"],
            'privacyStatus': fallbackDetails["privacyStatus"],
        }

        return await self._uploadYoutubeVideo(clipNumber, outputPath, pathToOAuthConfig, videoDetails)
        
    async def _uploadYoutubeVideo(
        self, 
        clipNumber: int,
        outputPath: str, 
        pathToOAuthConfig: str, 
         videoDetails: dict
    ):
        try:
            result = await asyncio.to_thread(uploadYoutubeVideo, outputPath, pathToOAuthConfig, videoDetails)
            await self.logger.log(f"upload thread finished, result for clip {clipNumber}: {result}")
            return result
        except Exception as e:
            await self.logger.log(f"Exception in upload thread for clip {clipNumber}: {e}")
            return False

    async def abortWorkflow(self, message="Aborting due to critical error."):
        await self.logger.log(f"Aborting workflow due to: {message}")
        await self.logger.flush()
        print(f"{message}", file=sys.stderr)

        self.killTargetedContent()
        await self.killTasks()

        sys.exit(1)

    async def killAndFinishWorkflow(self):
        await self.logger.log("Killing active threads and processes and finishing the workflow")

        self.killTargetedContent()
        await self.killTasks(tasksToKeepAlive=[SAVE_QUEUE_TASK_NAME])

        if self.obsClient and self.obsClient.isRecording():
            await self.logger.log("OBS is still recording. Stopping and saving last clip.")
            await self._stopRecordingAndQueue()

        await self.logger.log("Waiting for remaining clips in queue to finish saving and uploading.")
        await self.saveQueue.join()

        await self.finishWorkflow()

    def killTargetedContent(self):
        if self.targetedContentRef and self.targetedContentRef.poll() is None:
            self.targetedContentRef.kill()

    async def killTasks(self, tasksToKeepAlive = []):
        for task in self.runningTasks:
            if task.get_name() in tasksToKeepAlive:
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"Task {task.get_name()} cancelled.")

    async def finishWorkflow(self):
        # TODO Generate post workflow report. Json or text file maybe? 
        # Output to user, but also save 
        await self.logger.log("Workflow finished")
        await self.logger.flush()
        self.workflowLog.outputToFile()

        self.finished = True
