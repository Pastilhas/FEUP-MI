from utils import *

class Note:
    def __init__(self, mark=WAIT_MARK, pitch=0, duration=0, volume=0, instrument=INSTRUMENT_TAG[0]):
        self.mark = mark
        self.pitch = int(pitch)
        self.duration = int(duration)
        self.volume = int(volume)
        self.instrument = instrument
    
    def from_string(self, string=''):
        split = string.split(FEATURE_SEPARATOR)
        self.mark = split[0]
        if split[0] == WAIT_MARK:
            self.duration = int(split[1])
        else:
            self.pitch = int(split[1])
            self.volume = int(split[2])
            self.instrument = split[3]

    def __str__(self):
        array = [self.mark]
        if self.mark == WAIT_MARK:
            array.append(str(self.duration))
        else:
            array.append(str(self.pitch))
            array.append(str(self.volume))
            array.append(self.instrument)
        return FEATURE_SEPARATOR.join(array)
        

