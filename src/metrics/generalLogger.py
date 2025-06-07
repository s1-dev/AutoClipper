import asyncio
from utils.dateUtils import getStringFormatTime
from utils.fileUtils import FileUtils
from utils.constants import Metrics

LOGS_PATH_LOCATION = "./logs"

class GeneralLogger:
    def __init__(
        self, 
        configName: str, 
        outputLogs: bool = True,
        flushBatchSize: int = 3,
    ):
        FileUtils.createDir(LOGS_PATH_LOCATION, exist_ok=True)
        timestamp = getStringFormatTime("%Y-%m-%d_%H-%M-%S")
        self.loggingDir = FileUtils.joinFileToPath(LOGS_PATH_LOCATION, f"logs_{configName}_{timestamp}")
        FileUtils.createDir(self.loggingDir)

        self.logFile = FileUtils.joinFileToPath(self.loggingDir, Metrics.LOG_FILE_NAME)
        with open(self.logFile, "w") as f:
            f.write(f"[{timestamp}] Workflow logging started\n")

        self.outputLogs = outputLogs
        self.flushBatchSize = flushBatchSize
        self.logs = []
        self._lock = asyncio.Lock()  # Async-safe lock for concurrent access

    def logSync(self, messageToLog: str):
        timestamp = getStringFormatTime()
        fullLog = f"[{timestamp}] {messageToLog}"
        if self.outputLogs:
            print(fullLog)
        with open(self.logFile, "a") as f:
            f.write(fullLog + "\n")

    async def log(self, messageToLog: str):
        async with self._lock:
            timestamp = getStringFormatTime()
            fullLog = f"[{timestamp}] {messageToLog}"
            if self.outputLogs:
                print(fullLog)
            self.logs.append(fullLog)
            if len(self.logs) >= self.flushBatchSize:
                await self._flush_unlocked()

    async def flush(self):
        async with self._lock:
            await self._flush_unlocked()

    async def _flush_unlocked(self):
        if not self.logs:
            return
        with open(self.logFile, "a") as f:
            f.write("\n".join(self.logs) + "\n")
        self.logs = []


    def getLoggingDir(self) -> str:
        return self.loggingDir
