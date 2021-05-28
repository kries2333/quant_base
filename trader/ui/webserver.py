"""
web服务接口，提供websocket的Api接口，界面的数据全部来自这里
"""
import json
import time

import numpy as np
from websocket_server import WebsocketServer

from app.cta_strategy.ui.widget import CtaManager
from event.engine import EventEngine
from trader.engine import MainEngine
from trader.ui.widget import OrderMonitor


class WebServer():

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        order_widget = OrderMonitor(main_engine, event_engine)

    def Start(self):
        server = WebsocketServer(8081, host='127.0.0.1')
        server.set_fn_new_client(self.onOpen)
        server.set_fn_message_received(self.onMessage)
        server.run_forever()

    # Websocket服务端启动
    def onOpen(self, client, server):
        print("有个新用户连接")
        # 如果有连接进来创建实盘管理CTAManage
        self.ctaManage = CtaManager(client, server, self.main_engine, self.event_engine)

    def onMessage(self, client, server, message):
        print(message)
        if message == "start":
            print("")
        if message == "start":
            self.server = server
            self.ctaManage.start_backtesting()
        if message == "add_strategy":
            self.add_strategy()
        elif message == "init_strategy":
            self.ctaManage.init_all_strategies()
        elif message == "start_strategy":
            self.ctaManage.start_all_strategies()
        elif message == "show_candle_chart":
            self.server = server
            self.show_candle_chart()

    def add_strategy(self):
        class_name = "DemoStrategy"
        strategy_name = "Test"
        vt_symbol = "btcusdt.BINANCE"
        setting = {'class_name': class_name, 'n': 10}

        self.ctaManage.add_strategy(class_name, strategy_name, vt_symbol, setting)
