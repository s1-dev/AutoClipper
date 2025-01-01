class CoventionalRecordingConfig:
    
    def __init__(
            self,
            clipTime,
            inBetweenInterval,
            indefiniteClips,
            numberOfClips,
        ):
            self.clipTime = clipTime
            self.inBetweenInterval = inBetweenInterval
            self.indefiniteClips = indefiniteClips
            self.numberOfClips = numberOfClips

    def toDict(self):
        recordingConfig = {
            'clipTime': self.clipTime,
            'inBetweenInterval': self.inBetweenInterval,
            'indefiniteClips': self.indefiniteClips,
        }
        if self.numberOfClips != None:
            recordingConfig['numberOfClips'] = self.numberOfClips
        return recordingConfig
            