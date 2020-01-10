# -*- coding: utf-8 -*-
"""chatbot.ipynb

Original file is located at
    https://colab.research.google.com/github/adsamaz/Chattbot/blob/master/chatbot.ipynb
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import gensim
import gzip
import dill
from gensim.models import KeyedVectors

device = torch.device("cpu")

class SentimentNet(nn.Module):
    def __init__(self, vocab_size, output_size, embedding_dim, hidden_dim, n_layers, drop_prob=0.5):
        super(SentimentNet, self).__init__()
        self.output_size = output_size
        self.n_layers = n_layers
        self.hidden_dim = hidden_dim

        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, n_layers, dropout=drop_prob, batch_first=True)
        self.dropout = nn.Dropout(drop_prob)
        self.fc = nn.Linear(hidden_dim, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, hidden):
        batch_size = x.size(0)
        x = x.long()
        embeds = self.embedding(x)
        lstm_out, hidden = self.lstm(embeds, hidden)
        lstm_out = lstm_out.contiguous().view(-1, self.hidden_dim)

        out = self.dropout(lstm_out)
        out = self.fc(out)
        out = self.sigmoid(out)

        out = out.view(batch_size, -1)
        out = out[:,-1]
        return out, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        hidden = (weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(device),
                      weight.new(self.n_layers, batch_size, self.hidden_dim).zero_().to(device))
        return hidden

class Score:

    def __init__(self, bot, _):
        bot.registerCommand(
            "score", "Positivity score of word or phrase.", self.handleScore, True
        )

        try:
            with open("vocab_to_int.txt", "rb") as fp:
                self.vocab_to_int = dill.load(fp)
        except FileNotFoundError:
            return

        vocab_size = len(self.vocab_to_int) + 1
        output_size = 1
        embedding_dim = 400
        hidden_dim = 256
        n_layers = 2

        self.model = SentimentNet(vocab_size, output_size, embedding_dim, hidden_dim, n_layers)
        self.model.to(device)

        # Loading the best model
        self.model.load_state_dict(torch.load('./state_dict.pt', map_location=torch.device('cpu')))
        self.model.eval()

    def handleScore(self, bot, update, args):
        test_string = " ".join(args)
        test_input =[]
        test_input.append(test_string)
        test_int = []
        for test_temp in test_input:
            r = [self.vocab_to_int[w] for w in test_temp.split()]
            test_int.append(r)

        h = self.model.init_hidden(1)

        print(test_int)
        features = np.array(self.pad_features(test_int,200))

        features = torch.from_numpy(features)

        h = tuple([each.data for each in h])
        inputs = features.to(device)
        output, h = self.model(inputs, h)

        update.message.reply_text("Positivity score of %s is %f." % (test_string, output))
        return None


    # Fucntion which zero padds and shortens all reviews to seq_length

    def pad_features(self, reviews_int, seq_length):
        ''' Return features of review_ints, where each review is padded with 0's or truncated to the input seq_length.
        '''
        features = np.zeros((len(reviews_int), seq_length), dtype = int)

        for i, review in enumerate(reviews_int):
            review_len = len(review)

            if review_len <= seq_length:
                zeroes = list(np.zeros(seq_length-review_len))
                new = zeroes+review
            elif review_len > seq_length:
                new = review[0:seq_length]

            features[i,:] = np.array(new)

        return features

mainclass = Score

