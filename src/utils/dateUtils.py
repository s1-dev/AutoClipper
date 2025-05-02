from datetime import datetime, timezone
import time

def convertUtcToEpoch(timeStampString) -> int:
    dt = datetime.strptime(timeStampString, "%Y-%m-%dT%H:%M:%SZ")
    epochTime = dt.replace(tzinfo=timezone.utc).timestamp()
    return int(epochTime)

def getCurrentEpoch() -> int:
    return int(time.time())

def getCurrentDateUserFacing() -> str:
    return datetime.now().strftime("%m/%d/%Y")