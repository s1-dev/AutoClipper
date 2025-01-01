
class ClipSavingConfig:

    def __init__(
            self, 
            savingPath,
        ):
        self.savingPath = savingPath

    def toDict(self):
        return {
            'savingPath': str(self.savingPath),
        }