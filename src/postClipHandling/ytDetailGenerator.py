import asyncio
from google.generativeai import GenerativeModel, configure
import json

from utils.constants import AI

# We need to implement retries
def _queryGeminiForDetails(transcript: str, userRequests: str, model: GenerativeModel) -> dict:
    prompt = f"""
        {AI.BASE_YT_DETAIL_PROMPT}

        {userRequests}

        Transcript:
        {transcript}
    """

    response = model.generate_content([
        {"role": "user", "parts": [prompt]}
    ])
    try:
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json") and cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[7:-3].strip()
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {response.text}")
        print(f"Decoding error details: {e}")
        return None
    except Exception as e:
        print(f"An exception occurred while trying to generate smart details: {e}")
        return None

async def generateYtDetails(transcript: str, smartHandlingConfig: dict) -> dict:
    # Configure the Gemini API
    configure(api_key=smartHandlingConfig["geminiApiKey"])
    model = GenerativeModel('gemini-1.5-flash')

    return await asyncio.to_thread(
        _queryGeminiForDetails,
        transcript,
        smartHandlingConfig["userRequests"],
        model
    )
 