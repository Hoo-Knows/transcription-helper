# Transcription Helper

Small python script that accept an audio file and output a Music XML file and a JSON file containing key, tempo, beats and their position in the bar, and timestamped chords.

Limitations: Currently assumes 4/4 and no key/tempo changes; the resulting Music XML will likely be incorrect/have weird formatting if these assumptions are broken.

## Usage
Install [uv](https://docs.astral.sh/uv/), then run
```bash
git clone --recurse-submodules https://github.com/Hoo-Knows/transcription-helper
cd transcription-helper
uv run main.py path_to_audio_file musicxml_name
```

## Todo
- Add options to customize sheet generation (one staff only, octave offset, make beats not snap to quarter notes)
- Melody transcription?
- Allow user input to guide transcription? (key/tempo change timestamps)