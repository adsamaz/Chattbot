import fasttext
# Skipgram model :¨
import os

model = fasttext.train_supervised(input="fasttext/data.train", epoch=40, lr=1, wordNgrams=3)
def predict(text):
    a = model.predict(text)
    label, confidence = ("nonsense", a[1][0]) if a[1][0] < 0.6 else (a[0][0], a[1][0])
    return (label, confidence)
    
print(predict("I want to leave a review"))

print(predict("hello!"))

print(predict("Im I a robot?"))

print(model.predict("Give me some information about a game"))

test = model.test("fasttext/data.valid")
print("Precision: " + str(test[1]*100) + "%")

model.save_model("fasttext/trained_model.bin")