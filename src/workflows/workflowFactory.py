from workflows.setupWorkflow import SetupWorkflow

class WorkflowFactory:

    def createSetupWorkflow(self):
        return SetupWorkflow()

    def createRunWorkflow(self):
        print("TODO")