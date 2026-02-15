"""
Speech-to-Text Service using Google Cloud Speech-to-Text API
Handles audio transcription for voice input feature
"""

import os
from google.cloud import speech
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self, credentials_path: str = None):
        """
        Initialize the Speech Service with Google Cloud credentials
        
        Args:
            credentials_path: Path to Google Cloud service account JSON file
        """
        self.credentials_path = credentials_path
        
        # Set up client with service account credentials
        if credentials_path and os.path.isfile(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Initialize the Speech client (v1)
        try:
            self.client = speech.SpeechClient()
        except Exception as e:
            logger.error(f"Failed to initialize Speech client: {e}")
            self.client = None

    def transcribe_audio(
        self,
        audio_content: bytes,
        language_code: str = "auto",
        audio_encoding: str = "WEBM_OPUS"
    ) -> dict:
        """
        Transcribe audio content to text using Google Cloud Speech-to-Text API
        
        Args:
            audio_content: Audio file content as bytes
            language_code: Language code (e.g., 'en-US', 'es-ES', 'hi-IN') or 'auto' for auto-detection
            audio_encoding: Audio encoding format (WEBM_OPUS, LINEAR16, MP3, etc.)
        
        Returns:
            dict with 'success', 'text', 'language', and 'error' keys
        """
        if not self.client:
            return {
                "success": False,
                "text": "",
                "language": "",
                "error": "Speech client not initialized. Please check credentials configuration."
            }

        try:
            # Prepare the audio
            audio = speech.RecognitionAudio(content=audio_content)

            # Map encoding string to Speech API encoding enum
            encoding_map = {
                "WEBM_OPUS": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "LINEAR16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                "MP3": speech.RecognitionConfig.AudioEncoding.MP3,
                "OGG_OPUS": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            }
            
            encoding_enum = encoding_map.get(audio_encoding, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)

            # Configure recognition settings
            config = speech.RecognitionConfig(
                encoding=encoding_enum,
                language_code=language_code if language_code != "auto" else "en-US",
                enable_automatic_punctuation=True,
            )
            
            # If auto-detection is requested, enable alternative language codes
            if language_code == "auto":
                config.alternative_language_codes = [
                    "es-ES", "fr-FR", "de-DE", "hi-IN", "zh-CN", "ja-JP", "ko-KR",
                    "pt-BR", "ru-RU", "ar-SA", "it-IT", "nl-NL", "pl-PL", "tr-TR"
                ]

            # Perform the transcription
            logger.info(f"Transcribing audio ({len(audio_content)} bytes) with language: {language_code}")
            response = self.client.recognize(config=config, audio=audio)

            # Extract the transcription
            if not response.results:
                return {
                    "success": False,
                    "text": "",
                    "language": language_code,
                    "error": "No speech detected in the audio. Please try again."
                }

            # Get the best transcription
            transcript = ""
            detected_language = language_code
            
            for result in response.results:
                if result.alternatives:
                    transcript += result.alternatives[0].transcript + " "
                    # Get detected language from first result if available
                    if hasattr(result, 'language_code') and result.language_code:
                        detected_language = result.language_code

            transcript = transcript.strip()

            logger.info(f"Transcription successful: {transcript[:50]}...")
            
            return {
                "success": True,
                "text": transcript,
                "language": detected_language,
                "error": None
            }

        except Exception as e:
            logger.error(f"Transcription error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "text": "",
                "language": language_code,
                "error": f"Transcription failed: {str(e)}"
            }


# Singleton instance
_speech_service: Optional[SpeechService] = None


def get_speech_service(credentials_path: str) -> SpeechService:
    """Get or create the speech service singleton"""
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService(credentials_path)
    return _speech_service
