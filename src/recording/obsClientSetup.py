TITLE_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~"

def __pickScene(client):
    sceneList = client.getSceneList()
    __listScenes(sceneList)
    sceneName = input("Scene to set: ")

    try:
        # TODO just return config, but put check to ensure it's correct
        #client.setScene(sceneName)
        return sceneName
    except Exception as e:
        print(f"Exception: {e}")
        return None

def __listScenes(sceneList):
    print(f"{TITLE_LINE}Available scenes{TITLE_LINE}")
    for scene in sceneList:
        print(f"scene name: {scene['sceneName']}")

def __pickSource(client, sceneName):
    sourceList = client.getSourceList(sceneName)
    __listSources(sourceList)

    sourceName = input("Source name to set: ")

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
    print(f"{TITLE_LINE}Available sources{TITLE_LINE}")
    for source in sourceList:
        print(f"source name: {source['sourceName']}")

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
