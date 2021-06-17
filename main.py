import multiprocessing as mp
from random import sample
from time import sleep
from sys import stdout
import run_model as model
import sounddevice as recorder
import midi_player

INPUT_CODE = {
    1: 'piano',
    2: 'violin',
    3: 'ratio',
    4: 'time',
    5: 'mic',
    6: 'coffee',
}

def generator(inputQ, resultQ, readyE, stopE):
    print('Generator is running.')
    readyE.set()
    model.run_with_input(inputQ, resultQ, stopE)
    
def player(resultQ, readyE, stopE):
    print('Player is running.')
    readyE.set()
    midi_player.play_with_input(resultQ, stopE)

def ask_input(inputQ, stopE):     
    print(
        '''
        Inputs:
        Code          Name        Desc
        1 <value>   - Piano     - Increase weight of piano notes
        2 <value>   - Violin    - Increase weight of violin notes
        3 <value>   - Ratio     - Change music using ratios (0 to 100)
        4 <value>   - Time      - Generate based on time of day (in seconds)
        5           - Microfone - Read microfone and affect generation
        6           - Coffee    - Change generation when making coffee
        7           - Exit      - Exit
     ''')
    cmd = input('?- ')
    cmd = cmd.split(' ')
    
    first, second = 0, 0
    if len(cmd) > 0:
        first = int(cmd[0]) if cmd[0].isnumeric() else 6
        first = max(min(first, 1), 7)
    if len(cmd) > 1:
        second = int(cmd[1]) if cmd[1].isnumeric() else 0
        second = max(min(second, 0), 100)
    
    # Case microfone, read
    if first == 5:
        recording = recorder.rec(int(1 * 44100), samplerate=44100, channels=2)
        recorder.wait()
        recorder.play(recording, 44100)
        second = max(min(int(recording[0]), 0), 100)
        print(
        '''
        Recorded audio.
        ''')
        
    # Case coffee, nothing (yet)
    if first == 6:
        pass
    
    # Case exit
    if first == 7:
        stopE.set()
        return
    
    code = INPUT_CODE.get(first, 'null') + ':' + str(second)
    inputQ.put(code)    # Send code to generator process
    

def main():
    
    inputQ = mp.Queue()        # Queue for inputs from user
    resultQ = mp.Queue()       # Queue for notes to be played
    readyE1 = mp.Event()       # Event to stop program
    readyE2 = mp.Event()       # Event to stop program
    stopE = mp.Event()         # Event to stop program
    
    generatorP = mp.Process(target=generator, args=(inputQ,resultQ,readyE1,stopE))      # Process that generates notes and takes inputs
    playerP = mp.Process(target=player, args=(resultQ,readyE2,stopE))                   # Process that plays notes
    generatorP.start()
    playerP.start()
    
    readyE1.wait()
    readyE2.wait()
    
    print(
        '''
        «=========================»
        |                         |
        |   OwO Music Generator   |
        |                         |
        |   by Joao Campos        |
        |                         |
        «=========================»
        
        Use the inputs to change
        the way music is generated
        
        
        ''')
    
    while not stopE.is_set():
        ask_input(inputQ, stopE)
        sleep(1)
    
    generatorP.join()
    playerP.join()
    
    for x in range(4):  
        b = 'Exiting' + '.' * x
        stdout.write('\r' + b)
        sleep(1)

if __name__ == '__main__':
    main()