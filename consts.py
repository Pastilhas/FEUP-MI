import io
import os
import math
import time
import numpy
from collections import Counter

import torch
import torch.nn as nn
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import Vocab

model_savefile = 'model/best_model.pth'
vocab_file = 'data/vocab.txt'
train_file = 'data/train_data.txt'
tests_file = 'data/test_data.txt'
output_file = 'data/output_txt/out.txt'
txt_input = 'data/input_txt'

num_epochs = 9
input_size = 200
lr = 0.01

best_loss = float("inf")
best_model = None

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

################################################################################

class RNN(nn.ModuleList):
    def __init__(self, input_size, vocab_size):
        super(RNN, self).__init__()
        self.lstm_size = input_size
        self.embedding_dim = input_size
        self.num_layers = 3

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=self.embedding_dim,
        )
        self.lstm = nn.LSTM(
            input_size=self.lstm_size,
            hidden_size=self.lstm_size,
            num_layers=self.num_layers,
            dropout=0.2,
        )
        self.fc = nn.Linear(self.lstm_size, vocab_size)

    def forward(self, x, prev_state):
        embed = self.embedding(x)
        output, state = self.lstm(embed, prev_state)
        logits = self.fc(output)
        return logits, state

    def init_state(self, sequence_length):
        return (torch.zeros(self.num_layers, sequence_length, self.lstm_size).to(device),
                torch.zeros(self.num_layers, sequence_length, self.lstm_size).to(device))

def data_process(data):
  X, Y = [], []
  for i in range(0, len(data) - input_size - 1, int(input_size / 4)):
    X.append(data[i:i+input_size])
    y_ = [0] * vocab_size
    y_[data[i+input_size]] = 1
    Y.append(y_)
  return X, Y

def get_batch(trainX, trainY, n):
  X, Y = trainX[n], trainY[n]
  X = torch.tensor([X]).to(device)
  Y = torch.tensor([Y]).to(device)
  return X, Y

################################################################################

vocab_iter = open(vocab_file, 'r+').read().split()
vocab = { 'itos': {}, 'stoi': {} }
vocab['itos'] = { i: x for i, x in enumerate(vocab_iter) }
vocab['stoi'] = { x: i for i, x in enumerate(vocab_iter) }
vocab_size = len(vocab['itos'])

print('import consts')
