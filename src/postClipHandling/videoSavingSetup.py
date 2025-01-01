from postClipHandling.clipSavingConfig import ClipSavingConfig

def __retrieveSavingConfig():
    # TODO Sanitize user input and implement redos 
    print("Each clip will be saved with an appended random 6 character string and an integer for the number of clips that has been saved in this session.")
    print("For instance, the first clip will be saved as index 0, second as index 1, and so on.")
    fileName = input("Enter base name for clips: (Ex - clip_name) ")
    savingPath = input("Enter path to save video: ")
    # TODO check if saving path is valid directory
    savingPath = savingPath + fileName

    return ClipSavingConfig(
        savingPath
    )


# Public functions

def buildClipSavingConfig():
    return __retrieveSavingConfig()