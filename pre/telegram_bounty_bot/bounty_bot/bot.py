# -*- coding: utf-8 -*-
import os, sys
from threading import Thread
import logging
from random import randint
from time import sleep
from datetime import datetime

from telegram.ext import InlineQueryHandler
from telegram import (InlineQueryResultArticle, InputTextMessageContent)
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Filters
from telegram import ParseMode
from telegram.ext import JobQueue

from telegram import (ReplyKeyboardRemove, ReplyKeyboardMarkup)
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (ConversationHandler) # , RegexHandler)
from telegram.ext import CallbackQueryHandler
from telegram.error import TelegramError, NetworkError, TimedOut

from .settings import Setup, bot_instance

from db import (
    Bounter, db_commit, db
)

from googlesheet.gs_updater import UpdateSheet

CHANNEL_MONITOR = '@dalematbounty'
#BOUNTY_GROUP_ID = -1001243665227
BOUNTY_GROUP_ID = -1001131305306
ADMIN_ID = 171671406

BOT = bot_instance()
update_queue, dispatcher = Setup(BOT)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
job_queue = JobQueue(BOT)
job_queue.start()
dispatcher.job_queue = job_queue

#google_sheet = UpdateSheet('client_secret.json', 'Dalecoin.org', 'Dalc Bounty List')
google_sheet = UpdateSheet('client_secret.json','Dalecoin Bounty', 'telegram')

#=========BOT commands==============================

def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        job_queue.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

def restart(BOT, update):
    update.message.reply_text('BOT is restarting...')
    Thread(target=stop_and_restart).start()

def stop(BOT, update):
    job_queue.stop()


#===========================COMMANDS======================================================================

def start(BOT, update):
    BOT.send_message(chat_id=update.message.chat_id, text="Hello")
     #disable_web_page_preview=True, parse_mode=ParseMode.HTML)    

def handle_callback(BOT, update):
    query = update.callback_query
    data = query.data
    print('callback ==> ' + data)
    update.message.reply_text('Hellooooo')

def handle_new_chat_member(BOT, update):
    if update.message.chat_id != BOUNTY_GROUP_ID:
        return
    telegram_user = telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id

    if len(name) >= 39:
        update.message.reply_text("Your name is too long. You may not be able to participate in this dalecoin bounty program")
        return

    user = Bounter.get_bounter(telegram_id=user_id)
    if user:
        if 'dalecoin.org' in name:
            Bounter.set_is_active_bounter(user_id, True)
            #Bounter.break_point(user_id, update_week=False)
        Bounter.break_point(user_id, update_week=False)
        #BOT.send_message(group_chat_id, "welcome")
        db_commit()
        return

    Bounter.add_bounter(user_id, name, username)
    db_commit()
    #BOT.send_message(group_chat_id, "welcome new user")

def handle_bounty_command(BOT, update):
    """
    if update.message.chat_id != -201473564:
        return
    """
    telegram_user = telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id
    user = Bounter.get_bounter(telegram_id=user_id)
    """
    if user:
        t_diff = datetime.utcnow() - user.last_break_point
        print(t_diff.seconds)
        wks = Bounter.get_wks(user)
        bounty_status = 'active' if user.is_active_bounter else 'Not active'
        if not user.is_active_bounter:
            update.message.reply_text(f'Bounty status: {bounty_status}\nWeeks completed: {user.number_of_weeks_completed}')
            return
        update.message.reply_text(f'Bounty status: {bounty_status}\nWeeks completed: {wks}')
        return
    """
    update.message.reply_text('Bounty has ended. Please check google sheet for bounty report.')


def handle_user_left_chat(BOT, update):
    #if update.message.chat_id != -201473564:
    if update.message.chat_id != BOUNTY_GROUP_ID:
        return
    telegram_user = telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id
    user = Bounter.get_bounter(telegram_id=user_id)

    if user:
        Bounter.break_point(user_id, update_week=True)
        user.is_active_bounter = False
    db_commit()

def handle_user_change_name(BOT, update):
    print(update.message)
    if update.message.chat_id != BOUNTY_GROUP_ID:
        return
    telegram_user = telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id
    user = Bounter.get_bounter(telegram_id=user_id)
    if user:
        if 'dalecoin.org' in name and user.is_active_bounter:
            return
        elif 'dalecoin.org' in name and not user.is_active_bounter:
            user.is_active_bounter = True
            Bounter.break_point(user_id)
        elif user.is_active_bounter and not ('dalecoin.org' in name):
            Bounter.break_point(user_id, update_week=True)
            user.is_active_bounter = False
    elif 'dalecoin.org' in name:
        new_user = Bounter.add_bounter(user_id, name, username)
        new_user.is_active_bounter = True
    else:
        Bounter.add_bounter(user_id, name, username)
    
    db_commit()

def scan_change_name(BOT, job):
    users = Bounter.query.all()
    user_ids = [user.telegram_id for user in users]
    all_users = [BOT.get_chat_member(BOUNTY_GROUP_ID, id) for id in user_ids]
    for user in all_users:
        try:
            name = user.user.full_name
            print(name)
            user_id = user.user.id
            bounter = Bounter.get_bounter(user_id)
            if len(name) >= 39:
                return
            if user.status == 'left':
                if bounter.is_active_bounter:
                    Bounter.break_point(user_id, update_week=True)
                    bounter.is_active_bounter = False
                    db_commit()
                    print(f"{name} is deactivated")
                continue
            if 'dalecoin.org' in name and bounter.is_active_bounter:
                #print(f"{name} is active")
                pass
            elif ('dalecoin.org' not in name) and bounter.is_active_bounter:
                Bounter.break_point(user_id, update_week=True)
                bounter.is_active_bounter = False
                db_commit()
                print(f"{name} is deactivated")
                
            elif 'dalecoin.org' in name and not bounter.is_active_bounter:
                Bounter.break_point(user_id)
                bounter.is_active_bounter = True
                db_commit()
                print(f"{name} is activated")
                
        except AttributeError as identifier:
            name = user.first_name
            print('no name')
    


