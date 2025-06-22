import asyncio
import whisper

from utils.fileUtils import FileUtils

def _transcribeAudio(pathToVideo: str) -> str:
    try:
        whisperModel = whisper.load_model("base") # Allow for user to configure which model to use
        result = whisperModel.transcribe(pathToVideo)
        return result["text"]
    except Exception as e:
        print(f"An error occurred while trying to generate a clip transcript: {e}")
        return None

# Public functions

async def genTranscript(pathToVideo: str) -> str:
    if not FileUtils.isValidFile(pathToVideo):
        return None

    return await asyncio.to_thread(_transcribeAudio, pathToVideo)
