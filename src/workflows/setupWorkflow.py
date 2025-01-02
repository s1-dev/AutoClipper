from exceptions.fatalError import FatalError
from clipConfiguration.clipConfig import ClipConfig
from recording.obsClientCreation import launchObsSetupWarning, retrieveObsClient
from recording.obsClientSetup import setObsScene, setObsSource
from contentTargeting.seleniumSetup import launchSeleniumSetupWarning, getSeleniumCommand
from recording.conventionalRecordingSetup import buildConventionalRecordingConfig
from postClipHandling.videoSavingSetup import buildClipSavingConfig
from utils.fileUtils import FileUtils

# Maybe make workflow as an object and hold each subworkflow config as properties

# Transition functions?

class SetupWorkflow():

    def __init__(self):
        self.obsClient = None
        self.mutableClipConfig = ClipConfig()
        self.finished = False
        self.clipConfigFileName = ""

    def start(self):
        self.createObsClient()
        return self.finished

    def createObsClient(self):
        launchObsSetupWarning()

        obsClient = retrieveObsClient()
        if obsClient == None:
            raise FatalError("Unable to connect to OBS web socket. Exiting workflow...")
        self.obsClient = obsClient

        self.mutableClipConfig.setObsServerConnectionConfig(obsClient.connectionInfoToDict())

        self.setupObsClient()

    def setupObsClient(self):
        sceneName = setObsScene(self.obsClient)
        if sceneName == None:
            raise FatalError(f"Unable to set OBS scene. Exiting workflow...")

        setSourceResult = setObsSource(self.obsClient, sceneName)
        if setSourceResult == None:
            raise FatalError(f"Unable to set OBS source for the {sceneName} scene. Exiting workflow...")
        
        (sourceName, sourceItemId) = setSourceResult

        self.mutableClipConfig.setObsSceneConfig(
            {
                'sceneName': sceneName,
                'sourceName': sourceName,
                'sourceItemId': sourceItemId,
            }
        )

        self.getTargetContent()
        # Ask user which scene to use
        # Ask user which source to use 
        # Add scene creation/cutomization? Issues with picking certain settings so probably implement later
        # Pass to client to 

    def getTargetContent(self):
        launchSeleniumSetupWarning()

        seleniumCommand = getSeleniumCommand() # Do sanitization here?

        if seleniumCommand == None:
            raise FatalError("Unable to craft selenium command. Exiting workflow...")
        
        self.mutableClipConfig.setSeleniumCommand(seleniumCommand.toDict())

        self.recordingSetup()
        # Get target URL to launch and watch
        # Allow user to implement actions to take on the website
        # Ex - CLick this button, maxmize screen, etc.
        # Have a subworkflow to do a test run for the user 
        # Run test? 
        # Pass content target to recording setup

    def recordingSetup(self):
        recordingConfig = None
        recordingConfig = buildConventionalRecordingConfig()

        if recordingConfig == None:
            raise FatalError("TODO")
        
        self.mutableClipConfig.setConventionalRecordingConfig(recordingConfig.toDict())
        
        self.savingSetup()
        # Ask user how we should create clips 
        # Timed? Certain intervals 
        # Add AI to examine video and cut at certain points. Probably implement with manual time boxxing for now 
        # Pass to youtube setup

    def savingSetup(self):
        clipSavingConfig = buildClipSavingConfig()


        # TODO setup youtube uploading

        self.mutableClipConfig.setClipSavingConfig(clipSavingConfig.toDict())

        self.setupConfirmation()
        # Ask user if they'd like to automatically upload clips to youtube 
        # if not, just ensure the video is saved locally to a certain PATH
        # else, get youtube auth token, probably? 
        
    def setupConfirmation(self):
        clipConfigDict = self.mutableClipConfig.toDict()
        print("Overview of clip configuration: ")
        print(clipConfigDict)
        isToReconfig = input("Would you like to reconfigure? (y|n) ")
        isToReconfig = isToReconfig.lower() == "y"

        if isToReconfig:
            self.__restartSetup()
        else:
            self.__saveSetup()
        # Show overview of user setup? (Maybe optional button)
        # Ask what the user wants to do with setup:
        #   - Just save, run a test (have sample 30 second video), or start automation workflow
        # Return to main menu? 

    def __restartSetup(self):
        self.__init__()
        self.start()
    
    def __saveSetup(self):
        clipConfigDir = "clipConfigs"
        if not FileUtils.doesDirExist(clipConfigDir):
            FileUtils.createDir(clipConfigDir)

        clipConfigName = input("Enter clip config file name: (note .json will be appended)")

        if not clipConfigName.endswith(".json"):
            clipConfigName += ".json"

        FileUtils.dictToJson(
            dictData=self.mutableClipConfig.toDict(),
            outputPath=clipConfigName,
        )
        self.__completeWorkflow(clipConfigName)

    def __completeWorkflow(self, clipConfigFileName):
        self.finished = True
        self.clipConfigFileName = clipConfigFileName
        