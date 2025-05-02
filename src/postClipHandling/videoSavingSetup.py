from postClipHandling.clipSavingConfig import ClipSavingConfig
from utils.fileUtils import FileUtils
from utils.inputOutputUtils import getAndValidateUserInput

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

YOUTUBE = "YOUTUBE"
UPLOAD_PLATFORMS = [YOUTUBE]
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
PLATFORM_KEY = "platform"

MAX_YT_TITLE_LEN = 100
MAX_YT_DESC_LEN = 5000
MAX_YT_TAG_LEN = 500

def __retrieveSavingConfig():
    print(f"{TITLE_LINE}Post clip handling conifg{TITLE_LINE}")
    decision = input("Would you like to upload your videos to an external platform? (y/n): ")
    externalPlatformConfig = ""
    savingPath = ""
    keepVideosAfterUpload = True
    if decision.lower() == "y":
        externalPlatformConfig = _buildExternalPlatformConfig()
        decision = input("Would you like to save your videos after uploading? (y/n): ")
        if not decision.lower() == "y":
            keepVideosAfterUpload = False

    if keepVideosAfterUpload:
        savingPath = _retrieveSavingPath()

    return ClipSavingConfig(
        externalPlatformConfig = externalPlatformConfig,
        savingPath = savingPath,
        keepVideosAfterUpload = keepVideosAfterUpload,
    )

def _buildExternalPlatformConfig() -> dict:
    print("From the below list, input the name of the platform you'd like to upload to: ")
    for index, platform in enumerate(UPLOAD_PLATFORMS):
        print(f"{index+1}. {platform}")
    validInput = False
    platform = ""

    while not validInput:
        selectedPlatform = input("Platform: ")
        selectedPlatform = selectedPlatform.upper()
        if selectedPlatform in UPLOAD_PLATFORMS:
            platform = selectedPlatform
            validInput = True
        else:
            print("Please input a valid platform from the above list.")
    
    if platform == YOUTUBE:
        return _buildYouTubeConfig()
    return None

def _retrieveSavingPath() -> str:
    print("Would you like to specify a directory to save all your videos in?")
    print("If you'd like to stick with the OBS output path, please input nothing and click enter.")
    savingDir = getAndValidateUserInput(
        inputText="Enter the absolute path of the director to save clips: ",
        errorText="Please enter a valid directory.",
        conditional=lambda path: FileUtils.isValidDir(path),
    )
    if savingDir == None:
        raise Exception("TODO - change to illegal state exception")

    return savingDir

def _buildYouTubeConfig():
    youtubeConfig = {}
    youtubeConfig[PLATFORM_KEY] = YOUTUBE

    oAuthConfig = getAndValidateUserInput(
        inputText="Input absolute path of your OAUTH Config json file: ",
        errorText="You did not input a valid json file.",
        conditional=lambda filePath: FileUtils.isValidJsonFile(filePath),
    )
    if oAuthConfig:
        youtubeConfig["pathToOAuthConfig"] = oAuthConfig  # TODO validate that this is a OAUTH config file
    else:
        raise Exception("TODO - change to illegal state exception")

    print("Please input the base clip title to use. Note, the final clip title will contain the clip title and date.")
    print("Title syntax: <BASE_CLIP_TITLE> <CLIP_COUNTER> | <DATE>")
    print("Example title: First things first segment 1 | 3/17/25")
    videoTitle = getAndValidateUserInput(
        inputText="Input the base clip title: ",
        errorText="Please input a title less than or equal to 200 characters.",
        conditional=lambda title: len(title) <= MAX_YT_TITLE_LEN,
    )
    if videoTitle:
        youtubeConfig["videoTitle"] = videoTitle
    else:
        raise Exception("TODO - change to illegal state exception")

    print("Input a base description for the video (this may be easier to manually input into the config json file).")
    videoDesc = getAndValidateUserInput(
        inputText="Input a base description: ",
        errorText="Please input a description less than or equal to 5000 characters.",
        conditional=lambda desc: len(desc) <= MAX_YT_DESC_LEN,
    )
    if videoDesc:
        youtubeConfig["videoDesc"] = videoDesc
    else:
        raise Exception("TODO - change to illegal state exception")
    
    print("Input a comma seperated list of tags/keywords.")
    print("Example list of tags: tcp,pwned,xmastree,coding,security")
    videoTags = getAndValidateUserInput(
        inputText="Input a tags/keywords list: ",
        errorText="Please input a tags list less than or equal to 500 characters.",
        conditional=lambda tags: len(tags) <= MAX_YT_TAG_LEN,
    )
    if videoTags:
        youtubeConfig["videoTags"] = videoTags
    else:
        raise Exception("TODO - change to illegal state exception")
    
    print("Youtube allows one to categorize your video with a category ID.")
    print("These IDs are numerical and each number represents a certain topic.")
    print("For instasnce, the category ID for sports is '17'.")
    print("Please research the possible category IDs and set the most applicable for your clips.")
    categoryId = getAndValidateUserInput(
        inputText="Enter a categoryId: ",
        errorText="Category must be a valid positive number.",
        conditional=lambda strNum: strNum.strip().isdigit() and int(strNum) > 0
    )
    if categoryId:
        youtubeConfig["categoryId"] = categoryId
    else:
        raise Exception("TODO - change to illegal state exception")
    
    print(f"Youtube allows videos to be uploaded with one of the following privacy statuses: {VALID_PRIVACY_STATUSES}")
    privacyStatus = getAndValidateUserInput(
        inputText="Enter a privacy status for the clips: ",
        errorText=f"Privacy status must be one of the following: {VALID_PRIVACY_STATUSES}",
        conditional=lambda privStatus: privStatus.lower() in VALID_PRIVACY_STATUSES,
    )
    if categoryId:
        youtubeConfig["privacyStatus"] = privacyStatus.lower()
    else:
        raise Exception("TODO - change to illegal state exception")
    
    return youtubeConfig

# Public functions

def buildClipSavingConfig():
    return __retrieveSavingConfig()
