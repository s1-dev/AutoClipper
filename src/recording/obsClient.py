import obsws_python as obs

class ObsClient:
    def __init__(
            self,
            host,
            port, 
            password,
        ):

        self.serverAddress = host
        self.serverPort = port
        self.serverPassword = password

        self.__client = obs.ReqClient(
            host = self.serverAddress,  
            port = self.serverPort,         
            password = self.serverPassword,
        )

        self.__client.get_version() # Verify connection

    def connectionInfoToDict(self):
        return {
                'serverAddress': self.serverAddress,
                'serverPort': self.serverPort,
                'serverPassword': self.serverPassword,
            }

    def getSceneList(self):
        return self.__client.get_scene_list().scenes
    
    def setScene(self, sceneName):
        self.__client.set_current_program_scene(sceneName)

    def getSourceList(self, sceneName):
        return self.__client.get_scene_item_list(sceneName).scene_items

    def setSource(
            self, 
            sceneName, 
            sceneItemId, 
        ):
        self.__client.set_scene_item_enabled(
            scene_name = sceneName,
            item_id = sceneItemId,
            enabled = True,
        )
        