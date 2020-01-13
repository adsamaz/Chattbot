import fasttext
# Skipgram model :¨
import os
model = None


def predict(text):
    a = model.predict(text)
    label, confidence = ("nonsense", a[1][0]) if a[1][0] < 0.6 else (a[0][0], a[1][0])
    return (label, confidence)

model = fasttext.train_supervised(input="fasttext/data.train", epoch=28, lr=1, wordNgrams=4)

test = model.test("fasttext/data.valid")
print("Precision: " + str(test[1]*100) + "%")


model.save_model("fasttext/trained_model.bin")