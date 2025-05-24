import asyncio
import whisper

from utils.fileUtils import FileUtils

def _transcribeAudio(pathToVideo: str) -> str:
    # Figure out if we need error handling
    whisperModel = whisper.load_model("base") # Allow for user to configure which model to use
    result = whisperModel.transcribe(pathToVideo)
    return result["text"]

# Public functions

async def genTranscript(pathToVideo: str) -> str:
    if not FileUtils.isValidFile(pathToVideo):
        return None

    return await asyncio.to_thread(_transcribeAudio, pathToVideo)