def handle_start_job(BOT, update, job_queue, chat_data):
    if update.message.from_user.id != ADMIN_ID:
        return
    print(chat_data)

    #if chat_data['job']:
    #    update.reply_text('job already started')
    if 'job' in chat_data:
        update.message.reply_text('job alredy running')
        return

    due = 10
    chat_data['job'] = job_queue.run_repeating(scan_change_name, due)
    update.message.reply_text('job started')


        
#new message handler
def group_message_handler(BOT, update):
    if update.message.chat_id != BOUNTY_GROUP_ID:
        return
    telegram_user = telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id
    user = Bounter.get_bounter(telegram_id=user_id)
    if len(name) >= 39:
        update.message.reply_text("Your name is too long. You may not be able to participate in this dalecoin bounty program")
        return
    if user:
        if 'dalecoin.org' in name and user.is_active_bounter:
            return
        elif 'dalecoin.org' in name and not user.is_active_bounter:
            user.is_active_bounter = True
            Bounter.break_point(user_id)
        elif user.is_active_bounter and not ('dalecoin.org' in name):
            Bounter.break_point(user_id, update_week=True)
            user.is_active_bounter = False
    elif 'dalecoin.org' in name:
        new_user = Bounter.add_bounter(user_id, name, username)
        new_user.is_active_bounter = True
    else:
        Bounter.add_bounter(user_id, name, username)

    db_commit()

def clean_db(BOT, update):
    if update.message.chat_id != ADMIN_ID:
        return
    all_users = Bounter.query.all()
    for user in all_users:
        db.session.delete(user)
    db_commit()
    update.message.reply_text('Users deleted')

def update_google_sheet(BOT, update):
    if update.message.chat_id != ADMIN_ID:
        return

    all_users = Bounter.query.all()
    data_set = []
    n = 1
    for user in all_users:
        if user.is_active_bounter and not user.in_google_sheet:
            user.in_google_sheet = True
            db_commit()
        if not user.in_google_sheet:
            continue
        wks = Bounter.get_wks(user)
        bounty_status = 'active' if user.is_active_bounter else 'Not active'
        address = user.eth_address if user.eth_address else '-'
        name = user.telegram_username if user.telegram_username else "No telegram username"
        user_data = [n, name, wks, bounty_status, address]
        data_set.append(user_data)
        n += 1
    google_sheet.update_sheet(data_set)
    url = google_sheet.get_sheet_url()
    update.message.reply_text('Sheet updated successfully \n{}'.format(url))


def private_message_handler(BOT, update):
    telegram_user = update.message.from_user
    username = telegram_user.username
    name = telegram_user.full_name
    user_id = telegram_user.id
    group_chat_id = update.message.chat_id
    user = Bounter.get_bounter(telegram_id=user_id)
    '''
    if len(name) >= 39:
        update.message.reply_text("Your name is too long. You may not be able to participate in this dalecoin bounty program")
        return
    '''
    if user:
        if 'dalecoin.org' in name and user.is_active_bounter:
            pass
        elif 'dalecoin.org' in name and not user.is_active_bounter:
            user.is_active_bounter = True
            Bounter.break_point(user_id)
        elif user.is_active_bounter and not ('dalecoin.org' in name):
            Bounter.break_point(user_id, update_week=True)
            user.is_active_bounter = False
    elif 'dalecoin.org' in name:
        new_user = Bounter.add_bounter(user_id, name, username)
        new_user.is_active_bounter = True
    else:
        user = Bounter.add_bounter(user_id, name, username)

    address = update.message.text
    if address:
        if len(address.split(' ')) == 1 and address.startswith('0x'):
            user.eth_address = address
            update.message.reply_text('ETH address has been updated successfully')


    db_commit()




def error_callback(BOT, update, error):
    try:
        raise error
    
    except TimedOut as e:
        print("timedout eror ", e)
    except NetworkError as e:
        print("network eror ", e)
    except TelegramError as e:
        print("telegram error ", e)
    except Exception as e:
        print("unknown error ", e)



#register handlers
dispatcher.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@eltNEG')))
dispatcher.add_handler(CommandHandler('stop', stop))
dispatcher.add_handler(CommandHandler('start', start, filters=Filters.private))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))
msg_handler = MessageHandler(Filters.status_update.new_chat_members, handle_new_chat_member)
dispatcher.add_handler(msg_handler)
dispatcher.add_handler(CommandHandler("bounty", handle_bounty_command, filters=Filters.private))
#dispatcher.add_handler(CommandHandler('sj', handle_start_job, filters=Filters.private, pass_job_queue=True, pass_chat_data=True))
#dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_user_left_chat))
#dispatcher.add_handler(MessageHandler(Filters.status_update, handle_user_change_name))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, private_message_handler))
#dispatcher.add_handler(MessageHandler(Filters.text, group_message_handler))
dispatcher.add_handler(CommandHandler('clean', clean_db, filters=Filters.private))
#dispatcher.add_handler(CommandHandler('updatesheet', update_google_sheet, filters=Filters.private))
dispatcher.add_error_handler(error_callback)

def webhook(update):
    update_queue.put(update)