import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import subprocess
from pydub import AudioSegment

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AudioTranscript:
    text: str
    segments: List[Dict[str, Any]]
    language: str

class AudioProcessor:
    def __init__(self, 
                 language: str | None = None,
                 model_size_or_path: str = "medium",
                 device: str = "cuda"):
        """Initialize audio processor with specified Whisper model size or model path. By default, the medium model is used."""
        try:
            from faster_whisper import WhisperModel
            
            # Log cache directory
            cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
            logger.debug(f"Using HuggingFace cache directory: {cache_dir}")
            
            # Force CPU usage for now faster whisper having issues with cudas
            self.device = device
            compute_type = "float32"
            logger.debug(f"Using device: {self.device}")

            self.language = language if language else None
            # TODO: fix the bug when using cuda, Could not load library libcudnn_ops_infer.so.8. Error: libcudnn_ops_infer.so.8: cannot open shared object file: No such file or directory
            # If you want to use cuda, make sure to install the 12 version of cuda and cudnn9

            self.model = WhisperModel(
                model_size_or_path,
                device=device,
                compute_type=compute_type
            )
            logger.info(f"Initiation Input: Model size or path: {model_size_or_path}, Device: {device}, Compute type: {compute_type}, Language: {self.language if self.language else 'auto detected'}")
            logger.debug(f"Successfully loaded Whisper model: {model_size_or_path}")
            
            # Check for ffmpeg installation
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                self.has_ffmpeg = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.has_ffmpeg = False
                logger.warning("FFmpeg not found. Please install ffmpeg for better audio extraction.")
                
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise

    def extract_audio(self, video_path: Path, output_dir: Path) -> Optional[Path]:
        """Extract audio from video file and convert to format suitable for Whisper.
        Returns None if video has no audio streams."""
        audio_path = output_dir / "audio.wav"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Extract audio using ffmpeg
            subprocess.run([
                "ffmpeg", "-i", str(video_path),
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
                "-ar", "16000",  # 16kHz sampling rate
                "-ac", "1",  # Mono
                "-y",  # Overwrite output
                str(audio_path)
            ], check=True, capture_output=True)
            
            logger.debug("Successfully extracted audio using ffmpeg")
            return audio_path
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode()
            logger.error(f"FFmpeg error: {error_output}")
            
            # Check if error indicates no audio streams
            if "Output file does not contain any stream" in error_output:
                logger.debug("No audio streams found in video - skipping audio extraction")
                return None
                
            # If error is not about missing audio, try pydub as fallback
            logger.info("Falling back to pydub for audio extraction...")
            try:
                video = AudioSegment.from_file(str(video_path))
                audio = video.set_channels(1).set_frame_rate(16000)
                audio.export(str(audio_path), format="wav")
                logger.debug("Successfully extracted audio using pydub")
                return audio_path
            except Exception as e2:
                logger.error(f"Error extracting audio using pydub: {e2}")
                # If both methods fail, raise error
                raise RuntimeError(
                    "Failed to extract audio. Please install ffmpeg using:\n"
                    "Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg\n"
                    "MacOS: brew install ffmpeg\n"
                    "Windows: choco install ffmpeg"
                )

    def transcribe(self, audio_path: Path) -> Optional[AudioTranscript]:
        """Transcribe audio file using Whisper with quality checks."""
        accepted_languages = {
                "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh", "yue"
        }
        if self.language and self.language not in accepted_languages:
            logger.warning(f"Invalid language code: {self.language}, will detect language automatically")
        try:
            # Initial transcription with VAD filtering
            segments, info = self.model.transcribe(
                str(audio_path),
                beam_size=5,
                word_timestamps=True,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                language = self.language if self.language in accepted_languages else None
            )
            
            segments_list = list(segments)
            if not segments_list:
                logger.warning("No speech detected in audio")
                return None
            
            # Convert segments to the expected format
            segment_data = [
                {
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                    "words": [
                        {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        }
                        for word in (segment.words or [])
                    ]
                }
                for segment in segments_list
            ]
            
            return AudioTranscript(
                text=" ".join(segment.text for segment in segments_list),
                segments=segment_data,
                language=info.language
            )
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            logger.exception(e)
            return None
        

if __name__ == "__main__":
    import time
    time_start = time.time()
    audio_processor = AudioProcessor()
    transcript = audio_processor.transcribe("/home/lzh/videoplayback.mp4")
    print(transcript.text)
    print(transcript.segments)
    print(transcript.language)
    time_end = time.time()
    print(f"Time taken: {time_end - time_start} seconds")
