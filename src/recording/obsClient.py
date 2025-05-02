import asyncio
import obsws_python as obs
from obsws_python.error import OBSSDKRequestError
import time


RECORDING_MAX_RETRIES = 3
RECORDING_RETRY_DELAY_SECONDS = 2

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
        itemId, 
    ):
        self.__client.set_scene_item_enabled(
            scene_name = sceneName,
            item_id = itemId,
            enabled = True,
        )

    def setRecordDirectory(self, savingPath):
        self.__client.set_record_directory(savingPath)

    def startRecording(self):
        self.__client.start_record()

    async def startRecordingAsync(self) -> bool:
        #ready = await self._waitForRecordingReady()
        #if not ready:
        #    print("OBS never became ready to start recording.")
        #   return False
        for attempt in range(1, RECORDING_MAX_RETRIES + 1):
            try:
                self.__client.start_record()
                print("Recording started.")
                return True
            except OBSSDKRequestError as e:
                print(f"Attempt {attempt}: Failed to start recording - {e}")
                if attempt < RECORDING_MAX_RETRIES:
                    await asyncio.sleep(RECORDING_RETRY_DELAY_SECONDS)
                else:
                    print("Giving up on starting recording after multiple attempts.")
                    return False
                
    async def _waitForRecordingReady(self, max_wait_seconds=10) -> bool:
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            status = await self.getRecordStatus()
            if not status.output_active:
                return True
            await asyncio.sleep(0.5)
        print("Timeout waiting for OBS to become ready for recording.")
        return False

    def stopRecording(self):
        outputPath = self.__client.stop_record()
        return outputPath
    
    async def stopRecordingAsync(self):
        #ready = await self._waitForStopRecordingReady()
        #if not ready:
        #    print("OBS never became ready to stop recording.")
        #    return None
        for attempt in range(1, RECORDING_MAX_RETRIES + 1):
            try:
                outputPath = self.__client.stop_record().output_path
                print(f"Recording stopped. Saved to: {outputPath}")
                return outputPath
            except OBSSDKRequestError as e:
                print(f"Attempt {attempt}: Failed to stop recording - {e}")
                if attempt < RECORDING_MAX_RETRIES:
                    await asyncio.sleep(RECORDING_RETRY_DELAY_SECONDS)
                else:
                    print("Giving up on stopping recording after multiple attempts.")
                    return None
                
    async def _waitForStopRecordingReady(self, max_wait_seconds=10) -> bool:
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            status = await self.getRecordStatus()
            if status.output_active:
                return True
            await asyncio.sleep(0.5)
        print("Timeout waiting for OBS to become ready to stop recording.")
        return False
        
    def isRecording(self) -> bool: 
        status = self.__client.get_record_status()
        return status.output_active
    
    async def isRecordingAsync(self) -> bool: 
        status = await self.__client.get_record_status()
        return status.output_active
    
    def getRecordStatus(self): # Probably shelve for isRecording, unless I need something else in the query
        return self.__client.get_record_status()
        