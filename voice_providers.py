import os
import requests
import base64
from abc import ABC, abstractmethod
from openai import OpenAI

class VoiceProvider(ABC):
    @abstractmethod
    def generate_speech(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_voice_list(self) -> list:
        pass

class OpenAIVoiceProvider(VoiceProvider):
    def __init__(self, config):
        self.api_key = config.get('OPENAI_API_KEY')
        try:
            self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"OpenAI client initialization error: {e}")
            self.client = None
    
    def generate_speech(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        if not self.client:
            return False
        
        try:
            speed = kwargs.get('speed', 1.0)
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=float(speed)
            )
            response.stream_to_file(output_path)
            return True
        except Exception as e:
            print(f"OpenAI TTS error: {e}")
            return False
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_voice_list(self) -> list:
        return [
            {'value': 'alloy', 'name': 'Alloy (Neutral)'},
            {'value': 'echo', 'name': 'Echo (Male)'},
            {'value': 'fable', 'name': 'Fable (British Male)'},
            {'value': 'onyx', 'name': 'Onyx (Deep Male)'},
            {'value': 'nova', 'name': 'Nova (Female)'},
            {'value': 'shimmer', 'name': 'Shimmer (Soft Female)'}
        ]

class ElevenLabsVoiceProvider(VoiceProvider):
    def __init__(self, config):
        self.api_key = config.get('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # ElevenLabs voice IDs (you may need to update these)
        self.voice_ids = {
            'rachel': '21m00Tcm4TlvDq8ikWAM',
            'domi': 'AZnzlk1XvdvUeBnXmlld',
            'bella': 'EXAVITQu4vr4xnSDxMaL',
            'antoni': 'ErXwobaYiN019PkySvjV',
            'josh': 'TxGEqnHWrfWFTfGW9XjX',
            'adam': 'pNInz6obpgDQGcFmaJgB'
        }
    
    def generate_speech(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        if not self.api_key:
            return False
        
        try:
            stability = kwargs.get('stability', 0.5)
            voice_id = self.voice_ids.get(voice, self.voice_ids['rachel'])
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": float(stability),
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
            
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return False
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_voice_list(self) -> list:
        return [
            {'value': 'rachel', 'name': 'Rachel (American Female)'},
            {'value': 'domi', 'name': 'Domi (American Female)'},
            {'value': 'bella', 'name': 'Bella (American Female)'},
            {'value': 'antoni', 'name': 'Antoni (American Male)'},
            {'value': 'josh', 'name': 'Josh (American Male)'},
            {'value': 'adam', 'name': 'Adam (American Male)'}
        ]

class GoogleVoiceProvider(VoiceProvider):
    def __init__(self, config):
        self.api_key = config.get('GOOGLE_CLOUD_API_KEY')
        self.base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    
    def generate_speech(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        if not self.api_key:
            return False
        
        try:
            speed = kwargs.get('speed', 1.0)
            
            # Parse voice name to get language and name
            if voice.startswith('zh-CN'):
                language_code = 'zh-CN'
            else:
                language_code = 'en-US'
            
            headers = {"Content-Type": "application/json"}
            
            data = {
                "input": {"text": text},
                "voice": {
                    "languageCode": language_code,
                    "name": voice
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": float(speed)
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                audio_content = response.json()["audioContent"]
                audio_data = base64.b64decode(audio_content)
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                return True
            return False
            
        except Exception as e:
            print(f"Google TTS error: {e}")
            return False
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_voice_list(self) -> list:
        return [
            {'value': 'en-US-Standard-A', 'name': 'US English (Female A)'},
            {'value': 'en-US-Standard-B', 'name': 'US English (Male B)'},
            {'value': 'en-US-Standard-C', 'name': 'US English (Female C)'},
            {'value': 'en-US-Standard-D', 'name': 'US English (Male D)'},
            {'value': 'en-US-Wavenet-A', 'name': 'US English Wavenet (Female A)'},
            {'value': 'en-US-Wavenet-B', 'name': 'US English Wavenet (Male B)'}
        ]

class AzureVoiceProvider(VoiceProvider):
    def __init__(self, config):
        self.api_key = config.get('AZURE_SPEECH_KEY')
        self.region = config.get('AZURE_SPEECH_REGION', 'eastus')
        self.base_url = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    def generate_speech(self, text: str, voice: str, output_path: str, **kwargs) -> bool:
        if not self.api_key:
            return False
        
        try:
            speed = kwargs.get('speed', 1.0)
            speed_percent = f"{int((speed - 1) * 100):+d}%"
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
            }
            
            ssml = f"""
            <speak version='1.0' xml:lang='en-US'>
                <voice xml:lang='en-US' name='{voice}'>
                    <prosody rate='{speed_percent}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            response = requests.post(self.base_url, data=ssml, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
            
        except Exception as e:
            print(f"Azure TTS error: {e}")
            return False
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_voice_list(self) -> list:
        return [
            {'value': 'en-US-AriaNeural', 'name': 'Aria (US Female)'},
            {'value': 'en-US-DavisNeural', 'name': 'Davis (US Male)'},
            {'value': 'en-US-GuyNeural', 'name': 'Guy (US Male)'},
            {'value': 'en-US-JaneNeural', 'name': 'Jane (US Female)'},
            {'value': 'en-US-JasonNeural', 'name': 'Jason (US Male)'},
            {'value': 'en-US-JennyNeural', 'name': 'Jenny (US Female)'}
        ]

def get_voice_provider(provider_name: str, config) -> VoiceProvider:
    providers = {
        'openai': OpenAIVoiceProvider,
        'elevenlabs': ElevenLabsVoiceProvider,
        'google': GoogleVoiceProvider,
        'azure': AzureVoiceProvider
    }
    
    provider_class = providers.get(provider_name)
    return provider_class(config) if provider_class else None