import time
from datetime import datetime

from data_manager.engine import ManagerEngine
from event.engine import EventEngine
from gateway.binance_gateway import BinanceGateway, Exchange
from trader.database import DB_TZ
from trader.engine import MainEngine

binances_setting = {
    "key": "j4MI0GEdLGS6Aa6MlhuuBZqtGJBbSQRTVQuBKC9enPtGEGfol67jMFIi9Hkudno4",  # 信息保密隐藏了
    "secret": "gWSDCYJxQQKo174FEHvxTkzTcxFyzK4mlqXa3s13yslttRrZfkHnWgDoDNndZB1R", #信息保密隐藏了
    "session_number": 3,
    "服务器": ["REAL"],
    "合约模式": ["正向"],
    "proxy_host": "",
    "proxy_port": "", #信息保密隐藏了
    }

def loop_downdata(manage_engine, symbol):
    exchange = Exchange.BINANCE
    interval = "1m"

    start = datetime(2018, 1, 1)
    start = DB_TZ.localize(start)

    time.sleep(5)

    count = manage_engine.download_bar_data(symbol, exchange, interval, start)
    print("完成 {} = {}条数据".format(symbol, count))

def main():

    try:
        event_engine = EventEngine()
        main_engine = MainEngine(event_engine)
        main_engine.add_gateway(BinanceGateway)
        loop_downdata(main_engine, 'btcusdt.BINANCE')
        print("全部完成")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()