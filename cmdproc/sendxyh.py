import pandas as pd
import pandas_datareader as pdr
import datetime

from telegram import Update, ForceReply, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


admingroup = "-1001448969389"

def send_spy(update: Update, _:CallbackContext):
    start = datetime.datetime(2021,1,1)
    end = datetime.date.today()
    symbol='spy'
    df = pdr.get_data_yahoo(symbol.upper(), start=start, end=end)
    df1 = df["Adj Close"]  
    print(df1)
    df2 = df1.tail(13)
    print(df2)
    update.message.bot.send_message(admingroup, df2.mean())

    average_13 = df2.mean()
    string_13 = f"{average_13:0.2f}"

    print(string_13)    

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("spy", send_spy))
    return [BotCommand('spy','获得SPY价格')]
    