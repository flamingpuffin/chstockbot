from telegram.ext import Updater
import mysystemd
import os
import getopt
import sys
import config


import pandas as pd
import pandas_datareader as pdr
import datetime


def help():
    return "'bot.py -c <configpath>'"


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    updater = Updater(CONFIG['Token'], use_context=True)
    dispatcher = updater.dispatcher

    me = updater.bot.get_me()
    CONFIG['ID'] = me.id
    CONFIG['Username'] = '@' + me.username
    config.set_default()
    print(f"Starting... ID: {str(CONFIG['ID'])} , Username: {CONFIG['Username']}")

    commands = []
    from cmdproc import groupcmd
    commands += groupcmd.add_dispatcher(dispatcher)
    from cmdproc import reportcmd
    commands += reportcmd.add_dispatcher(dispatcher)
    from cmdproc import sendxyh
    commands += sendxyh.add_dispatcher(dispatcher)

    updater.bot.set_my_commands(commands)


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

    print(df)

    response_text = f"""
    当日行情：
    {symbol}价格: {string_today_close} ({string_today_low} - {string_today_high})
    13日均价: {string_13}
    50日均价: {string_50}
    """

    updater.bot.send_message(admingroup, response_text)


    updater.start_polling()
    print('Started...')
    mysystemd.ready()

    updater.idle()
    print('Stopping...')
    print('Stopped.')