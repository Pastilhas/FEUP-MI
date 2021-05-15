import os

vocab_file = 'data/vocab.txt'
train_file = 'data/train_data.txt'
tests_file = 'data/test_data.txt'
txt_input = 'data/input_txt'

train_string, tests_string = [], []
vocab = set()

for file in os.scandir(txt_input):
  if file.is_file() and file.name.lower().endswith('.txt'):
    print(file.path)

    with open(file.path, 'r+') as in_file: data = in_file.read().split()
    data = [token for token in data if isinstance(token, str) and token != 'end' and token != '']
    
    vocab.update(data)
    if len(train_string) < len(tests_string):
      train_string += data
    else:
      tests_string += data

print('Read all files')

with open(train_file, 'w+') as train_data: train_data.write(' '.join(train_string))
with open(tests_file, 'w+') as tests_data: tests_data.write(' '.join(tests_string))
with open(vocab_file, 'w+') as vocab_data: vocab_data.write(' '.join(vocab))
