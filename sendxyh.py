import sendxyh

import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
import pandas as pd

config.config_file = os.path.join(config.config_path, "config.json")
CONFIG = config.load_config()

bot = Bot(token = CONFIG['Token'])
symbols = CONFIG['xyhticker']
notifychat = CONFIG['xyhchat']
adminchat = CONFIG['xyhlog']
debug = CONFIG['DEBUG']
ds = CONFIG['xyhsource']

def check_data_source (ds:list, symbol:str, end=datetime.date.today(), i=0): 
    start = end - datetime.timedelta(days=365)
    error_code = i
    if i < len(ds):
        try:
            df = web.DataReader(symbol.upper(), ds[i], start=start, end=end)
        except NotImplementedError: #一个数据源不支持，试着下一个
            i+=1
            return check_data_source (ds, symbol.upper(), end, i)
        except KeyError: #数据源找到了但是没有找到ticker或者网络不好
            error_code = -1
            df= pd.DataFrame()
            if debug:
                print(f"{adminchat}\n在用{ds[i]}试图抓取{symbol}数据时未成功，建议检查网络连接或ticker是否正确")
            else:
                bot.send_message(adminchat,f"在用{ds[i]}试图抓取{symbol}数据时未成功，建议检查网络连接或ticker是否正确")
            return [error_code, df]    
        except RemoteDataError: #数据源找到了但是没有找到ticker或者网络不好
            error_code = -2
            df= pd.DataFrame()
            if debug:
                print(f"{adminchat}\n在用{ds[i]}试图抓取{symbol}数据时未成功，建议检查网络链接或ticker是否正确")
            else:
                bot.send_message(adminchat,f"在用{ds[i]}试图抓取{symbol}数据时未成功，建议检查网络链接或ticker是否正确")
            return [error_code, df]    
        except: #出现了其他的错误
            error_code = -3
            df= pd.DataFrame()

            if debug:
                print(f"{adminchat}\n今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了")
            else:
                bot.send_message(adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了")
            return [error_code, df]

    else:
        if debug:
            print(f"{adminchat}\n在试图抓取{symbol}数据时未成功：全部数据源都不被支持")
        else:
            bot.send_message(adminchat,f"在试图抓取{symbol}数据时未成功：全部数据源都不被支持")
        df=pd.DataFrame()
        return [error_code, df]
    return [error_code, df]


def date_check (df, today:datetime, test_symbol:str) -> bool: #检查ticker的最新数据时间是否和今天为同一天，返回Bool
    index_value = df.index
    if index_value[-1] == today:
        return True
    else:
        return False

def cal_symbols_avg(ds, target:list, end=datetime.date.today()):
    start = end - datetime.timedelta(days=365)
    symbol = target[0]
    cal_period = target[1:]
    df_list = check_data_source(ds, symbol, end, 0)
    df = df_list[1]
    error_code = df_list[0]
    if error_code >= 0 & error_code < len(ds): #df抓取到了数据
        if error_code > 0:
            if debug:
                print(f"在查询{symbol}时至少一个数据源未被支持")
            else:
                bot.send_message(adminchat,f"在查询{symbol}时至少一个数据源未被支持")
        if df is not None and df.empty  == False:
            df = df.sort_values(by="Date")
            if date_check (df, datetime.date.today(), symbol):
                return ticker_string (df, symbol, cal_period, end, start)
            else:
                return ""
        else:
            return ""
    else:
        return ""

def ticker_string (df, symbol, avgs, end, start): #返回单个ticker的当日价和周期价string
    if "Adj Close" in df.columns:
        today_close = df["Adj Close"][-1]
    else:
        today_close = df["Close"][-1] 
    today_low = df["Low"][-1]
    today_high = df["High"][-1]

    result_str = f"{symbol.upper()}价格: {today_close:0.2f}({today_low:0.2f} - {today_high:0.2f}) \n"
    
    for i in avgs:
        result_str += get_average_price(df, i, today_close)

    result_str += "\n"
    return result_str


def get_average_price (df, length, today_price): #传入目标ticker的DataFrame,周期,当日价格,返回周群均价String
    if "Adj Close" in df.columns:
        df_close = df["Adj Close"]
    else:
        df_close = df["Close"] 
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

    end = datetime.date.today()
    start = end - datetime.timedelta(days=365)

    final_str = ""

    for i in symbols:
        final_str += cal_symbols_avg(ds, i, end)
    if "均价" in final_str:
        send_str = "🌈🌈🌈当日天相🌈🌈🌈: \n" + final_str
        if debug :
            print(f"{notifychat}\n{send_str}")
        else:
            bot.send_message(notifychat,send_str)

    else:
        exit