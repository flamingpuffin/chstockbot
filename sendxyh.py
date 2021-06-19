import pandas as pd
import pandas_datareader.data as pdr
import datetime

from telegram import Bot
import mysystemd
import os
import getopt
import sys
import config

grand_target = [["spy", 10, 50, 200], ["qqq", 13, 55, 200], ["rblx", 13, 55, 200]]
admin_group = "-1001448969389"
receiver_group = "-1001478922081"
ds = "stooq"
end = datetime.date.today()
start = end - datetime.timedelta(days=365)
first_ticker = grand_target[0][0]

def help():
    return "'bot.py -c <configpath>'"

def date_check (ds:str, today:datetime, test_symbol:str, start, end) -> bool: #检查第一个ticker的最新数据时间是否和今天为同一天，返回Bool
    if ds == "stooq":
        df = pdr.DataReader(test_symbol.upper(), 'stooq', start=start, end=end)
        index_value = df.index
        if index_value[0] == today:
            return True
        else:
            return False
    elif ds == "yahoo":
        df = pdr.get_data_yahoo(test_symbol.upper(), start=start, end=end)
        index_value = df.index
        if index_value[-1] == today:
            return True
        else:
            return False
    else:
        return False
    

def ticker_string_stooq (target:list, end, start) -> int: #用stooq返回单个ticker的当日价和周期价string
    symbol = target[0]
    df = pdr.DataReader(symbol.upper(), 'stooq', start=start, end=end)
    today_close = df["Close"][0]
    today_low = df["Low"][0]
    today_high = df["High"][0]

    result_str = f"{symbol.upper()}价格: {today_close:0.2f}({today_low:0.2f} - {today_high:0.2f}) \n"
    
    for i in target [1:]:
        result_str += get_average_stooq(df, i, today_close)

    result_str += "\n"
    return result_str

def get_average_stooq (df, length, today_price): #stooq用 传入目标ticker的DataFrame,周期,当日价格,返回周群均价String
    df_close = df["Close"]

    if df_close.count() >= length:
        df_length = df_close.head(length)
        avg_numb = df_length.mean()
        if today_price > avg_numb:
            return f"🟢{length}日均价: {avg_numb:0.2f}\n"
        else:
            return f"🔴{length}日均价: {avg_numb:0.2f}\n"
    else:
        return f"🔴{length}日均价: 历史数据不足{length}天\n"

def ticker_string_yahoo (target:list, end, start): #用yahoo返回单个ticker的当日价和周期价string
    symbol = target[0]
    df = pdr.get_data_yahoo(symbol.upper(), start=start, end=end)
    today_close = df["Adj Close"][-1]
    today_low = df["Low"][-1]
    today_high = df["High"][-1]

    result_str = f"{symbol.upper()}价格: {today_close:0.2f}({today_low:0.2f} - {today_high:0.2f}) \n"
    
    for i in target [1:]:
        result_str += get_average_yahoo(df, i, today_close)

    result_str += "\n"
    return result_str

def get_average_yahoo (df, length, today_price): #yahoo用 传入目标ticker的DataFrame,周期,当日价格,返回周群均价String
    df_close = df["Adj Close"]
    if df_close.count() >= length:
        df_length = df_close.tail(length)
        avg_numb = df_length.mean()
        if today_price  > avg_numb:
            return f"🟢{length}日均价: {avg_numb:0.2f}\n"
        else:
            return f"🔴{length}日均价: {avg_numb:0.2f}\n"
    else:
        return f"🔴{length}日均价: 历史数据不足{length}天\n"


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

    try:
        if date_check(ds=ds, today=end, test_symbol=first_ticker, start=start, end=end) == True:
            bot = Bot(token = CONFIG['Token'])
            final_str = "🌈🌈🌈当日天相🌈🌈🌈: \n"
            if ds == 'stooq':
                for i in grand_target:
                    final_str += ticker_string_stooq(i, end, start)
            elif ds == 'yahoo':
                for i in grand_target:
                    final_str += ticker_string_yahoo(i, end, start)

            bot.send_message(receiver_group, f"目标string: {grand_target} \n数据系统:{ds}")
            bot.send_message(receiver_group, final_str)
    except Exception as err:
#        print(err)
        bot.send_message(admin_group,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了\n出的问题是:\n{type(err)}:\n{err}")