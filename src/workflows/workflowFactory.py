from workflows.setupWorkflow import SetupWorkflow
from workflows.runWorkflow import RunWorkflow
from clipConfiguration.clipConfig import ClipConfig

class WorkflowFactory:

    def createSetupWorkflow(self):
        return SetupWorkflow()

    def createRunWorkflow(
            self, 
            clipConfigFileName: str,
        ):
        clipConfig = ClipConfig()
        clipConfig.loadFromJson(clipConfigFileName)

        configName = clipConfigFileName.strip()
        if configName.endswith(".json"):
            configName = configName[:-5]

        return RunWorkflow(
            clipConfig=clipConfig,
            configName=configName,
        )
    