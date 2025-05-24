from recording.obsClient import ObsClient
from postClipHandling.oAuthSetup import isOAuthSetup
from postClipHandling.youtubeUploader import uploadYoutubeVideo
from utils.fileUtils import FileUtils
from utils.dateUtils import getCurrentDateUserFacing
from postClipHandling.transcriptGenerator import genTranscript
from postClipHandling.ytDetailGenerator import generateYtDetails
#from utils.asyncUtils import runCoroutine, creatTask, readOutputToThread, blockingTimer

import logging
import asyncio
import subprocess
import mss
import numpy as np
import cv2
import time
import sys
from ultralytics import YOLO

MAX_YT_TITLE_LEN = 100
MAX_YT_DESC_LEN = 5000
MAX_YT_TAG_LEN = 500

logging.getLogger("ultralytics").disabled = True # TODO - allow user to dictate if they want logs or not

class RunWorkflow:

    # TODO - before workflow runs, run some sort of verification that verifies the user has setup OAUTH and what not

    def __init__(
        self,
        clipConfig,
    ):
        self.clipConfig = clipConfig
        self.obsClient = None
        self.targetedContentRef = None
        self.runningTasks = []
        self.saveQueue = asyncio.Queue(maxsize=5)
        self.clipCounter = 0
        self.finished = False

    def start(self):
        # TODO Validation workflow that validates clipping config contents before starting workflow
        self.startObs()
        return self.finished
        
    def startObs(self):
        print("Please ensure that OBS is started") # Eventually have it automatically launch
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

        self.launchTargetContet()        

    def launchTargetContet(self):
        print("Launching targeted content...")
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
        process = self.targetedContentRef
        while process.poll() is None:
            statusUpdate = await self._readOutputToThread(process.stdout)
            if statusUpdate == "INITIALIZED":
                saveQueueTask = asyncio.create_task(self.saveQueueListener())
                modelDetectionTask = asyncio.create_task(self.launchDetectionModel())

                self.runningTasks.extend([saveQueueTask, modelDetectionTask])
            elif statusUpdate == "COMPLETED":
                await self.killAndFinishWorkflow()       

    async def _readOutputToThread(self, pipe):
        return (await asyncio.to_thread(pipe.readline)).strip()          

    async def _sendMessageToSubprocess(self, message: str):
        if self.targetedContentRef and self.targetedContentRef.stdin:
            self.targetedContentRef.stdin.write(message + '\n')
            await asyncio.to_thread(self.targetedContentRef.stdin.flush)
    
    async def launchDetectionModel(self):
        print("Launching image detection...")

        # === Load config ===
        config = self.clipConfig.getRecordingConfig()
        startOnDetect = bool(config['startRecordingOnDetection'])
        indefiniteClips = bool(config['indefiniteClips'])
        maxClips = int(config['numberOfClips'])
        minLength = int(config['minimumClipLength'])
        maxLength = int(config['maximumClipLength'])
        verbose = bool(config['verboseMode'])
        toggleThreshold = config['toggleThreshold']
        model = YOLO(config['pathToModel'], verbose=verbose)

        # === Setup state ===
        screen = mss.mss()
        monitor = screen.monitors[1]
        confidenceThreshold = 0.7
        detectedCount = undetectedCount = 0
        detectedActionDone = undetectedActionDone = False
        isRecording = False
        minClipTime = maxClipTime = -1

        while True:
            if not indefiniteClips and self.clipCounter >= maxClips:
                await self.killAndFinishWorkflow()

            await asyncio.sleep(1)

            # === Stop if clip hit max length ===
            if isRecording and time.time() >= maxClipTime:
                print("Stop recording since we hit the maximum clip length.")
                await self._stopRecordingAndQueue()
                isRecording = False
                undetectedActionDone = False
                minClipTime = maxClipTime = -1
                detectedCount = undetectedCount = 0
                continue

            # === Run detection model ===
            frame = self._captureFrame(screen, monitor)
            detectionTriggered = self._detectImage(model, frame, confidenceThreshold)

            # === Process detection result ===
            if detectionTriggered and startOnDetect:
                if verbose:
                    print("Image detected")
                undetectedCount = 0
                detectedCount += 1

                if detectedCount >= toggleThreshold and not isRecording:
                    success = await self._startRecording()
                    if not success:
                        await self.abortWorkflow()
                    now = time.time()
                    minClipTime = now + minLength
                    maxClipTime = now + maxLength
                    isRecording = True
                    detectedActionDone = False

            else:
                if verbose:
                    print("Image not detected")
                detectedCount = 0
                undetectedCount += 1

                if undetectedCount >= toggleThreshold and isRecording:
                    print("Stop recording since we stopped detecting the image.")
                    
                    currentTime = time.time()
                    if currentTime < minClipTime:
                        print(f"Attempted to stop recording before the minimum clip time, discarding clip.")
                        await self._stopRecordingWithoutSaving()
                    else:
                        await self._stopRecordingAndQueue()
                    
                    isRecording = False
                    undetectedActionDone = False
                    maxClipTime = -1

            # === Trigger subprocess commands if needed ===
            if not undetectedActionDone and undetectedCount >= 30:
                await self._sendMessageToSubprocess("REFRESH")
                undetectedActionDone = True

            # Uncomment if needed
            # if not detectedActionDone and detectedCount >= 30:
            #     await self._sendMessageToSubprocess("REFRESH")
            #     detectedActionDone = True

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
        print("Attempting to start recording...")
        return await self.obsClient.startRecordingAsync()

    async def _stopRecordingAndQueue(self):
        print("Attempting to stop recording...")
        outputPath = await self.obsClient.stopRecordingAsync()
        if outputPath is None:
            await self.abortWorkflow()
        self.clipCounter += 1
        await self.saveQueue.put((outputPath, self.clipCounter))     

    async def _stopRecordingWithoutSaving(self):
        outputPath = await self.obsClient.stopRecordingAsync()
        if outputPath is None:
            await self.abortWorkflow()
        else:
            print(f"Recording stopped early and discarded: {outputPath}")
            try:
                FileUtils.deleteFile(outputPath)
                print("Early recording deleted.")
            except Exception as e:
                print(f"Failed to delete discarded clip: {e}")
    
    async def saveQueueListener(self):
        while True:
            (videoOutputPath, clipCounter) = await self.saveQueue.get()
            await self.launchSave(videoOutputPath, clipCounter)
            self.saveQueue.task_done()
        
    async def launchSave(self, outputPath, clipCounter):
        clipSavingConfig = self.clipConfig.getClipSavingConfig()
        externalPlatformConfig = clipSavingConfig["externalPlatformConfig"]

        if externalPlatformConfig["platform"] == "YOUTUBE":
            await self._startYoutubeUpload(outputPath, clipCounter, externalPlatformConfig)
        else:
            raise("Unsupported external platform")

        keepVideosAfterUpload = bool(clipSavingConfig["keepVideosAfterUpload"])
        savingPath = str(clipSavingConfig["savingPath"])

        if not keepVideosAfterUpload:
            FileUtils.deleteFile(outputPath) # This returns a bool. Should we handle? 

        if savingPath != "":
            FileUtils.moveFileToDir(outputPath, savingPath) # Also returns a bool

    async def _startYoutubeUpload(
        self, 
        outputPath: str, 
        clipCounter: int,
        youtubeConfig: dict,
    ):
        pathToOAuthConfig = str(youtubeConfig["pathToOAuthConfig"])

        defaultDetails = {
            'title': f"{youtubeConfig["videoTitle"]} {clipCounter} | {getCurrentDateUserFacing()}",
            'description': youtubeConfig["videoDesc"],
            'keywords': youtubeConfig["videoTags"],
            'categoryId' : youtubeConfig["categoryId"],
            'privacyStatus': youtubeConfig["privacyStatus"],
        }

        if not isOAuthSetup(pathToOAuthConfig):
            raise Exception("OAUTH config is not setup")
        else:
            print("OAUTH is configured.")

        smartHandlingConfig = youtubeConfig["smartHandlingConfig"] 

        if smartHandlingConfig != None and smartHandlingConfig != "":
            await self._uploadYoutubeVideoWithSmartDetails(outputPath, pathToOAuthConfig, smartHandlingConfig, defaultDetails)
        else: 
            await self._uploadYoutubeVideo(outputPath, pathToOAuthConfig, defaultDetails)
    
    async def _uploadYoutubeVideoWithSmartDetails(
        self, 
        outputPath: str, 
        pathToOAuthConfig: str,
        smartHandlingConfig: dict, 
        fallbackDetails: dict
    ):
        # 1. Attempt to gen transcript 
        # 2. If error or none, fall back to default details 
        # 3. else, attempt query for smart details 
        # 4. If query fails, fall back to default details
        # 5. else, upload youtube video with details. 
        # Perhaps, we generate the dict in the workflow, and then pass it to uploader. This way there's no conditional logic in uploader

        print("Attempting to generate transcript...")
        videoTranscript = await genTranscript(outputPath)
        if videoTranscript == None:
             await self._uploadYoutubeVideo(outputPath, pathToOAuthConfig, fallbackDetails)
             return

        print("Attempting to generate details...")
        smartDetails = await generateYtDetails(videoTranscript, smartHandlingConfig)
        print(f"smart details: {smartDetails}")
        if smartDetails == None:
            await self._uploadYoutubeVideo(outputPath, pathToOAuthConfig, fallbackDetails)
            return
        
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

        await self._uploadYoutubeVideo(outputPath, pathToOAuthConfig, videoDetails)
        
    async def _uploadYoutubeVideo(self, outputPath: str, pathToOAuthConfig: str, videoDetails: dict):
        print("upload yt vid hit")
        try:
            result = await asyncio.to_thread(uploadYoutubeVideo, outputPath, pathToOAuthConfig, videoDetails)
            print("upload thread finished, result:", result)
        except Exception as e:
            print("Exception in upload thread:", e)

    async def abortWorkflow(self, message="Aborting due to critical error."):
        print(f"{message}", file=sys.stderr)

        if self.targetedContentRef and self.targetedContentRef.poll() is None:
            self.targetedContentRef.kill()

        for task in self.runningTasks:
            task.cancel()

        sys.exit(1)

    async def killAndFinishWorkflow(self):
        print("Stopping everything...")

        if self.targetedContentRef and self.targetedContentRef.poll() is None:
            self.targetedContentRef.kill()

        for task in self.runningTasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"Task {task.get_name()} cancelled.")

        await self._finishWorkflow()

    async def _finishWorkflow(self):
        # TODO Generate post workflow report. Json or text file maybe? 
        # Output to user, but also save 
        self.finished = True

# 1. launch obs
# 2. launch targeted content 
# 3. launch model to listen
# 4. once model detects logo, start recording 
# - determine how many consecutive non-logo frames warrant a stopage of recording. 120 (2 seconds)?
# - ensure that saving the video occurs on another thread. If recording fails, try n times and then just fall back to save the video to an mp4
# - Make an after workflow report: list of created clips, number of clips created, number of clips where an error occured

# - It may be time to switch core workflow over to Kotlin and have necessary python microservices 
# - Consider making a python only lite version, without unit tests
# We need to overhaul the configuration 
# figure out how to optimize taking screenshots 
