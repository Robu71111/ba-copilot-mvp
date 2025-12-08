"""
Audio Transcription Service
============================
Uses Gemini 2.0 Flash for audio transcription with proper File API handling
"""

import google.generativeai as genai
from backend.core.config import APIConfig
import base64
import tempfile
import os
import time
from google.api_core import exceptions as google_exceptions
from google.api_core import retry


class AudioTranscriber:
    """Handle audio recording and transcription"""
    
    def __init__(self):
        """Initialize Gemini Audio API"""
        self.api_configured = False
        
        try:
            # Configure Gemini API with MAIN API KEY
            genai.configure(api_key=APIConfig.GEMINI_API_KEY)
            
            # Use gemini-2.0-flash for transcription (supports audio input)
            self.transcription_model = genai.GenerativeModel(
                model_name=APIConfig.GEMINI_MODEL
            )
            
            self.api_configured = True
            print(f"✅ Audio transcription configured with model: {APIConfig.GEMINI_MODEL}")
        
        except Exception as e:
            print(f"❌ Audio API configuration error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    
    def transcribe_audio(self, audio_data, audio_format="wav"):
        """
        Transcribe audio to text using Gemini
        
        Args:
            audio_data: Audio data (base64 encoded or bytes)
            audio_format: Audio format (wav, mp3, webm, etc.)
            
        Returns:
            Transcribed text
        """
        if not self.api_configured:
            raise Exception("Transcription API not configured. Check GEMINI_API_KEY in environment.")
        
        temp_path = None
        audio_file = None
        
        try:
            print(f"🎙️ Transcribing audio using {APIConfig.GEMINI_MODEL}...")
            
            # Decode base64 if needed
            if isinstance(audio_data, str):
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            
            print(f"📊 Audio size: {len(audio_bytes)} bytes, format: {audio_format}")
            
            # Determine MIME type
            mime_type_map = {
                'wav': 'audio/wav',
                'mp3': 'audio/mp3',
                'webm': 'audio/webm',
                'm4a': 'audio/mp4',
                'ogg': 'audio/ogg',
                'flac': 'audio/flac'
            }
            mime_type = mime_type_map.get(audio_format.lower(), 'audio/wav')
            
            print(f"🔧 Using MIME type: {mime_type}")
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format}') as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            print(f"💾 Temporary file created: {temp_path}")
            
            # METHOD 1: Try using File API if available
            try:
                print("📤 Uploading audio to Gemini...")
                
                # Check if upload_file exists
                if hasattr(genai, 'upload_file'):
                    # Retry logic for rate limiting
                    max_retries = 3
                    retry_delay = 5
                    
                    for attempt in range(max_retries):
                        try:
                            audio_file = genai.upload_file(path=temp_path, mime_type=mime_type)
                            print(f"✅ Audio uploaded successfully: {audio_file.name}")
                            break
                        except google_exceptions.ResourceExhausted as e:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (attempt + 1)
                                print(f"⏳ Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                                time.sleep(wait_time)
                            else:
                                raise Exception(f"API rate limit exceeded after {max_retries} attempts. Please wait a few minutes and try again, or enable billing on your Google Cloud project for higher limits.")
                    
                    # Wait for processing
                    max_wait = 60
                    waited = 0
                    print("⏳ Waiting for audio processing...")
                    
                    while audio_file.state.name == "PROCESSING" and waited < max_wait:
                        print(f"   Processing... ({waited}s / {max_wait}s)")
                        time.sleep(2)
                        audio_file = genai.get_file(audio_file.name)
                        waited += 2
                    
                    if audio_file.state.name == "FAILED":
                        raise Exception("Audio file processing failed on Gemini servers")
                    
                    if audio_file.state.name == "PROCESSING":
                        raise Exception(f"Audio processing timeout after {max_wait} seconds")
                    
                    print(f"✅ Audio processing complete. State: {audio_file.state.name}")
                    
                    # Create transcription prompt
                    prompt = """
Please transcribe this audio recording into text.
This is a business meeting or requirements discussion.

Provide a clear, accurate, and complete transcription.
Include all spoken words and format it as a professional transcript.
Do not add any commentary or explanation - just the transcription.
"""
                    
                    # Generate transcription with retry
                    print("🤖 Generating transcription...")
                    for attempt in range(max_retries):
                        try:
                            response = self.transcription_model.generate_content([
                                prompt,
                                audio_file
                            ])
                            
                            transcript = response.text.strip()
                            print(f"✅ Transcription complete: {len(transcript)} characters")
                            
                            if not transcript:
                                raise Exception("Transcription returned empty text")
                            
                            return transcript
                        except google_exceptions.ResourceExhausted as e:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (attempt + 1)
                                print(f"⏳ Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                                time.sleep(wait_time)
                            else:
                                raise Exception(f"API rate limit exceeded after {max_retries} attempts. Please wait a few minutes and try again, or enable billing on your Google Cloud project for higher limits.")
                
                else:
                    raise AttributeError("upload_file not available")
            
            except (AttributeError, Exception) as upload_error:
                # Check if it's a rate limit error
                if "429" in str(upload_error) or "Resource exhausted" in str(upload_error) or "rate limit" in str(upload_error).lower():
                    raise Exception(f"⚠️ API RATE LIMIT EXCEEDED ⚠️\n\n"
                                  f"Your Gemini API has reached its quota limit.\n\n"
                                  f"Solutions:\n"
                                  f"1. Wait 1-5 minutes and try again (free tier: 15 requests/min)\n"
                                  f"2. Check your quota at: https://aistudio.google.com/app/apikey\n"
                                  f"3. Enable billing for higher limits: https://console.cloud.google.com/billing\n\n"
                                  f"Original error: {str(upload_error)}")
                
                # METHOD 2: Direct inline approach (fallback)
                print(f"⚠️ File upload not available: {str(upload_error)}")
                print("🔄 Attempting direct inline transcription...")
                
                # Read file back as bytes for inline upload
                with open(temp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Create transcription prompt
                prompt = """
Please transcribe this audio recording into text.
This is a business meeting or requirements discussion.

Provide a clear, accurate, and complete transcription.
Include all spoken words and format it as a professional transcript.
Do not add any commentary or explanation - just the transcription.
"""
                
                # Retry logic for inline method
                max_retries = 3
                retry_delay = 5
                
                for attempt in range(max_retries):
                    try:
                        print(f"🤖 Generating transcription (inline method, attempt {attempt + 1}/{max_retries})...")
                        response = self.transcription_model.generate_content([
                            prompt,
                            {
                                "mime_type": mime_type,
                                "data": audio_bytes
                            }
                        ])
                        
                        transcript = response.text.strip()
                        print(f"✅ Transcription complete (inline method): {len(transcript)} characters")
                        
                        if not transcript:
                            raise Exception("Transcription returned empty text")
                        
                        return transcript
                    
                    except google_exceptions.ResourceExhausted as e:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)
                            print(f"⏳ Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                            time.sleep(wait_time)
                        else:
                            raise Exception(f"⚠️ API RATE LIMIT EXCEEDED ⚠️\n\n"
                                          f"Your Gemini API has reached its quota limit.\n\n"
                                          f"Solutions:\n"
                                          f"1. Wait 1-5 minutes and try again (free tier: 15 requests/min)\n"
                                          f"2. Check your quota at: https://aistudio.google.com/app/apikey\n"
                                          f"3. Enable billing for higher limits: https://console.cloud.google.com/billing\n\n"
                                          f"Free tier limits: ~15 requests/minute, 1500/day")
        
        except Exception as e:
            print(f"❌ Transcription error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Audio transcription failed: {str(e)}")
        
        finally:
            # Clean up audio file from Gemini
            if audio_file and hasattr(genai, 'delete_file'):
                try:
                    genai.delete_file(audio_file.name)
                    print("🧹 Audio file cleaned up from Gemini")
                except Exception as cleanup_err:
                    print(f"⚠️ Could not cleanup remote file: {cleanup_err}")
            
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print("🧹 Temporary file cleaned up")
                except Exception as cleanup_err:
                    print(f"⚠️ Could not cleanup temp file: {cleanup_err}")
    
    
    def is_configured(self):
        """Check if API is properly configured"""
        return self.api_configured


# Initialize transcriber instance
audio_transcriber = AudioTranscriber()