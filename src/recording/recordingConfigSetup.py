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
        errorText="Input must be '-1' or an integer greater than 0.",
        conditional=lambda s: (s.strip() == "-1") or (s.strip().isdigit() and int(s) > 0),
    )
    maximumClipLength = int(maximumClipLength)

    recordingToggleActions = {}
    print("Depending on your targeted content script, you may want to send commands to the script after recording is toggled on or off.")
    print("For instance, you may want to refresh the site you are targeting after a commercial is hit or load a different video when recording stops.")
    print("This may be rather advanced and you'd have to make sure your script can listen for commands and handle them accordingly.")
    print("An example may be: I send the command 'REFRESH' when we stop recording.")
    decision = input("Would you like to setup post recording toggle actions? (y/Y) ")
    if decision.lower() == "y":
        recordingToggleActions = _setupRecordingToggleActions()

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
        recordingToggleActions,
    )

def _setupRecordingToggleActions() -> dict:
    recordingToggleActionConfigs = {}

    onStopRecordActionConfig = {}
    decision = input("Would you like to setup an action after recording stops? (y/Y) ")
    if decision.lower() == "y":
        onStopRecordActionConfig = _setupRecordingStoppedAction()
    recordingToggleActionConfigs["onStopRecordActionConfig"] = onStopRecordActionConfig

    onStartRecordActionConfig = {}
    decision = input("Would you like to setup an action after recording starts? (y/Y) ")
    if decision.lower() == "y":
        onStartRecordActionConfig = _setupRecordingStartedAction()
    recordingToggleActionConfigs["onStartRecordActionConfig"] = onStartRecordActionConfig

    return recordingToggleActionConfigs
    
 
def _setupRecordingStoppedAction() -> dict:
    onStopRecordActionConfig = {}

    action = getAndValidateUserInput(
        inputText="Please input the message you'd like to send to your targeted content script when recording stops: ",
        errorText="Message can not exceed 500 characters.",
        conditional=lambda s: len(s) <= 500, 
    )
    onStopRecordActionConfig["action"] = action

    actionDelayTime = getAndValidateUserInput(
        inputText="Input the time, in seconds, that you'd like to wait until sending the action. For example, an input of '5' will result in the action being sent 5 seconds after recording has stopped. ",
        errorText="Input must be a positive integer or '0' if you'd like no wait to send the action when recording stops.",
        conditional=lambda s: s.strip().isdigit() and int(s) >= 0,
    )
    onStopRecordActionConfig["actionDelayTime"] = int(actionDelayTime)

    return onStopRecordActionConfig

def _setupRecordingStartedAction() -> dict:
    onStartRecordActionConfig = {}

    action = getAndValidateUserInput(
        inputText="Please input the message you'd like to send to your targeted content script when recording starts: ",
        errorText="Message can not exceed 500 characters.",
        conditional=lambda s: len(s) <= 500, 
    )
    onStartRecordActionConfig["action"] = action

    actionDelayTime = getAndValidateUserInput(
        inputText="Input the time, in seconds, that you'd like to wait until sending the action. For example, an input of '5' will result in the action being sent 5 seconds after recording has started. ",
        errorText="Input must be a positive integer or '0' if you'd like no wait to send the action when recording starts.",
        conditional=lambda s: s.strip().isdigit() and int(s) >= 0,
    )
    onStartRecordActionConfig["actionDelayTime"] = int(actionDelayTime)

    return onStartRecordActionConfig

# Public functions

def buildRecordingConfig():
    return __retrieveRecordingConfig()
