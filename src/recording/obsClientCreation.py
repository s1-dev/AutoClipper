from recording.obsClient import ObsClient
from utils.constants import CLI

obsServerConfig = {
    'host': '',
    'port': '',
    'password': '',
}

def configureObsServerConfig():
    __getConfigFromUser()
    errorsEncountered = 0
    while True:
        if errorsEncountered > 0:
            if errorsEncountered == 1:
                print("You have failed to connect")
            else:
                print(f"You have failed to connect {errorsEncountered} times")
            response = input("Would you like to attempt again? (y|Y) ")
            if response.lower() != "y":
                return None
        
        try:
            obsClient = __connectToObs()
            return obsClient
        except Exception as e:
            print(f"Failed to connect to OBS: \n{e}")
            errorsEncountered += 1

def __getConfigFromUser():
    print(f"{CLI.TITLE_LINE}OBS Web Server Config{CLI.TITLE_LINE}")

    obsServerConfig["host"] = input("Hostname or IP: ")
    obsServerConfig["port"] = input("Port number: ")
    obsServerConfig["password"] = input("Password (nothing required if authentication is off): ")

    __printConfig()

def __printConfig():
    print("OBS Server Config")
    print(obsServerConfig)

def __connectToObs():
    client = ObsClient(
        host = obsServerConfig["host"],  
        port = obsServerConfig["port"],         
        password = obsServerConfig["password"],
    )
    print("Connected to OBS successfully!")

    return client

# Public functions

#def launchObsSetupWarning():
#    print("TODO")

def retrieveObsClient():
    return configureObsServerConfig()
