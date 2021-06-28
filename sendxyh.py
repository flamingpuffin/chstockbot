import sendxyh

import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
import pandas as pd
import urllib3.exceptions

config.config_file = os.path.join(config.config_path, "config.json")
CONFIG = config.load_config()

bot = Bot(token = CONFIG['Token'])
symbols = CONFIG['xyhticker']
notifychat = CONFIG['xyhchat']
adminchat = CONFIG['xyhlog']
debug = CONFIG['DEBUG']
ds = CONFIG['xyhsource']

def get_ticker_data (datasources:list, symbol:str, end=datetime.date.today()): 
    start = end - datetime.timedelta(days=365)
    result_df = pd.DataFrame()
    error_msg = ""
    for i in datasources:
        try:
            result_df = web.DataReader(symbol.upper(), i, start=start, end=end)
            break
        except ConnectionError as e:
            error_msg += f"在从{i}中抽取{symbol}数据时出现了网络错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except ConnectionRefusedError as e:
            error_msg += f"在从{i}中抽取{symbol}数据时出现了网络错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except urllib3.exceptions.NewConnectionError as e:
            error_msg += f"在从{i}中抽取{symbol}数据时出现了网络错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except urllib3.exceptions.MaxRetryError as e:
            error_msg += f"在从{i}中抽取{symbol}数据时出现了网络错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except NotImplementedError as e: #一个数据源不支持，试着下一个
            error_msg += f"在从{i}中抽取{symbol}数据时出现了DataReader数据源不支持错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except KeyError as e: #数据源找到了但是没有找到ticker或者网络不好
            error_msg += f"在从{i}中抽取{symbol}数据时未找到该ticker, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except RemoteDataError as e: #数据源找到了但是没有找到ticker或者网络不好
            error_msg += f"在从{i}中抽取{symbol}数据时未找到该ticker, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
        except Exception as e:
            error_msg += f"在从{i}中抽取{symbol}出现了未知错误, 具体问题是：\n{type(e)}:\n{e}\n\n"
            continue
    if result_df.empty: #因为stooq如果没能成功找到ticker并不会报exception，而是会返回一个空的DataFrame，所以要检查DataFrame是否为空
        error_msg += f"尝试各种数据源后都未能抽取到ticker:{symbol}的数据！\n\n" 
    return [error_msg, result_df]
  
def date_check (df, checkday:datetime) -> bool: #检查ticker的最新数据时间是否和今天为同一天，返回Bool
    checkday = datetime.datetime(2021, 6, 25) #测试用
    index_value = df.index
    if index_value[-1] == checkday:
        return True
    else:
        return False

def cal_symbols_avg(datasources, target:list, end=datetime.date.today()):
    symbol = target[0]
    cal_period = target[1:]
    df_list = get_ticker_data(datasources, symbol, end)
    error_msg = df_list[0]
    result_df = df_list[1]
    notify_msg = ""

    if result_df.empty == False: #抓取到了数据
        result_df = result_df.sort_values(by="Date") #把数据按日期排列
        if date_check(result_df, datetime.date.today()): #检查最新数据是否为当日
            notify_msg += ticker_string (result_df, symbol, cal_period)
        else:
            error_msg += f"今天没有{symbol}的最新数据，不发送{symbol}的均价信息\n\n"

    return [error_msg, notify_msg]

def ticker_string (df, symbol, avgs): #返回单个ticker的当日价和周期价string
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


def get_average_price (df, length, today_price): #传入目标ticker的DataFrame,周期,当日价格,返回周期均价String
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
        return f"✖️{length}日均价: 历史数据不足{length}天\n"

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

    final_admin_str=""
    final_notify_str = ""

    try:
        for i in symbols:
            cal_symbol_result = cal_symbols_avg(ds, i, end)
            final_admin_str += cal_symbol_result[0]
            final_notify_str += cal_symbol_result[1]
        if final_notify_str:
            send_str = "🌈🌈🌈当日天相🌈🌈🌈: \n" + final_notify_str
            if debug :
                print(f"{notifychat}\n{send_str}")
            else:
                bot.send_message(notifychat,send_str)
        if final_admin_str:
            if debug :
                print(f"{adminchat}\n{final_admin_str}")
            else:
                bot.send_message(adminchat,final_admin_str)
    except Exception as e:
            if debug:
                print(f"{adminchat}\n今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(e)}:\n{e}")
            else:
                bot.send_message(adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(e)}:\n{e}")

