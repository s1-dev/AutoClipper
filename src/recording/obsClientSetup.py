from utils.inputOutputUtils import getAndValidateUserInput

def __pickScene(client):
    sceneList = client.getSceneList()
    __listScenes(sceneList)
    sceneName = getAndValidateUserInput(
        inputText="Input the name of the scene you'd like to set (case sensitive): ",
        errorText="Invalid scene name.",
        conditional=lambda userInput: userInput in sceneList,
    )

    try:
        # TODO just return config, but put check to ensure it's correct
        #client.setScene(sceneName)
        return sceneName
    except Exception as e:
        print(f"Exception: {e}")
        return None

def __listScenes(sceneList):
    print("Available scenes: ")
    for index, scene in enumerate(sceneList):
        print(f"{index+1}: {scene['sceneName']}")

def __pickSource(client, sceneName):
    sourceList = client.getSourceList(sceneName)
    __listSources(sourceList)

    sourceName = getAndValidateUserInput(
        inputText="Input the name of the source you'd like to set (case sensitive): ",
        errorText="Invalid source name.",
        conditional=lambda userInput: userInput in sourceList,
    )

    sceneItemId = __getSceneItemId(sourceList, sourceName)

    if sceneItemId == None:
        print("TODO")
        exit()

    try:
        # TODO just return config, but put check to ensure it's correct
        #client.setSource(sceneName, sceneItemId)
        return (sourceName, sceneItemId)
    except Exception as e:
        print(f"Exception: {e}") 
        return None

def __listSources(sourceList):
    print("Available sources: ")
    for index, source in enumerate(sourceList):
        print(f"{index+1}: {source['sourceName']}")

def __getSceneItemId(sourceList, sourceName):
    for item in sourceList:
        if [item['sourceName'] == sourceName]:
            return item['sceneItemId']
    return None

# Public functions

def setObsScene(client):
    return __pickScene(client)

def setObsSource(client, sceneName):
    return __pickSource(client, sceneName)
