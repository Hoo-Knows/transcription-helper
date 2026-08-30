from chord_recognition_module import chord_recognition
from madmom.features.key import CNNKeyRecognitionProcessor, key_prediction_to_label
from madmom.features.tempo import TempoEstimationProcessor
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
from madmom.features.downbeats import DBNBarTrackingProcessor, RNNBarProcessor
import sys
import json

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: main.py path_to_audio_file path_to_output_file')
        exit(0)

    # ISMIR2019-Large-Vocabulary-Chord-Recognition for chord recognition
    chords = chord_recognition(sys.argv[1])

    # madmom for key, tempo, beats, bars
    print("Detecting key...")
    key_proc = CNNKeyRecognitionProcessor()
    key_class_ids = key_proc(sys.argv[1])
    key = key_prediction_to_label(key_class_ids)

    print("Detecting beats/tempo...")
    beat_act = RNNBeatProcessor()(sys.argv[1])
    beat_proc = DBNBeatTrackingProcessor(fps=100)
    tempo_proc = TempoEstimationProcessor("dbn", fps=100)

    beats = beat_proc(beat_act)
    tempo = tempo_proc(beat_act)

    print("Detecting bars...")
    bar_act = RNNBarProcessor()((sys.argv[1], beats))
    bar_proc = DBNBarTrackingProcessor(beats_per_bar=[4, 4])

    bars = bar_proc(bar_act)

    # write data to json
    song_data = {}
    song_data["key"] = key
    song_data["tempo"] = tempo[0][0] # tempo is 2d array with columns tempo, prob
    song_data["bars"] = bars.tolist()
    song_data["chords"] = chords

    with open(sys.argv[2], "w") as file:
        json.dump(song_data, file, indent=4)

