from datetime import datetime, timezone
import time

def convertUtcToEpoch(timeStampString) -> int:
    dt = datetime.strptime(timeStampString, "%Y-%m-%dT%H:%M:%SZ")
    epochTime = dt.replace(tzinfo=timezone.utc).timestamp()
    return int(epochTime)

def getCurrentEpoch() -> float:
    return time.time()

def getCurrentDateUserFacing() -> str:
    return datetime.now().strftime("%m/%d/%Y")

def getStringFormatTime(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(format)