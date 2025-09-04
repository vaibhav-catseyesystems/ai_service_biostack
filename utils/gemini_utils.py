from google import genai
import os
import logging

logger = logging.getLogger(__name__)

API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]
current_key_index = 0

def get_gemini_model():
    """Returns the configured Gemini model instance."""
    try:
        global current_key_index
        if not API_KEYS or all(key is None for key in API_KEYS):
            logger.error("No Gemini API keys are set. Please check your environment variables.")
            raise ValueError("No Gemini API keys are set. Please check your environment variables.")
        api_key = API_KEYS[current_key_index]
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        for _ in range(len(API_KEYS)):
            if api_key:
                try:
                    logger.info(f"api_key: {api_key}")
                    return genai.Client(api_key=api_key)
                except Exception as e:
                    logger.warning(f"Warning: Key {api_key} failed. Retrying with the next one.")
                    api_key = API_KEYS[current_key_index]
                    current_key_index = (current_key_index + 1) % len(API_KEYS)
            else:
                logger.info(f"Skipping empty API key at index {current_key_index - 1}.")
                api_key = API_KEYS[current_key_index]
                current_key_index = (current_key_index + 1) % len(API_KEYS)
        logger.error("All Gemini API keys failed or were not configured.")
        raise RuntimeError("All Gemini API keys failed or were not configured.")
    except Exception as e:
        raise RuntimeError(f"Failed to configure Gemini model: {e}")

def generate_content_with_file(client, prompt_string, file_bytes, mime_type):
    """
    Generates content from a prompt and a file using the Gemini model.
    """
    try:
        response=client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {"role": "user", "parts": [{"text": prompt_string}, {"inline_data": {"mime_type": mime_type, "data": file_bytes}}]}
            ]
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise RuntimeError(f"Gemini API call failed: {e}")