import json

from app.cta_strategy.base import EVENT_CTA_STRATEGY
from event.engine import EventEngine
from trader.engine import MainEngine

from app.cta_strategy import CtaEngine, APP_NAME
from trader.utility import SEncoder


class CtaManager:
    def __init__(self, client, server, main_engine: MainEngine, event_engine: EventEngine):
        super(CtaManager, self).__init__()

        self.client = client
        self.server = server
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.cta_engine = main_engine.get_engine(APP_NAME)

        self.managers = {}

        self.register_event()
        self.cta_engine.init_engine()

    def register_event(self):
        self.event_engine.register(EVENT_CTA_STRATEGY, self.process_strategy_event)

    def process_strategy_event(self, event):
        """
        Update strategy status onto its monitor.
        """
        data = event.data
        strategy_name = data["strategy_name"]

        if strategy_name in self.managers:
            manager = self.managers[strategy_name]
            manager.update_data(data)
        else:
            manager = StrategyManager(self, self.cta_engine, data)
            self.managers[strategy_name] = manager

    def init_all_strategies(self):
        self.cta_engine.init_all_strategies()

    def start_all_strategies(self):
        self.cta_engine.start_all_strategies()

    def add_strategy(self, class_name, strategy_name, vt_symbol, setting):
        self.cta_engine.add_strategy(class_name, strategy_name, vt_symbol, setting)


class StrategyManager:
    def __init__(self, cta_manager: CtaManager, cta_engine: CtaEngine, data: dict):
        """"""
        super(StrategyManager, self).__init__()
        self.cta_manager = cta_manager
        self.cta_engine = cta_engine

        self.strategy_name = data["strategy_name"]
        self._data = data

    def update_data(self, data: dict):
        self._data = data

        # self.parameters_monitor.update_data(data["parameters"])
        # self.variables_monitor.update_data(data["variables"])

        # Update button status
        variables = data["variables"]
        inited = variables["inited"]
        trading = variables["trading"]
        # df = variables['dataframe']

        if not inited:
            return

        data = {'update_data': data}
        json_str = json.dumps(data, cls=SEncoder)
        sever = self.cta_manager.server
        client = self.cta_manager.client
        sever.send_message(client, json_str)

    def start_strategy(self):
        """"""
        self.cta_engine.start_strategy(self.strategy_name)