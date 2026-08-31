from bisect import bisect_right
from pathlib import Path

from musicscore.chord import Chord
from musicscore.measure import Measure
from musicscore.part import Part
from musicscore.score import Score
from musicscore.staff import Staff
from musicscore.clef import TrebleClef, BassClef
from musicscore.key import Key
from musicscore.metronome import Metronome

from typing import List, cast
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
        snapped_start = max(0, bisect_right(beats, start) - 1)
        snapped_start_back = min(len(beats) - 1, bisect_right(beats, start))
        if beats[snapped_start_back] - start < start - beats[snapped_start]:
            snapped_start = snapped_start_back
        
        snapped_end = max(0, bisect_right(beats, end) - 1)
        snapped_end_back = min(len(beats) - 1, bisect_right(beats, end))
        if beats[snapped_end_back] - end < end - beats[snapped_end]:
            snapped_end = snapped_end_back

        # ignore pickups
        measure = bisect_right(downbeats, beats[snapped_start]) - 1
        if measure < 0:
            continue

        quarter_duration = snapped_end - snapped_start
        chord_durations.append([chord, quarter_duration, snapped_start])

    # score setup
    s = Score(title=musicxml_name)
    p = s.add_child(Part("P1", name="P1"))
    m = p.add_child(Measure(number=0))
    fifths = KEY_TO_FIFTHS[key]
    m.key = Key(fifths)
    st = m.add_child(Staff(number=1, clef=TrebleClef()))
    st.add_voice(voice_number=1)
    st = m.add_child(Staff(number=2, clef=BassClef()))
    st.add_voice(voice_number=1)

    added_tempo = False
    if fifths > 0:
        accidental_mode = "sharp"
    elif fifths < 0:
        accidental_mode = "flat"
    else:
        accidental_mode = "standard"

    # insert rests if first chord doesn't start on beat 1
    if len(chord_durations) > 0:
        # diff between starting beat of first chord and first downbeat becomes initial rest in quarter notes
        initial_rest = chord_durations[0][2] - beats.index(downbeats[0])
        if initial_rest > 0:
            chord = Chord(0, quarter_duration=initial_rest)
            if not added_tempo:
                chord.metronome = Metronome(round(tempo), beat_unit=1)
                added_tempo = True

            p.add_chord(Chord(0, quarter_duration=initial_rest), staff_number=2, voice_number=1)

    # adding chords
    for chord_name, duration, _ in chord_durations:
        from chord_recognition_module import ComplexChord
        midi = cast(List, ComplexChord(chord_name).to_midi())
        midi = [n - 12 for n in midi] # adjust down an octave so everything is readable in bass clef

        chord = Chord(midi if midi else 0, quarter_duration=duration)
        if not added_tempo:
            chord.metronome = Metronome(round(tempo), beat_unit=1)
            added_tempo = True

        for pitch in chord.midis:
            pitch.accidental.mode = accidental_mode

        p.add_chord(chord, staff_number=2, voice_number=1)

    # fix formatting on the top staff
    for m in p.get_children():
        m.get_staff(staff_number=1).fill_with_rests()

    # hide accidentals supplied by the key signature
    if fifths > 0:
        key_accidentals = {step: 1 for step in "FCGDAEB"[:fifths]}
    elif fifths < 0:
        key_accidentals = {step: -1 for step in "BEADGCF"[:-fifths]}
    else:
        key_accidentals = {}

    for m in cast(List[Measure], p.get_children()):
        for staff in m.get_children():
            accidental_state = {} # track accidental changes within measure
            for score_chord in staff.get_chords():
                if score_chord.is_rest:
                    continue

                for pitch in score_chord.midis:
                    if pitch.is_tied_to_previous:
                        pitch.accidental.show = False
                        continue

                    step, alter, octave = pitch.accidental.get_pitch_parameters()
                    state_key = (step, octave)
                    current_alter = accidental_state.get(state_key, key_accidentals.get(step, 0))
                    pitch.accidental.show = alter != current_alter
                    accidental_state[state_key] = alter
    
    xml_path = Path(__file__).parent.joinpath(musicxml_name).with_suffix('.musicxml')
    s.export_xml(xml_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: json_to_musicxml.py path_to_json_file musicxml_name")
        exit(0)

    json_to_musicxml(sys.argv[1], sys.argv[2])    
