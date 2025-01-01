
class SeleniumCommand:

    def __init__(
            self,
            pathToScript = "",
            args = [],
        ):
        self.command = self.buildBaseCommand(pathToScript)
        self.args = self.validateArgs(args)

    def buildBaseCommand(self, pathToScript):
        pythonVersion = self.__getPythonVersion()
        command = f"{pythonVersion} {pathToScript}"
        return command
    
    def __getPythonVersion(self):
        # TODO
        return "python"
    
    def validateArgs(self, args):
        # TODO
        return args
    
    def toDict(self):
        return {
            'baseCommand': self.command,
            'args': self.args,
        }
    