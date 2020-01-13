#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

import re
import traceback
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import urllib
import http.cookiejar
import configparser
import fasttext
import sentiment as snet
import randrev as rr 

class Bot:

    reviewMode = False

    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read("config.txt")

        self.model = fasttext.load_model("../fasttext/trained_model.bin")

        # Create the Updater and pass it your bot's token.
        self.updater = Updater(self.config["DEFAULT"]['apitoken'])
        # Get the dispatcher to register handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler("start", self.standardStart))
        self.dp.add_handler(CommandHandler("help", self.standardHelp))
        self.dp.add_handler(CommandHandler("score", self.commandScore, pass_args=True))
        self.dp.add_handler(MessageHandler(Filters.text, self.messageCheck))
        # Log all errors
        self.dp.add_error_handler(self.error)

        # Init neural network
        self.nn = snet.Score(self)

        # Init random review
        self.rr = rr.RandReview(self)

    def standardStart(self, bot, update):
        update.message.reply_text('The best bot in the whole world type "/help" to learn more')

    def standardHelp(self, bot, update):
        update.message.reply_text('Say hello (if you want), then leave a review, or get a random review by simply telling me what you want to do.')
        
    def registerCommand(self,name,help,func,args = False, user_data=False):
        self.dp.add_handler(CommandHandler(name, func, pass_args=args, pass_user_data=user_data))
        # self.help[name] = help
    
    def commandScore(self, bot, update, args):
        self.nn.handleScore(self.nn, update, args)
    
    def predict(self, text):
        a = self.model.predict(text)
        label, confidence = ("__label__nonsense", a[1][0]) if a[1][0] < 0.6 else (a[0][0], a[1][0])
        return (label, confidence)

    def messageCheck(self, bot, update):
        inMessage = update.message.text.lower()
        if (self.reviewMode):
            score = self.nn.messageScore(self.nn, inMessage)
            print(score[0])
            if (score[0] > 0.75):
                update.message.reply_text('Glad you liked it!')
            elif (score[0] > 0.3):
                update.message.reply_text('Thank you for the review! We will keep improving!')
            else:
                update.message.reply_text('Sorry you did not like it. We will do better next time!')
            self.reviewMode = False
            return
        label, confidence = self.predict(inMessage)
        if ('hi' in label):
            update.message.reply_text('Hi! I am Chatbot Eta. I love video game reviews.')
        elif ('info' in label):
            update.message.reply_text('Here is a random review for you!')
            update.message.reply_text(self.rr.getRandomReview())
        elif ('review' in label):
            update.message.reply_text('Okay, please write your review.')
            self.reviewMode = True
        else:
            update.message.reply_text('Sorry, I do not understand that. Please try again.')
    
    def error(self, bot, update, error):
        self.logger.warn('Update "%s"\n caused error "%s"' % (update, error))

    def run(self):
        print ("telegram bot is running")
        self.updater.start_polling()
        ## ctrl-c to quit 
        self.updater.idle()

def main():
    b = Bot()

    b.run()
    return 1

if __name__ == '__main__':
    main()

