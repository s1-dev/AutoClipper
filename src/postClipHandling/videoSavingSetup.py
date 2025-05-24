from postClipHandling.clipSavingConfig import ClipSavingConfig
from utils.fileUtils import FileUtils
from utils.inputOutputUtils import getAndValidateUserInput
from utils.constants import AI, CLI

YOUTUBE = "YOUTUBE"
UPLOAD_PLATFORMS = [YOUTUBE]
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
PLATFORM_KEY = "platform"

MAX_YT_TITLE_LEN = 100
MAX_YT_DESC_LEN = 5000
MAX_YT_TAG_LEN = 500

def __retrieveSavingConfig():
    print(f"{CLI.TITLE_LINE}Post clip handling conifg{CLI.TITLE_LINE}")
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
    
    smartHandlingConfig = ""
    print("Would you like to use AI to generate youtube video details?")
    print("This would be for a youtube title, description, and tags (keywords) list.")
    print("It is important to note that the details are generated based on a transcript of the clip.")
    print("If there is no dialogue in the media you are clipping, I would advise skipping this step and using the default YT details above.")
    
    decision = input("Type (y) if you'd like to setup 'smart video handling': ")
    if decision.lower() == "y":
        smartHandlingConfig = _setupYtSmartHandlingConfig()
    youtubeConfig["smartHandlingConfig"] = smartHandlingConfig

    return youtubeConfig

def _setupYtSmartHandlingConfig() -> dict:
    print("Currently, google's gemini is the only supported LLM.")
    print("Please configure your google account to use gemini and retrieve your gemini API key.")

    smartHandlingConfig = {}

    apiKey = getAndValidateUserInput( # See if it's possible to do some validation here
        inputText="Please enter your gemini API key: ",
        errorText="",
        conditional=lambda _: 1==1,
    )
    smartHandlingConfig["apiKey"] = apiKey

    print("Below is the base prompt that will be feed to the chatbot: ")
    print(f"{CLI.TITLE_LINE}\n{AI.BASE_YT_DETAIL_PROMPT}\n")

    print("Please provide more context to the bot about the media you are clipping.")
    print("This may include the genre of media, characters or hosts of the media, ask it to include certain 'hashtags', etc.")

    print("Would you like to see an example of custom requests to the bot?")
    decision = input("Enter (y) if so: ")
    if decision.lower() == "y":
        exampleCustomRequests = f"""
            EXAMPLE: 

            The transcript was generated from a segment from the FS1 sports talk show, First Things First. Please make
            the tags list a mix of FTF related words and tags related to the contents of the transcript. Make sure to include
            First Things First, Nick Wright, Chris Broussard, and or Kevin Wildes in the title and description.
            Please ensure the title is no longer than 100 chars, the description is no longer than 5000 chars, and the tags list
            is no longer than 500 chars.

            Would you please also include these hashtags in the description? #FirstThingsFirst #FS1 #NickWright #ChrisBroussard #KevinWildes #NBA #NFL #SportsTalk #Debate
        """
        print(f"{CLI.TITLE_LINE}\n{exampleCustomRequests}\n")
    
    userRequests = getAndValidateUserInput(
        inputText="Please enter your custom requests (hit enter if you'd like to skip): ",
        errorText="",
        conditional=lambda _: 1==1,
    )
    smartHandlingConfig["userRequests"] = userRequests
 
    return smartHandlingConfig

# Public functions

def buildClipSavingConfig():
    return __retrieveSavingConfig()
