from recording.conventionalRecordingConfig import CoventionalRecordingConfig

# - number of clips
# - number of clips until upload
# - set interval of clips
# - set pause time between clips

def __retrieveRecordingConfig():
    # TODO Sanitize user input and implement redos 
    clipTime = input("Enter the time of each clip in minutes: ")
    inBetweenInterval = input("Enter the time that should be taken between each clip in seconds: ")
    indefiniteClips = input("Would you like to make clips until the targeted content finishes? (y/n) ")
    indefiniteClips = indefiniteClips.lower() == "y"
    numberOfClips = None
    if not indefiniteClips:
        numberOfClips = input("Enter the amount of clips you would like to attempt to create: ")

    return CoventionalRecordingConfig(
        clipTime, 
        inBetweenInterval,
        indefiniteClips,
        numberOfClips,
    )

# Public functions

def buildConventionalRecordingConfig():
    return __retrieveRecordingConfig()
