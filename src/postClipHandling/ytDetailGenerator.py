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

    try:
        response = model.generate_content([
            {"role": "user", "parts": [prompt]}
        ])
        print("naw this hit")
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
    configure(api_key=smartHandlingConfig["geminiApiKey"])
    model = GenerativeModel('gemini-1.5-flash')

    return await asyncio.to_thread(
        _queryGeminiForDetails,
        transcript,
        smartHandlingConfig["userRequests"],
        model
    )

# if __name__ == "__main__":

#     async def main():
#         dummy_transcript = "This is a sample transcript of a YouTube video. It discusses various interesting topics."
#         smart_config = {
#             "geminiApiKey": "AIzaSyBmCh6Rfcg_PbnssCwK1VXWjiZh1wk1YLc",  
#             "userRequests": "Extract the key takeaways and topics discussed in the video in JSON format."
#         }

#         if not smart_config["geminiApiKey"]:
#             print("Missing Gemini API key. Please set GEMINI_API_KEY environment variable.")
#             return

#         print("Starting Gemini detail generation test...\n")
#         result = await generateYtDetails(dummy_transcript, smart_config)
#         print("\nGenerated details:\n", json.dumps(result, indent=2) if result else "No result returned.")

#     asyncio.run(main())

