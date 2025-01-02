from datetime import datetime

class ClipConfig:

    def __init__(self):
        self.__creationDate = datetime.now().isoformat()
        self.__obsServerConnectionConfig = {}
        self.__obsSceneConfig = {}
        self.__seleniumCommand = {}
        self.__conventionalRecordingConfig = {}
        self.__clipSavingConfig = {}

    def getCreationDate(self):
        return self.__creationDate

    def setObsServerConnectionConfig(self, obsServerConnectionConfig):
        self.__obsServerConnectionConfig = obsServerConnectionConfig
    
    def getObsServerConnectionConfig(self):
        return self.__obsServerConnectionConfig
    
    def setObsSceneConfig(self, obsSceneConfig):
        self.__obsSceneConfig = obsSceneConfig
    
    def getObsSceneConfig(self):
        return self.__obsSceneConfig
    
    def setSeleniumCommand(self, seleniumCommand):
        self.__seleniumCommand = seleniumCommand

    def getSeleniumCommand(self):
        return self.__seleniumCommand
    
    def setConventionalRecordingConfig(self, conventionalRecordingConfig):
        self.__conventionalRecordingConfig = conventionalRecordingConfig
    
    def getConventionalRecordingConfig(self):
        return self.__conventionalRecordingConfig
    
    def setClipSavingConfig(self, clipSavingConfig):
        self.__clipSavingConfig = clipSavingConfig

    def getClipSavingConfig(self):
        return self.__clipSavingConfig
    
    def toDict(self):
        return {
            'creationDate': self.__creationDate,
            'obsServerConnectionConfig': self.__obsServerConnectionConfig,
            'obsSceneConfig': self.__obsSceneConfig,
            'seleniumCommand': self.__seleniumCommand,
            'conventionalRecordingConfig': self.__conventionalRecordingConfig,
            'clipSavingConfig': self.__clipSavingConfig,
        }
