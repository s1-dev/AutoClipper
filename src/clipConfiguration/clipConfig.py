from datetime import datetime
import json

class ClipConfig:

    def __init__(self):
        self.__creationDate = datetime.now().isoformat()
        self.__obsServerConnectionConfig = {}
        self.__obsSceneConfig = {}
        self.__seleniumCommand = {}
        self.__recordingConfig = {}
        self.__clipSavingConfig = {}

    def loadFromJson(self, clipConfigFileName):
        with open(f"clipConfigs/{clipConfigFileName}", "r") as jsonFile:
            jsonData = json.load(jsonFile)

        self.__creationDate = jsonData['creationDate']
        self.__obsServerConnectionConfig = jsonData['obsServerConnectionConfig']
        self.__obsSceneConfig = jsonData['obsSceneConfig']
        self.__seleniumCommand = jsonData['seleniumCommand']
        self.__recordingConfig = jsonData['recordingConfig']
        self.__clipSavingConfig = jsonData['clipSavingConfig']

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
    
    def setRecordingConfig(self, recordingConfig):
        self.__recordingConfig = recordingConfig
    
    def getRecordingConfig(self):
        return self.__recordingConfig
    
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
            'recordingConfig': self.__recordingConfig,
            'clipSavingConfig': self.__clipSavingConfig,
        }
