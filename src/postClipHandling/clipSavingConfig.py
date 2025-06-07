from enum import Enum

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
    
class ExternalPlatform(Enum):
    NONE = "none"
    YOUTUBE = "youtube"

    @staticmethod
    def fromValue(value: str):
        try:
            return ExternalPlatform(value)
        except ValueError:
            return None
