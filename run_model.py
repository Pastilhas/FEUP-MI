import numpy
import multiprocessing as mp
import random
import torch
from tqdm import tqdm
from time import sleep
from consts import *

GEN_TOKENS = 20000  # 20000 tokens => 18 minutes
GEN_TOKENS_WITH_INPUT = 1600000

with open(tests_file, 'r+') as rfile: data = rfile.read().split()
init_prompt = [vocab['stoi'][token] for token in data if vocab['stoi'].get(token) is not None]
max_size = len(init_prompt) - input_size - 1

def new_model(model_savefile, device, input_size):
  model = torch.load(model_savefile).to(device)
  model.eval()
  statH, statC = model.init_state(input_size)
  return model, statH, statC

def new_prompt(init_prompt, input_size, max_size):
  prompt_i = random.randint(0, max_size)
  prompt = init_prompt[prompt_i:prompt_i+input_size]
  return prompt

model, statH, statC = new_model(model_savefile, device, input_size)
prompt = new_prompt(init_prompt, input_size, max_size)
print('Loaded model')

final = prompt
prev_output, i = 0, 0


def run():
  with torch.no_grad(), tqdm(total=GEN_TOKENS) as pbar:
    while i < GEN_TOKENS:
      X = torch.tensor([prompt]).to(device)
      output, (statH, statC) = model(X, (statH, statC))
      statH, statC = model.init_state(input_size)

      (values, indices) = torch.max(output, 1)
      (kvalues, kindices) = torch.topk(values, 20)
      output = numpy.random.choice(numpy.array(kindices.tolist()[0]))

      if output != prev_output:
        prompt = prompt[1:] + [output]
        final += [output]
        prev_output = output
        i += 1
        pbar.update(i)

      else:
        prompt = new_prompt(init_prompt, input_size, max_size)
        final += prompt
        prev_output = prompt[-1]
        i += len(prompt)
        pbar.update(len(prompt))

last_input, last_input_id = None, None
def run_with_input(inputQ, resultQ, stopE):
  with torch.no_grad(), tqdm(total=GEN_TOKENS_WITH_INPUT) as pbar:
    while not stopE.is_set():
      if not inputQ.empty():
        last_input = inputQ.get()
        last_input_id = vocab['stoi'].get(last_input)
      
      if last_input_id is not None:
        prompt[0] = last_input_id
      X = torch.tensor([prompt]).to(device)
      output, (statH, statC) = model(X, (statH, statC))
      statH, statC = model.init_state(input_size)

      (values, indices) = torch.max(output, 1)
      (kvalues, kindices) = torch.topk(values, 20)
      output = numpy.random.choice(numpy.array(kindices.tolist()[0]))

      if output != prev_output:
        prompt = prompt[1:] + [output]
        final += [output]
        prev_output = output
        i += 1
        pbar.update(i)
        if not resultQ.full():
          resultQ.put_nowait(output)

      else:
        prompt = new_prompt(init_prompt, input_size, max_size)
        final += prompt
        prev_output = prompt[-1]
        i += len(prompt)
        pbar.update(len(prompt))
        for x in prompt:
          if not resultQ.full():
            resultQ.put_nowait(x)
            
      # If full wait
      while resultQ.full():
        sleep(20)
      

if __name__ == '__main__':
  run()
  print('Output generated')
  final = [vocab['itos'][token] for token in final if vocab['itos'].get(token) is not None]
  with open(output_file, 'w+') as wfile: wfile.write(' '.join(final))
  print('Output written')
