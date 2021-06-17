import music21
import multiprocessing
import create_midi as streamer

vocab_file = 'data/vocab.txt'
vocab_iter = open(vocab_file, 'r+').read().split()
vocab = { 'itos': {}, 'stoi': {} }
vocab['itos'] = { i: x for i, x in enumerate(vocab_iter) }

def play_with_input(resultQ, stopE):
    while not stopE.is_set():
        i, notes = 0, []
        while not resultQ.empty() and i < 100:
            notes.append(resultQ.get_nowait())
            i += 1
        
        notes = [vocab['itos'][token] for token in notes if vocab['itos'].get(token) is not None]
        notes = ' '.join(notes)
        stream = streamer.txt_to_stream(notes)
        player = music21.midi.realtime.StreamPlayer(stream)
        player.play()