from recording.obsClientCreation import launchObsSetupWarning, retrieveObsClient
from recording.obsClientSetup import setObsScene, setObsSource
from contentTargeting.seleniumSetup import launchSeleniumSetupWarning, getSeleniumScript

# Maybe make workflow as an object and hold each subworkflow config as properties

# Transition functions?

class SetupWorkflow():

    def __init__(self):
        self.obsClient = None
        self.mutableConfig = None

    def start(self):
        self.createObsClient()

    def createObsClient(self):
        launchObsSetupWarning()

        obsClient = retrieveObsClient()
        if obsClient == None:
            print("Unable to connect to OBS web socket. Exiting...")
            exit() # TODO Emit some sort of fatal error and return to menu. For now just exit program 
        self.obsClient = obsClient

        # TODO Update config

        self.setupObsClient()

    def setupObsClient(self):
        sceneName = setObsScene(self.obsClient)
        if sceneName == None:
            print("TODO")
            exit()

        setSourceResult = setObsSource(self.obsClient, sceneName)
        if setSourceResult == None:
            print("TODO")
            exit()
        
        (sourceName, sourceItemId) = setSourceResult

        # TODO Update config

        self.getTargetContent()

        # Ask user which scene to use
        # Ask user which source to use 
        # Add scene creation/cutomization? Issues with picking certain settings so probably implement later
        # Pass to client to 

    def getTargetContent(self):
        launchSeleniumSetupWarning()

        seleniumScriptPath = getSeleniumScript()

        # Get target URL to launch and watch
        # Allow user to implement actions to take on the website
        # Ex - CLick this button, maxmize screen, etc.
        # Have a subworkflow to do a test run for the user 
        # Run test? 
        # Pass content target to recording setup

    def recordingSetup(self):
        print("TODO")
        # Ask user how we should create clips 
        # Timed? Certain intervals 
        # Add AI to examine video and cut at certain points. Probably implement with manual time boxxing for now 
        # Pass to youtube setup

    def savingSetup(self):
        print("TODO")
        # Ask user if they'd like to automatically upload clips to youtube 
        # if not, just ensure the video is saved locally to a certain PATH
        # else, get youtube auth token, probably? 
        
    def setupConfirmation(self):
        print("TODO")
        # Show overview of user setup? (Maybe optional button)
        # Ask what the user wants to do with setup:
        #   - Just save, run a test (have sample 30 second video), or start automation workflow
        # Return to main menu? 
        