from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from .provider import VoiceResult
class GTTSProvider:
    def synthesize(self, text: str, *, preset: str, output_path: Path) -> VoiceResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        gTTS(text=text, lang="en", tld="com", slow=preset == "calm").save(str(output_path))
        duration = len(AudioSegment.from_file(output_path)) / 1000
        return VoiceResult(output_path=output_path, duration_seconds=duration)
