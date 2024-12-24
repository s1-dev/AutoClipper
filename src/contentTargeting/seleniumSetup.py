# Discuss need for chrome driver
# Have preset scripts for youtube videos, twtich vods, etc. 
# Allow for custom scripts to be passed in
# Potentially add some sort of programmatic way to build a selenium script
# For instance, user wants to go to a site and click a button via ID

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"
options = ['YouTube', 'Twitch', 'Custom script']

def __retrieveSelniumScriptChoice():
    __printSeleniumSetupOptions()
    option = input("Option: ")

    __handleOption(option)

def __printSeleniumSetupOptions():
    print(f"{TITLE_LINE}Selenium Setup Options{TITLE_LINE}")
    print("Please select which type script you'd like to use")
    print("Note: For the preset scripts, such as youtube, will simply take in a URL and play the video. See example usage")

    for idx, option in options:
        print(f"{idx}: {option}")

def __handleOption(option):
    if option == "1":
        print("TODO - youtube")
    elif option == "2":
        print("TODO - twitch")
    elif option == "3":
        print("TODO - custom script")
    else:
        print("Unknown option...")

# Public functions 

def launchSeleniumSetupWarning():
    print("TODO")

def getSeleniumScript():
    return __retrieveSelniumScriptChoice()
