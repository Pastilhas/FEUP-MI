import os
import time
from tqdm import tqdm
import music21
from utils import *

def txt_to_stream(string):
  speed = 1.0 / SAMPLE_FREQUENCY
  notes = [[] for i in INSTRUMENT_TAG]
  time_offset = 0
  score = string.split()
  prev_note_wait = False
  with tqdm(score) as pbar:
    for i, note_ in enumerate(score):
        pbar.update(1)
        note = note_.split(FEATURE_SEPARATOR)
        mark = note[0]
        # On wait skip time
        if mark == WAIT_MARK:
            time_offset += int(note[1])
            prev_note_wait = True
            continue
        
        # On start create note
        elif mark == START_MARK:
            if prev_note_wait: time_offset += 1
            prev_note_wait = False
            pitch, duration, volume, instrument = int(note[1]), int(note[2]), int(note[3]), note[4]
            
            # Create note
            new_note = music21.note.Note(pitch + NOTE_OFFSET)
            new_note.duration = music21.duration.Duration(duration)
            new_note.offset = time_offset * speed
            new_note.volume = music21.volume.Volume(velocity=volume)
            notes[INSTRUMENT_TAG.index(instrument)].append(new_note)

    # Create list of streams for each instrument and join them
    instruments = list(map(lambda x: music21.instrument.fromString(x[0]), INSTRUMENTS))
    streams = list(map(lambda x,y: music21.stream.Stream([y] + x), notes, instruments))
    stream = music21.stream.Stream(streams)
    return music21.stream.Stream(notes[0])
        

###############################################################################

def main():
    for file in os.scandir(TXT_OUTPUT_DIRECTORY):
        if file.is_file() and file.name.lower().endswith('.txt'):
            print('Started converting', file.name)
            start_time = time.time()

            with open(file, 'r') as f: string = f.read()
            stream = txt_to_stream(string)
            stream.write('midi', fp=MIDI_OUTPUT_DIRECTORY + file.name[:-4] + '.mid')
            
            end_time = time.time()
            print('Finished converting', file.name, 'in', round(end_time - start_time, 2), 'seconds')
            
if __name__ == '__main__':
    main()
