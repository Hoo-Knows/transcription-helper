from audio_to_json import audio_to_json
from json_to_musicxml import json_to_musicxml

from pathlib import Path
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: main.py path_to_audio_file musicxml_name')
        exit(0)

    json_path = Path(__file__).parent.joinpath(sys.argv[2]).with_suffix('.json')
    audio_to_json(sys.argv[1], json_path)
    print("Creating MusicXML...")
    json_to_musicxml(json_path, sys.argv[2])
    print("Done!")