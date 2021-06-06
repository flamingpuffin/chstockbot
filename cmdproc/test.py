import pandas as pd
import pandas_datareader as pdr
import datetime

from telegram import Update, ForceReply, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

admingroup = "-1001448969389"

start = datetime.datetime(2021,1,1)
end = datetime.date.today()
symbol='spy'
df = pdr.get_data_yahoo(symbol.upper(), start=start, end=end)

df_close = df["Adj Close"]  
df_high = df["High"]
df_low = df["Low"]

df_13 = df_close.tail(13)
df_50 = df_close.tail(50)

string_today_high = f"{df_high.tail().mean():0.2f}"
string_today_low = f"{df_low.tail().mean():0.2f}"
string_today_close = f"{df_close.tail().mean():0.2f}"

average_13 = df_13.mean()
string_13 = f"{average_13:0.2f}"

average_50 = df_50.mean()
string_50 = f"{average_50:0.2f}"

response_text = f"""
当日行情：
{symbol}价格: {string_today_close} ({string_today_low} - {string_today_high})
13日均价: {string_13}
50日均价: {string_50}
"""

