from consts import *

if os.path.isfile(model_savefile):
  model = torch.load(model_savefile).to(device)
else:
  model = RNN(input_size, vocab_size).to(device)

with open(train_file, 'r+') as rfile: train_iter = rfile.read().split()
with open(tests_file, 'r+') as rfile: tests_iter = rfile.read().split()

train_iter = [vocab['stoi'][token] for token in train_iter if vocab['stoi'].get(token) is not None]
tests_iter = [vocab['stoi'][token] for token in tests_iter if vocab['stoi'].get(token) is not None]

trainX, trainY = data_process(train_iter)
testsX, testsY = data_process(tests_iter)

print('| training batches {:5d} |'.format(len(trainX)))
print('| training batches {:5d} |'.format(len(testsX)))

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=lr)

def train(model, trainX, trainY):
  model.train()
  statH, statC = model.init_state(input_size)
  best_train_loss = float("inf")

  for i in range(len(trainX)):
    X, Y = get_batch(trainX, trainY, i)
    optimizer.zero_grad()
    output, (statH, statC) = model(X, (statH, statC))

    loss = criterion(output, Y)
    if loss < best_train_loss:
      best_train_loss = loss
    statH, statC = statH.detach(), statC.detach()

    loss.backward()
    optimizer.step()

    if i % 500 == 0 and i > 0: 
      print('| epoch {:3d} | {:5d}/{:5d} batches |'
        ' loss {:3f} |'.format(epoch, i, len(trainX), loss))

  return best_train_loss

# Train the model
for epoch in range(num_epochs):
  last_loss = train(model, trainX, trainY)
  if last_loss < best_loss:
    best_loss, best_model = last_loss, model
  print('| epoch {:3d}/{:3d} |'
    ' loss {:3f} |'.format(epoch, num_epochs, last_loss))

# Save best
torch.save(best_model, model_savefile)
