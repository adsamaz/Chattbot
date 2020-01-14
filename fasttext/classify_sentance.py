import fasttext

model = fasttext.load_model("fasttext/trained_model.bin")

def predict(text):
    a = model.predict(text)
    label, confidence = ("nonsense", a[1][0]) if a[1][0] < 0.6 else (a[0][0], a[1][0])
    return (label, confidence)

print(predict("can I read a review"))
