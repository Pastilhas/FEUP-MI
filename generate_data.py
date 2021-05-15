import math
import os
import time

import music21
import numpy as np
from utils import *

# return id of instrument from name
def get_instrument_id(instrument):
    for i in range(len(INSTRUMENTS)):
        if instrument in INSTRUMENTS[i]:
            return i
    return -1

# return token in shape
# mark:pitch:velocity:instrument
def get_token(mark, pitch, duration, volume, instrument_id): return FEATURE_SEPARATOR.join([mark, pitch, duration, volume, instrument_id])

# return tag of instrument from id
def get_instrument_tag(instrument): return INSTRUMENT_TAG[instrument] if instrument >= 0 and instrument < len(INSTRUMENT_TAG) else 'p'

# return instrument or default piano
def instrument_or_piano(note): return note.getInstrument() if get_instrument_id(note.getInstrument()) >= 0 else PIANOLIKE[0]

# return tuple with note features
# tuple(pitch, start, duration, volume, instrument)
def store_note(pitch, offset, duration, volume, instrument):
    return (pitch.midi - NOTE_OFFSET, 
        math.floor(offset * SAMPLE_FREQUENCY), 
        math.floor(duration.quarterLength * SAMPLE_FREQUENCY), 
        volume.velocity,
        instrument,
    )

# convert stream of notes to score array
# only one instrument per stream
def stream_to_notes(stream):
    last_time_step = math.floor(stream.duration.quarterLength * SAMPLE_FREQUENCY) + 1
    score_array = ['' for i in range(last_time_step)]
    score_array = np.array(score_array, dtype=object)
    note_filter = music21.stream.filters.ClassFilter('Note')
    chord_filter = music21.stream.filters.ClassFilter('Chord')
    notes = []

    # Parse notes
    for note in stream.recurse().addFilter(note_filter):
        pitch = note.pitch
        offset = note.offset
        duration = note.duration
        volume = note.volume
        instrument_id = get_instrument_id(instrument_or_piano(note.activeSite))
        store = store_note(pitch, offset, duration, volume, instrument_id)
        notes.append(store)

    # Parse chords
    for chord in stream.recurse().addFilter(chord_filter):
        pitches_in_chord = chord.pitches
        offset = chord.offset
        duration = chord.duration
        volume = chord.volume
        instrument_id = get_instrument_id(instrument_or_piano(chord.activeSite))
        for pitch in pitches_in_chord:
            store = store_note(pitch, offset, duration, volume, instrument_id)
            notes.append(store)

    # Write notes to array
    # tuple(pitch, start, duration, volume, instrument)
    for note in notes:
        pitch = clamp(note[0], 0, NOTE_RANGE - 1)
        start, duration = note[1], note[2]
        volume = clamp(note[3], 30, 80)
        instrument_tag = get_instrument_tag(note[4])

        start_token = get_token(START_MARK, str(pitch), str(duration), str(volume), instrument_tag)
        score_array[start] += start_token + NOTE_SEPARATOR

    return score_array

# convert score array to string
# array of tokens start:pitch:velocity:instrument 
# and end:pitch:velocity:instrument
def notes_to_string(score_array):
    translated_list, translated_string = [], ''

    for i, chord in enumerate(score_array):
        if chord == '':
            translated_list.append(WAIT_MARK)
            continue
        notes = chord.split(NOTE_SEPARATOR)
        for note in notes[:-1]:
            translated_list.append(note)

    i = 0
    while i < len(translated_list):
        wait_count = 1
        if translated_list[i] == WAIT_MARK:
            max_wait = min(len(translated_list) - i, SAMPLE_FREQUENCY * 2)
            while wait_count < max_wait and translated_list[i + wait_count] == WAIT_MARK:
                wait_count += 1
            translated_list[i] = 'wait:' + str(wait_count)
        translated_string += translated_list[i] + ' '
        i += wait_count

    return translated_string, translated_string.split()

# convert midi file to string tokens
# token wait            wait:duration 
# token start note      start:pitch:velocity:instrument
# token end note        end:pitch:velocity:instrument
def midi_to_txt(file):
    start_time = time.time()
    midi_file = music21.midi.MidiFile()
    midi_file.open(file.path)
    midi_file.read()
    midi_file.close()
    midi_stream = music21.midi.translate.midiFileToStream(midi_file)
    score_array = stream_to_notes(midi_stream)
    score_string, _ = notes_to_string(score_array)

    output_filename = TXT_INPUT_DIRECTORY + '/' + file.name[:-4] + '.txt'
    output_file = open(output_filename, 'w+')
    output_file.write(score_string + "end")
    output_file.close()

    end_time = time.time()
    print('Finished converting', file.name, 'in', round(end_time - start_time, 2), 'seconds')

###############################################################################

def main():
    for file in os.scandir(MIDI_INPUT_DIRECTORY):
        if file.is_file() and file.name.lower().endswith('.mid'):
            midi_to_txt(file)

if __name__ == '__main__':
    main()
