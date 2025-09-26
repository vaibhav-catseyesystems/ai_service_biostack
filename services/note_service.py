import tempfile
import speech_recognition as sr
from pydub import AudioSegment

def convert_audio_to_text(file_storage):
    """
    Converts uploaded audio file (WebM) to text by first converting it to WAV.
    """
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
        file_storage.save(temp_webm.name)
        webm_path = temp_webm.name

    audio_segment = AudioSegment.from_file(webm_path, format="webm")
    wav_path = webm_path.replace(".webm", ".wav")
    audio_segment.export(wav_path, format="wav")
    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        raise ValueError("Could not understand audio")
    except sr.RequestError as e:
        raise Exception(f"Speech recognition service error: {e}")
    finally:
        import os
        os.remove(webm_path)
        os.remove(wav_path)