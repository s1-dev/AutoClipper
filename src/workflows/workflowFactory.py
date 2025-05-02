from workflows.setupWorkflow import SetupWorkflow
from workflows.runWorkflow import RunWorkflow
from clipConfiguration.clipConfig import ClipConfig

class WorkflowFactory:

    def createSetupWorkflow(self):
        return SetupWorkflow()

    def createRunWorkflow(
            self, 
            clipConfigFileName,
        ):
        clipConfig = ClipConfig()
        clipConfig.loadFromJson(clipConfigFileName)

        return RunWorkflow(
            clipConfig = clipConfig
        )
    