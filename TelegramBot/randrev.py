import random
import dill

class RandReview:

    def __init__(self, bot):

        try:
            with open("reviewText.txt", "rb") as fp:
                self.reviews = dill.load(fp)
        except FileNotFoundError:
            print("Reviews not found. :(")

    def getRandomReview(self):
        index = random.randint(0, len(self.reviews))
        return self.reviews[index]

