import obsws_python as obs
from obsClient import ObsClient

TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

obsServerConfig = {
    'host': '',
    'port': '',
    'password': '',
}

def printConfig():
    print("OBS Server Config")
    print(obsServerConfig)

def configureObsServerConfig():
    print(f"{TITLE_LINE}OBS Web Server Config{TITLE_LINE}")

    obsServerConfig["host"] = input("Hostname or IP: ")
    obsServerConfig["port"] = input("Port number: ")
    obsServerConfig["password"] = input("Password (nothing required if authentication is off): ")

    printConfig()

def connectToObs():
    try:
        client = obs.ReqClient(
            host = obsServerConfig["host"],  
            port = obsServerConfig["port"],         
            password = obsServerConfig["password"],
        )

        client.get_version() # Verify connection
        print("Connected to OBS successfully!")

        ObsClient(client)

    except Exception as e:
        print(f"Failed to connect to OBS: \n{e}")

def obsSetupDialog():
    print("TODO")

def printOptions():
    print(f"{TITLE_LINE}Options{TITLE_LINE}")
    print("1. Configure connection to OBS server")
    print("2. Connect to OBS")
    print("3. Print OBS web server config")

def handleOption(selectedOption):
    if selectedOption == "1":
        configureObsServerConfig()
    elif selectedOption == "2":
        connectToObs()
    elif selectedOption == "3":
        printConfig()
    else:
        print("Unknown option...")

def start():
    while True:
        printOptions()
        selectedOption = input("Option: ")
        handleOption(selectedOption)

def main():
    start()


if __name__ == "__main__":
    main()