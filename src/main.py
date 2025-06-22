from os import listdir
from os.path import isfile, join

from workflows.workflowFactory import WorkflowFactory
from exceptions.fatalError import FatalError
from utils.inputOutputUtils import getAndValidateUserInput
from utils.fileUtils import FileUtils
from utils.constants import CLI

from postClipHandling.oAuthSetup import verifyOAuthIsSetup, configureOAuth

# Going to make this CLI tool to start... then make GUI

CLIP_CONFIGS_PATH = "clipConfigs/"

workflowFactory = WorkflowFactory()

def printOptions():
    print(f"{CLI.TITLE_LINE}Options{CLI.TITLE_LINE}")
    print("1. Setup a clipping config")
    print("2. Run a clipping config")
    print("3. List clipping configs")
    print("4. Verify/setup OAUTH")

def handleOption(option):
    if option == "1":
        runSetupWorkflow()
    elif option == "2":
        clipConfigToRun = getAndValidateUserInput(
            inputText="Enter the name of the clip config you'd like to run: ",
            errorText="Must be a valid JSON file.",
            conditional=lambda pathToClipConfig: FileUtils.isValidJsonFile(f"clipConfigs/{pathToClipConfig}"),
        )

        runClippingWorkflow(clipConfigToRun)
    elif option == "3":
        listClippingConfigs()
    elif option == "4":
        verifyOrSetupOAuth()
    else:
        print("Unknown option...")

def runSetupWorkflow():
    workflow = workflowFactory.createSetupWorkflow()
    try:
        workflowCompletedSucessfully = workflow.start()

        if workflowCompletedSucessfully:
            runWorkflow = input("Would you like to begin running this clipping config? (y|n) ")
            runWorkflow = runWorkflow.lower() == "y"
            if runWorkflow:
                runClippingWorkflow(workflow.clipConfigFileName)
    except FatalError as e:
        print(f"Fatal error caught: {e}")

def runClippingWorkflow(clipConfigFileName):
    runWorkflow = workflowFactory.createRunWorkflow(
        clipConfigFileName = clipConfigFileName,
    )
    runWorkflow.start()
    quit()

def listClippingConfigs():
    onlyfiles = [f for f in listdir(CLIP_CONFIGS_PATH) if isfile(join(CLIP_CONFIGS_PATH, f))]

    print(f"{CLI.TITLE_LINE}CLIP CONFIGS{CLI.TITLE_LINE}")
    for file in onlyfiles:
        print(f"Clipconfig: {file}")

def verifyOrSetupOAuth():
    print("Would you like to verify or setup/reconfigure OAUTH?")
    userInput = getAndValidateUserInput(
        inputText="Input (v)erify or (s)etup: ",
        errorText="Please enter 'v' or 's'.",
        conditional=lambda userInput: userInput == "v" or userInput == "s",
    )

    if userInput == "v":
        verifyOAuth()
    elif userInput == "s":
        setupOAuth()

def verifyOAuth():
    pathToOAuthConfig = getAndValidateUserInput(
        inputText="Please enter in the path to your OAUTH config: ",
        errorText="Given input was not a valid json file.",
        conditional=lambda userInput: FileUtils.isValidJsonFile(userInput),
    )
    verifyOAuthIsSetup(pathToOAuthConfig)

def setupOAuth():
    pathToOAuthConfig = getAndValidateUserInput(
        inputText="Please enter in the output path of the OAuth config: ",
        errorText="Output path must end if '.json'.",
        conditional=lambda userInput: userInput.endswith(".json"),
    )
    configureOAuth(pathToOAuthConfig)

def main():
    print(f"{CLI.TITLE_LINE}Welcome to AutoClipper{CLI.TITLE_LINE}")
    print("This is the preliminary CLI version. GUI to come")

    while True:
        printOptions()
        option = input("Option: ")
        handleOption(option.strip())

if __name__ == "__main__":
    main()
