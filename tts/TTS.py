from kokoro import KPipeline
import soundfile as sf
import torch
import io
import base64
from datetime import datetime

 # Input text
# text = '''
# '''
LANGUAGES = {'ES':'e', 'EN': 'a'}

class TTSGenerator:
    def __init__(self, tts_language:str="EN"):
        
        # Initialize the TTS pipeline
        self.pipeline = KPipeline(repo_id='hexgrad/Kokoro-82M', lang_code=LANGUAGES.get(tts_language,'a'), device ='cuda' if torch.cuda.is_available() else 'cpu')
        self.voice = "am_adam" if tts_language == "EN" else "em_alex"
        
    def generate(self, text:str, save:bool = True, split_pattern:str='') -> list[dict]:
        """
        Generate TTS audio from text with optional base64 encoding and saving.
        Args:
            text (str): The input text to synthesize.
            b64 (bool): Whether to return audio as base64 encoded string.
            save (bool): Whether to save the audio files to disk.
            split_pattern (str): Pattern to split the audio. If empty, no splitting is done.
        Returns:
            list[dict]: A list of dictionaries containing split audio results.
            
        If split_pattern = '', the entire audio will be processed as a single unit and the list will contain one dictionary with the full audio.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g. 20250620_173245
        # Generate audio

        generator = self.pipeline(text=text, voice=self.voice, speed=0.9, split_pattern=split_pattern)
        
        results = []
        
        for i, (gs, ps, audio) in enumerate(generator):
            
            split_result = {
                'split_index': i,
                'graphemes': gs,
                'phonemes': ps,
                'audio_b64' : ""
            }
            
            
            buffer = io.BytesIO()
            sf.write(buffer, audio, 24000, format='WAV')
            buffer.seek(0)
            audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            split_result['audio_b64'] = audio_b64
            #print(f"Generated audio for split {i} with base64 encoding.")
            
            # if save: # Decode back for verification
            #     audio_bytes = base64.b64decode(audio_b64)
            #     reconstructed_path = f'tts/{timestamp}_{self.voice}_{i}_reconstructed.wav'
            #     with open(reconstructed_path, 'wb') as f:
            #         f.write(audio_bytes)
            #     print(f"Saved reconstructed audio to {reconstructed_path}")
                
            if save:
                original_path = f'tts/{timestamp}_{i}.wav'
                sf.write(original_path, audio, 24000)
                #print(f"Saved original audio to {original_path}")
                
            results.append(split_result)
            
        tts_base64 = results[0].get("audio_b64", "")
            
        return tts_base64         


# if __name__ == "__main__":
#     tts = TTSGenerator()
#     output = tts.generate(text, save=True)
#     print("TTS synthesis completed and saved.")
    
#     print("Output:", output)

        

            
        



