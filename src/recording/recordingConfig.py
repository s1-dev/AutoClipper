class RecordingConfig:
    
    def __init__(
            self,
            modelType,
            pathToModel,
            startRecordingOnDetection,
            verboseMode,
            toggleThreshold,
            indefiniteClips,
            numberOfClips,
            minimumClipLength,
            maximumClipLength,
        ):
            self.modelType = modelType
            self.pathToModel = pathToModel
            self.startRecordingOnDetection = startRecordingOnDetection
            self.verboseMode = verboseMode
            self.toggleThreshold = toggleThreshold
            self.indefiniteClips = indefiniteClips
            self.numberOfClips = numberOfClips
            self.minimumClipLength = minimumClipLength
            self.maximumClipLength = maximumClipLength

    def toDict(self):
        recordingConfig = {
            'modelType': self.modelType,
            'pathToModel': self.pathToModel,
            'startRecordingOnDetection': self.startRecordingOnDetection,
            'verboseMode': self.verboseMode,
            'toggleThreshold': self.toggleThreshold,
            'indefiniteClips': self.indefiniteClips,
            'numberOfClips': self.numberOfClips,
            'minimumClipLength': self.minimumClipLength,
            'maximumClipLength': self.maximumClipLength,
        }
        
        return recordingConfig
            