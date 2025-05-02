from os import listdir
from os.path import isfile, join

from workflows.workflowFactory import WorkflowFactory
from exceptions.fatalError import FatalError
from utils.inputOutputUtils import getAndValidateUserInput
from utils.fileUtils import FileUtils

from postClipHandling.oAuthSetup import verifyOAuthIsSetup

# Going to make this CLI tool to start... then make GUI

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

CLIP_CONFIGS_PATH = "clipConfigs/"

workflowFactory = WorkflowFactory()

def printOptions():
    print(f"{TITLE_LINE}Options{TITLE_LINE}")
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
        verifyOAuth()
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

def listClippingConfigs():
    onlyfiles = [f for f in listdir(CLIP_CONFIGS_PATH) if isfile(join(CLIP_CONFIGS_PATH, f))]

    print(f"{TITLE_LINE}CLIP CONFIGS{TITLE_LINE}")
    for file in onlyfiles:
        print(f"Clipconfig: {file}")

def verifyOAuth():
    pathToOAuthConfig = getAndValidateUserInput(
        inputText="Please enter in the path to your OAUTH config: ",
        errorText="Given input was not a valid json file.",
        conditional=lambda userInput: FileUtils.isValidJsonFile(userInput),
    )
    verifyOAuthIsSetup(pathToOAuthConfig)

def main():
    print(f"{TITLE_LINE}Welcome to AutoClipper{TITLE_LINE}")
    print("This is the preliminary CLI version. GUI to come")

    printOptions()
    option = input("Option: ")
    handleOption(option)

if __name__ == "__main__":
    main()

# Have stored configs: client settings, target video/website settings, AI settings, youtube settings 
# Start fresh workflow (setup workflow?)
# Start run workflow? As in take setup and run config
# AI stuff 
# Figure out how to locally store configs, securely
