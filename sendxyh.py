import pandas as pd
import pandas_datareader.data as web
import datetime

from telegram import Bot
import mysystemd
import os
import getopt
import sys
import config

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

    bot = Bot(token = CONFIG['Token'])


grand_target = [["hd", 1, 3, 5], ["goev", 7, 9], ["opra", 2, 4, 6, 8, 10]]
admin_grou1 = "-1001448969389"
admin_group = "-1001478922081"

def ticker_string (target:list): #返回单个ticker的当日价和周期价string
    symbol = target[0]

    end = datetime.date.today()
    start = end - datetime.timedelta(days=365)
    df = web.DataReader(symbol.upper(), 'stooq', start=start, end=end)

    today_close = df.iat[0,3]
    today_low = df.iat[0,2]
    today_high = df.iat[0,1]

    result_str = f"{symbol.upper()}价格: {today_close}({today_low} - {today_high}) \n"
    
    for i in target [1:]:
        result_str += get_average(df, i)

    result_str += "\n"
    return result_str

def get_average (df, length): #传入目标ticker的DataFrame和周期，返回周群均价String
    avg_str = f"{length}日均价: "

    df_close = df["Close"]
    df_length = df_close.head(length)
    avg_numb = df_length.mean()
    avg_str += f"{avg_numb:0.2f} \n"
    
    return avg_str

final_str = "🌈🌈🌈当日天相🌈🌈🌈: \n"

for i in grand_target:
    final_str += ticker_string(i)

#bot.send_message(admin_group, f"目标string: {grand_target}")
bot.send_message(admin_group, final_str)
