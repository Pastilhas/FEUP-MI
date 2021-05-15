VIOLINLIKE = ['Violin', 'Viola', 'Cello', 'Violincello', 'Violoncello', 'Flute',
              'Oboe', 'Clarinet', 'Recorder', 'Voice', 'Piccolo',
              'StringInstrument', 'Bassoon', 'Horn']
PIANOLIKE = ['Piano', 'Harp', 'Harpsichord', 'Organ', '']
INSTRUMENTS = [PIANOLIKE, VIOLINLIKE]
INSTRUMENT_TAG = ['p', 'v']

START_MARK = 'start'
END_MARK = 'end'
WAIT_MARK = 'wait'
FEATURE_SEPARATOR = ':'
NOTE_SEPARATOR = ','

MIDI_INPUT_DIRECTORY = 'data/input_midi/'
TXT_INPUT_DIRECTORY = 'data/input_txt/'
MIDI_OUTPUT_DIRECTORY = 'data/output_midi/'
TXT_OUTPUT_DIRECTORY = 'data/output_txt/'
SAMPLE_FREQUENCY = 12
NOTE_OFFSET = 33
NOTE_RANGE = 62


# return value between min and max using step
def clamp(value, min_=0, max_=100, step=1): return max(min_, min(value - value % step, max_))