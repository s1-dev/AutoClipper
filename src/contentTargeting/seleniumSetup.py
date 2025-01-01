from contentTargeting.seleniumCommand import SeleniumCommand

# Discuss need for chrome driver
# Have preset scripts for youtube videos, twtich vods, etc. 
# Allow for custom scripts to be passed in
# Potentially add some sort of programmatic way to build a selenium script
# For instance, user wants to go to a site and click a button via ID
TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"
options = ['YouTube', 'Twitch', 'Custom script']

YOUTUBE_SCRIPT_PATH = "scripts/launchYoutubeVideo.py"
TWITCH_SCRIPT_PATH = "scripts/launchTwitchVideo.py"

def __retrieveSelniumScriptChoice():
    __printSeleniumSetupOptions()
    option = input("Option: ")

    return __handleOption(option)

def __printSeleniumSetupOptions():
    print(f"{TITLE_LINE}Selenium Setup Options{TITLE_LINE}")
    print("Please select which type script you'd like to use")
    print("Note: For the preset scripts, such as youtube, will simply take in a URL and play the video. See example usage")

    for idx, option in enumerate(options):
        print(f"{idx+1}: {option}")

def __handleOption(option):
    # TODO refactor
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
    # TODO
    seleniumCommand = SeleniumCommand(
        pathToScript = pathToScript,
        args = [],
    )

    return seleniumCommand

def __getCustomScriptPath():
    customScriptPath = input("Input absolute path of custom selenium script: ")
    # TODO sanitize 
    return customScriptPath

# Public functions 

def launchSeleniumSetupWarning():
    print("TODO")

def getSeleniumCommand():
    return __retrieveSelniumScriptChoice()
