from workflows.workflowFactory import WorkflowFactory
from exceptions.fatalError import FatalError

# Going to make this CLI tool to start... then make GUI

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

workflowFactory = WorkflowFactory()

def printOptions():
    print(f"{TITLE_LINE}Options{TITLE_LINE}")
    print("1. Setup a clipping config")
    print("2. List clipping configs")

def handleOption(option):
    if option == "1":
        runSetupWorkflow()
    elif option == "2":
        print("TODO")
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
    workflowFactory.createRunWorkflow()


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
