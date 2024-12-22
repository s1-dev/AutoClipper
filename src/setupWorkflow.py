
# Maybe make workflow as an object and hold each subworkflow config as properties

# Transition functions?

def start():
    print("TODO")

def getObsClient():
    print("TODO")
    # Run OBS setup
    # Attempt connect to server
    # Passs to client setup

def setupObsClient():
    print("TODO")
    # Ask user which scene to use
    # ASk user which source to use 
    # Add scene creation/cutomization? Issues with picking certain settings so probably implement later
    # Pass to client to 

def getTargetContent():
    print("TODO")
    # Get target URL to launch and watch
    # Allow user to implement actions to take on the website
    # Ex - CLick this button, maxmize screen, etc.
    # Have a subworkflow to do a test run for the user 
    # Pass content target to recording setup

def recordingSetup():
    print("TODO")
    # Ask user how we should create clips 
    # Timed? Certain intervals 
    # Add AI to examine video and cut at certain points. Probably implement with manual time boxxing for now 
    # Pass to youtube setup

def savingSetup():
    print("TODO")
    # Ask user if they'd like to automatically upload clips to youtube 
    # if not, just ensure the video is saved locally to a certain PATH
    # else, get youtube auth token, probably? 
    
def setupConfirmation():
    print("TODO")
    # Show overview of user setup? (Maybe optional button)
    # Ask what the user wants to do with setup:
    #   - Just save, run a test (have sample 30 second video), or start automation workflow
    # Return to main menu? 
    