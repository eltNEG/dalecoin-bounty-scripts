import os
from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.ext import Dispatcher

from time import sleep #avoid flood limit


def bot_instance():
    """Create Bot instance"""
    return Bot(os.environ.get('BOT_TOKEN'))

def Setup(bot):
    sleep(5)
    #create bot, update queue and dispatcher instances
    #bot = bot_instance()
    bot.set_webhook(os.environ.get('PUBLIC_URL') + '/tele')
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue)
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    return (update_queue, dispatcher)