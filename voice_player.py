"""
Voice Player using Edge TTS
Handles text-to-speech functionality with natural Spanish voices
"""

import os
import asyncio
import edge_tts
import tempfile
import pygame


class VoicePlayer:
    def __init__(self):
        # Voice settings from environment or defaults
        # Available Spanish voices:
        # es-ES-ElviraNeural (female, Spain)
        # es-ES-AlvaroNeural (male, Spain)
        # es-MX-DaliaNeural (female, Mexico)
        # es-MX-JorgeNeural (male, Mexico)
        # es-AR-ElenaNeural (female, Argentina)
        # es-AR-TomasNeural (male, Argentina)
        
        self.voice = os.getenv("EDGE_VOICE", "es-ES-ElviraNeural")
        self.rate = os.getenv("VOICE_RATE", "+0%")  # -50% to +100%
        self.volume = os.getenv("VOICE_VOLUME", "+0%")  # -50% to +50%
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
    def speak(self, text: str):
        """
        Convert text to speech and play using Edge TTS
        
        Args:
            text: Text to speak
        """
        try:
            # Run async function in sync context
            asyncio.run(self._speak_async(text))
        except Exception as e:
            print(f"Error speaking text: {e}")
            
    async def _speak_async(self, text: str):
        """Async method to generate and play speech"""
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
            
        try:
            # Generate speech
            communicate = edge_tts.Communicate(
                text,
                self.voice,
                rate=self.rate,
                volume=self.volume
            )
            
            # Save to file
            await communicate.save(temp_path)
            
            # Play audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    def stop(self):
        """Stop current speech"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping speech: {e}")
            
    def set_voice(self, voice: str):
        """
        Set voice
        
        Args:
            voice: Voice name (e.g., 'es-ES-ElviraNeural')
        """
        self.voice = voice
        
    def set_rate(self, rate: str):
        """
        Set speech rate
        
        Args:
            rate: Rate adjustment (e.g., '+0%', '+50%', '-25%')
        """
        self.rate = rate
        
    def set_volume(self, volume: str):
        """
        Set volume
        
        Args:
            volume: Volume adjustment (e.g., '+0%', '+25%', '-25%')
        """
        self.volume = volume
        
    @staticmethod
    def list_voices():
        """List available Spanish voices"""
        voices = [
            "es-ES-ElviraNeural (female, Spain) - Natural",
            "es-ES-AlvaroNeural (male, Spain) - Natural",
            "es-MX-DaliaNeural (female, Mexico) - Natural",
            "es-MX-JorgeNeural (male, Mexico) - Natural",
            "es-AR-ElenaNeural (female, Argentina) - Natural",
            "es-AR-TomasNeural (male, Argentina) - Natural",
        ]
        for voice in voices:
            print(voice)
