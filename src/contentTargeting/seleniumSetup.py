from contentTargeting.seleniumCommand import SeleniumCommand
from utils.inputOutputUtils import getAndValidateUserInput
from utils.fileUtils import FileUtils
from utils.constants import CLI

# Discuss need for chrome driver
# Have preset scripts for youtube videos, twtich vods, etc. 
# Allow for custom scripts to be passed in
# Potentially add some sort of programmatic way to build a selenium script
# For instance, user wants to go to a site and click a button via ID
options = ['YouTube', 'Twitch', 'Custom script']
VALID_OPTIONS = ("1", "2", "3")

YOUTUBE_SCRIPT_PATH = "seleniumScripts/launchYoutubeVideo.py"
TWITCH_SCRIPT_PATH = "seleniumScripts/launchTwitchVideo.py"

def __retrieveSelniumScriptChoice():
    __printSeleniumSetupOptions()
    option = getAndValidateUserInput(
        inputText="Input an option: ",
        errorText=f"Must be one of the valid options: {VALID_OPTIONS}",
        conditional=lambda userOption: userOption in VALID_OPTIONS,
    )

    return __handleOption(option)

def __printSeleniumSetupOptions():
    print(f"{CLI.TITLE_LINE}Selenium Setup Options{CLI.TITLE_LINE}")
    print("Please select which type script you'd like to use")
    print("Note: For the preset scripts, such as youtube, will simply take in a URL and play the video. See example usage")

    for idx, option in enumerate(options):
        print(f"{idx+1}: {option}")

def __handleOption(option):
    if option == "1":
        return __buildSeleniumCommand(YOUTUBE_SCRIPT_PATH)
    elif option == "2":
        return __buildSeleniumCommand(TWITCH_SCRIPT_PATH)
    elif option == "3":
        pathToCustomScript = __getCustomScriptPath()
        return __buildSeleniumCommand(pathToCustomScript)
    else:
        print("Unknown option...")
        return None

def __buildSeleniumCommand(pathToScript):
    seleniumCommand = SeleniumCommand(
        pathToScript = pathToScript,
        args = [],
    )

    return seleniumCommand

def __getCustomScriptPath():
    customScriptPath = getAndValidateUserInput(
        inputText="Input absolute path of custom selenium script: ",
        errorText="Please input a valid file.",
        conditional=lambda file: FileUtils.isValidFile(file),
    )
    return customScriptPath

# Public functions 

def launchSeleniumSetupWarning():
    print("TODO - Show user warning about selenium usage")

def getSeleniumCommand():
    return __retrieveSelniumScriptChoice()
