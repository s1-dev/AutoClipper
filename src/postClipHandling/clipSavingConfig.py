
class ClipSavingConfig:

    def __init__(
            self, 
            externalPlatformConfig,
            savingPath,
            keepVideosAfterUpload,
        ):
        self.externalPlatformConfig = externalPlatformConfig
        self.savingPath = savingPath
        self.keepVideosAfterUpload = keepVideosAfterUpload

    def toDict(self):
        return {
            'externalPlatformConfig': self.externalPlatformConfig,
            'savingPath': str(self.savingPath),
            'keepVideosAfterUpload': bool(self.keepVideosAfterUpload),
        }