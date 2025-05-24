from recording.recordingConfig import RecordingConfig
from utils.inputOutputUtils import getAndValidateUserInput
from utils.fileUtils import FileUtils
from utils.constants import CLI

VALID_MODEL_TYPES = ["YOLO"]

def __retrieveRecordingConfig():
    print(f"{CLI.TITLE_LINE}Recording config setup{CLI.TITLE_LINE}")
    print("Detecting when a clip should be started or stopped must be predicated on some sort of image detection ML model.")
    print("As of right now, only YOLO (You Only Look Once) models are supported. Furthermore, you will not to train your own model. Fortunuately, this is not incredibly difficult.")
    print("Please see the README.md/documentation for more information on YOLO and guides for how to train a model.")

    modelType = VALID_MODEL_TYPES[0] # When different models are allowed, we will collect user input for what model they are using
    
    pathToModel = getAndValidateUserInput(
        inputText="Please enter the absolute path to your model: ",
        errorText="Input must be a valid file.",
        conditional=lambda path: FileUtils.isValidFile(path),
    )
    
    startRecordingOnDetection = getAndValidateUserInput(
        inputText="By default, recording will start on model detection and stop recording when the model does not detect its target. Type 'no' if you'd like to reverse this: ",
        errorText="",
        conditional=lambda _: 1==1,
    )
    startRecordingOnDetection = startRecordingOnDetection.lower() != "no"
    
    verboseMode = getAndValidateUserInput(
        inputText="Would you like for the terminal to display when your model makes a detection? (y|n) ",
        errorText="",
        conditional=lambda _: 1==1,
    )
    verboseMode = verboseMode.lower() == "y"

    toggleThreshold = getAndValidateUserInput(
        inputText="There is a 1 second wait between taking a screenshot and checking the model for detection. How many detections in a row to toggle recording? (Recommended 5) ",
        errorText="Please enter a positive integer.",
        conditional=lambda s: s.strip().isdigit() and int(s) > 0
    )
    toggleThreshold = int(toggleThreshold)

    indefiniteClips = getAndValidateUserInput(
        inputText="By default, clips will be taken so long as the targeted content is alive. Type 'no' if you'd like a specific number of clips to be made. ",
        errorText="",
        conditional=lambda _: 1==1,
    )
    indefiniteClips = indefiniteClips.lower() != "no"

    numberOfClips = -1
    if not indefiniteClips:
        numberOfClips = getAndValidateUserInput(
            inputText="Enter the number of clips you'd like to create for a given run of this workflow: ",
            errorText="Please enter a positive integer.",
            conditional=lambda s: s.strip().isdigit() and int(s) > 0
        )
        numberOfClips = int(numberOfClips)
    
    print("The following is for configuring a minimum clip time for the clip to be processed.")
    print("If the clip length is less than the the minimum clip time, the clip will be discarded and not uploaded to an external platform (if applicable).")
    minimumClipLength = getAndValidateUserInput(
        inputText="Enter a minimum clip time in seconds ('0' for none): ",
        errorText="Input must be an integer greater than or equal to 0.",
        conditional=lambda s: s.strip().isdigit() and int(s) >= 0,
    )
    minimumClipLength = int(minimumClipLength)

    print("The following is for configuring a maximum clip time.")
    print("Moreover, if a clip's recording time hits the maximum clip time, then the clip will be saved and processed.")
    print("Example input - '600' - note that 10 minutes = 600 seconds")
    maximumClipLength = getAndValidateUserInput(
        inputText="Enter a maximum clip length in seconds (enter '-1' if you'd like clips to be recording until the model stops them): ",
        errorText="Input must be a non-number or an integer greater than 0.",
        conditional=lambda s: (s.strip().isdigit() and int(s) > 0) or (s.strip().isdigit() and int(s) == -1),
    )
    maximumClipLength = int(maximumClipLength)

    # TODO advanced config for allowing the user to send specific stdin to selenium script when recording starts and stops
    # Make sure that the toggle threshold is lower than the detected/undetected action threshold
    return RecordingConfig(
        modelType,
        pathToModel,
        startRecordingOnDetection,
        verboseMode,
        toggleThreshold,
        indefiniteClips,
        numberOfClips,
        minimumClipLength,
        maximumClipLength,
    )

# Public functions

def buildRecordingConfig():
    return __retrieveRecordingConfig()
