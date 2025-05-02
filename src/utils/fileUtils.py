import json
import shutil
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

    @staticmethod
    def isValidFile(pathToFile: str) -> bool:
        return os.path.isfile(pathToFile)

    @staticmethod
    def isValidJsonFile(pathToJson: str) -> bool:
        if not os.path.isfile(pathToJson):
            return False
        try:
            with open(pathToJson, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False
        
    @staticmethod 
    def isValidDir(pathToDir: str) -> bool:
        return os.path.isdir(pathToDir)

    @staticmethod
    def deleteFile(pathToFile: str) -> bool:
        if os.path.exists(pathToFile):
            os.remove(pathToFile)
            return True
        else:
            return False
        
    @staticmethod
    def moveFileToDir(srcPath: str, destPath: str) -> bool:
        destPath = f"{destPath}/{os.path.basename(srcPath)}" # Need to check if user specifies '\' instead of '/'
        try:
            shutil.move(srcPath, destPath)
            return True
        except FileNotFoundError:
            print(f"Error: File not found at {srcPath}")
        except FileExistsError:
            print(f"Error: File already exists at {destPath}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            return False
