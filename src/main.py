from workflows.workflowFactory import WorkflowFactory
from exceptions.fatalError import FatalError

# Going to make this CLI tool to start... then make GUI

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

def printOptions():
    print(f"{TITLE_LINE}Options{TITLE_LINE}")
    print("1. Setup a clipping config")
    print("2. List clipping configs")

def handleOption(workflowFactory, option):
    if option == "1":
        workflow = workflowFactory.createSetupWorkflow()

        try:
            workflow.start()
        except FatalError as e:
            print(f"Fatal error caught: {e}")

    elif option == "2":
        print("TODO")
    else:
        print("Unknown option...")

def main():
    workflowFactory = WorkflowFactory()
    print(f"{TITLE_LINE}Welcome to AutoClipper{TITLE_LINE}")
    print("This is the preliminary CLI version. GUI to come")

    printOptions()
    option = input("Option: ")
    handleOption(workflowFactory, option)


if __name__ == "__main__":
    main()

# Have stored configs: client settings, target video/website settings, AI settings, youtube settings 
# Start fresh workflow (setup workflow?)
# Start run workflow? As in take setup and run config
# AI stuff 
# Figure out how to locally store configs, securely
