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
from telegram.ext import Updater, CommandHandler
import logging
import urllib
import http.cookiejar
import configparser

class Bot:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read("config.txt")

        # Create the Updater and pass it your bot's token.
        self.updater = Updater(self.config["DEFAULT"]['apitoken'])
        # Get the dispatcher to register handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler("start", self.standardStart))
        self.dp.add_handler(CommandHandler("help", self.standardHelp))
        # Log all errors
        self.dp.add_error_handler(self.error)

    def standardStart(self, bot, update):
        update.message.reply_text('The best bot in the whole world type "/help" to learn more')

    def standardHelp(self, bot, update):
        update.message.reply_text(self.generateHelp())
        
    def loadPlugins(self):
        self.help = {}
        
        self.plugins = []
        try:
            for i in __import__('plugins').__all__:
                try:
                    plugin = __import__('plugins.%s' % i, fromlist=[None])
                    try:
                        config = self.config["plugins.%s" % i]
                        print("config!!")
                    except KeyError:
                        config = []

                    if "mainclass" in dir(plugin):
                        print("Loading", i)
                        obj = plugin.mainclass(self, config)
                        self.plugins.append(obj)
                except:
                    traceback.print_exc()
        except:
            traceback.print_exc()

    def registerCommand(self,name,help,func,args = False, user_data=False):
        self.dp.add_handler(CommandHandler(name, func, pass_args=args, pass_user_data=user_data))
        self.help[name] = help
    
    def generateHelp(self):
        hStr = ""
        for key in self.help:
            hStr = hStr + str(key) + " - " + self.help[key] + "\n"
        return hStr
    
    def error(self,bot, update, error):
        self.logger.warn('Update "%s"\n caused error "%s"' % (update, error))

    def run(self):
        print ("telegram bot is running")
        print (self.generateHelp())
        self.updater.start_polling()
        #ctrl-c to quit 
        self.updater.idle()

def main():
    b = Bot()

    b.loadPlugins()
    b.run()
    return 1

if __name__ == '__main__':
    main()

