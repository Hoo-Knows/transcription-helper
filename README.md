# Transcription Helper

WIP, currently outputs a (most likely incorrect and/or poorly formatted) MusicXML file and a JSON file containing key, tempo, beats and their position in the bar, and timestamped chords.

## Usage
Install [uv](https://docs.astral.sh/uv/), then run
```bash
git clone --recurse-submodules https://github.com/Hoo-Knows/transcription-helper
cd transcription-helper
uv run main.py path_to_audio_file musicxml_name
```