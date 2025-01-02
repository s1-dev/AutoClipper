import json
import os

class FileUtils(object):

    @staticmethod
    def doesDirExist(pathToDir):
        return os.path.exists(pathToDir)
    
    @staticmethod 
    def createDir(dirToCreate):
        os.makedirs(dirToCreate)

    @staticmethod
    def dictToJson(
        dictData, 
        outputPath, 
        indent = 4,
    ):            
        with open(outputPath, "w") as jsonFile:
            json.dump(dictData, jsonFile, indent=indent)
