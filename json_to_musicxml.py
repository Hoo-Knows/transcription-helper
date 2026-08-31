from bisect import bisect_right
from pathlib import Path

from musicscore.chord import Chord
from musicscore.measure import Measure
from musicscore.part import Part
from musicscore.score import Score
from musicscore.staff import Staff
from musicscore.clef import TrebleClef, BassClef
from musicscore.key import Key

from typing import List, cast
from fractions import Fraction
import json
import sys

KEY_TO_FIFTHS = {
    'C major': 0, 'G major': 1, 'D major': 2, 'A major': 3, 'E major': 4, 'B major': 5, 'F# major': 6,
    'Db major': -5, 'Ab major': -4, 'Eb major': -3, 'Bb major': -2, 'F major': -1,
    'A minor': 0, 'E minor': 1, 'B minor': 2, 'F# minor': 3, 'C# minor': 4, 'G# minor': 5, 'D# minor': 6,
    'Bb minor': -5, 'F minor': -4, 'C minor': -3, 'G minor': -2, 'D minor': -1
}

def json_to_musicxml(json_path, musicxml_name):
    file = open(json_path, "r")
    song_data = json.load(file)
    file.close()

    key = song_data["key"]
    tempo = song_data["tempo"]
    bars = song_data["bars"]
    beats = [row[0] for row in bars]
    downbeats = [row[0] for row in filter(lambda row: row[1] == 1, bars)]
    chords = song_data["chords"]

    # get duration in quarter notes
    chord_durations = []
    for row in chords:
        start, end, chord = row

        # estimate note duration by snapping start and end timestamps to closest beat
        snapped_start = beats[max(0, bisect_right(beats, start) - 1)]
        snapped_start_back = beats[min(len(beats) - 1, bisect_right(beats, start))]
        if snapped_start_back - start < start - snapped_start:
            snapped_start = snapped_start_back
        
        snapped_end = beats[bisect_right(beats, end) - 1]
        snapped_end_back = beats[min(len(beats) - 1, bisect_right(beats, end))]
        if snapped_end_back - end < end - snapped_end:
            snapped_end = snapped_end_back

        # ignore pickups
        measure = bisect_right(downbeats, snapped_start) - 1
        if measure < 0: # ignore pickups for now
            continue

        # TODO: actually add subdivisions
        subdivisions = 4 # 16ths
        numerator = round((snapped_end - snapped_start) / 60 * tempo * subdivisions)
        quarter_duration = Fraction(numerator, subdivisions)
        
        chord_durations.append([chord, quarter_duration])

    # score setup
    s = Score(title=musicxml_name)
    p = s.add_child(Part("P1", name="P1"))
    m = p.add_child(Measure(number=0))
    m.key = Key(KEY_TO_FIFTHS[key])
    st = m.add_child(Staff(number=1, clef=TrebleClef()))
    st = m.add_child(Staff(number=2, clef=BassClef()))
    st.add_voice(voice_number=1)

    # adding chords
    for chord_name, duration in chord_durations:
        from chord_recognition_module import ComplexChord
        midi = cast(List, ComplexChord(chord_name).to_midi())

        chord = (
            Chord(midi, quarter_duration=duration)
            if midi
            else Chord(0, quarter_duration=duration)
        )

        p.add_chord(chord, staff_number=2, voice_number=1)
    
    xml_path = Path(__file__).parent.joinpath(musicxml_name).with_suffix('.musicxml')
    s.export_xml(xml_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: json_to_musicxml.py path_to_json_file musicxml_name")
        exit(0)

    json_to_musicxml(sys.argv[1], sys.argv[2])    
