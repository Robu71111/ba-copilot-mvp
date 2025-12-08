"""
Speech-to-Text Module
=====================
Converts audio to text using Google Cloud Speech-to-Text API.

SETUP INSTRUCTIONS:
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable "Cloud Speech-to-Text API"
4. Create service account and download JSON key
5. Set path in api_config.py or environment variable

Note: This module requires Google Cloud credentials to work.
For MVP testing without credentials, use the mock_transcribe() method.
"""

import os
from google.cloud import speech
from backend.core.config import APIConfig


class SpeechToText:
    """Handle speech-to-text conversion"""
    
    def __init__(self):
        """Initialize Google Cloud Speech client"""
        self.credentials_configured = False
        self.client = None
        
        # Try to initialize client
        try:
            if os.path.exists(APIConfig.GOOGLE_CLOUD_CREDENTIALS):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = APIConfig.GOOGLE_CLOUD_CREDENTIALS
                self.client = speech.SpeechClient()
                self.credentials_configured = True
        except Exception as e:
            print(f"Google Cloud credentials not configured: {str(e)}")
    
    
    def transcribe_audio(self, audio_content, encoding="LINEAR16", sample_rate=16000, language="en-US"):
        """
        Transcribe audio content to text
        
        Args:
            audio_content: Audio data in bytes
            encoding: Audio encoding format (LINEAR16, FLAC, etc.)
            sample_rate: Sample rate in Hz
            language: Language code (en-US, en-GB, etc.)
            
        Returns:
            Transcribed text as string
        """
        if not self.credentials_configured:
            raise Exception("Google Cloud credentials not configured. Please set up credentials in api_config.py")
        
        try:
            # Prepare audio
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=getattr(speech.RecognitionConfig.AudioEncoding, encoding),
                sample_rate_hertz=sample_rate,
                language_code=language,
                enable_automatic_punctuation=True,
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Extract transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
        
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    
    def transcribe_long_audio(self, audio_uri):
        """
        Transcribe long audio files (>1 minute) using async operation
        
        Args:
            audio_uri: GCS URI (gs://bucket-name/file.wav)
            
        Returns:
            Transcribed text as string
        """
        if not self.credentials_configured:
            raise Exception("Google Cloud credentials not configured")
        
        try:
            audio = speech.RecognitionAudio(uri=audio_uri)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            
            # Start async operation
            operation = self.client.long_running_recognize(config=config, audio=audio)
            
            print("Waiting for transcription to complete...")
            response = operation.result(timeout=300)
            
            # Extract transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
        
        except Exception as e:
            raise Exception(f"Long audio transcription error: {str(e)}")
    
    
    @staticmethod
    def mock_transcribe(duration_seconds=30):
        """
        Mock transcription for testing without Google Cloud credentials
        
        Args:
            duration_seconds: Simulated recording duration
            
        Returns:
            Mock transcript text
        """
        mock_transcript = """
        Good morning everyone. Thank you for joining today's requirements gathering session 
        for our new mobile banking application. Let me start by outlining the key features 
        we need to implement.
        
        First, users should be able to log in securely using their email and password. 
        We also need to support biometric authentication like fingerprint and face recognition 
        for enhanced security.
        
        Second, the dashboard should display account balance, recent transactions for the last 
        30 days, and quick access to frequently used features like transfers and bill payments.
        
        Third, users must be able to transfer money between their own accounts instantly, 
        and to other users within 24 hours. All transfers should require two-factor authentication 
        for amounts above $1000.
        
        Fourth, we need a bill payment feature that allows users to save payees, schedule 
        recurring payments, and receive notifications before payment due dates.
        
        The app must support both iOS and Android platforms, work offline for viewing 
        transaction history, and sync when connection is restored. Response time for any 
        action should not exceed 2 seconds under normal load.
        
        For security, all data must be encrypted both in transit and at rest. The app should 
        automatically log out users after 5 minutes of inactivity. We also need to implement 
        fraud detection that flags suspicious transactions.
        
        Are there any questions or additional requirements we should consider?
        """
        
        return mock_transcript.strip()
    
    
    def is_configured(self):
        """Check if Google Cloud credentials are properly configured"""
        return self.credentials_configured


# Initialize speech-to-text instance
stt = SpeechToText()