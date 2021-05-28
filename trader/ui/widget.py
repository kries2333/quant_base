from typing import Dict, Any

from event.engine import EventEngine, Event
from trader.engine import MainEngine
from trader.event import EVENT_ORDER


class BaseMonitor:
    """
    Monitor data update in VN Trader.
    """

    event_type: str = ""
    data_key: str = ""
    sorting: bool = False
    headers: Dict[str, dict] = {}
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super(BaseMonitor, self).__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.cells: Dict[str, dict] = {}

        self.register_event()

    def register_event(self) -> None:
        if self.event_type:
            self.event_engine.register(self.event_type, self.process_event)

    def process_event(self, event: Event) -> None:
        data = event.data

        if not self.data_key:
            self.insert_new_row(data)

    def insert_new_row(self, data: Any):
        print("insert_new_row")

class OrderMonitor(BaseMonitor):
    """"""

    event_type = EVENT_ORDER
    data_key = "kt_orderid"

    headers: Dict[str, dict] = {
        "orderid": {"display": "委托号", "update": False},
        # "reference": {"display": "来源", "cell": BaseCell, "update": False},
        # "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        # "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        # "type": {"display": "类型", "cell": EnumCell, "update": False},
        # "direction": {"display": "方向", "cell": DirectionCell, "update": False},
        # "offset": {"display": "开平", "cell": EnumCell, "update": False},
        # "price": {"display": "价格", "cell": BaseCell, "update": False},
        # "volume": {"display": "总数量", "cell": BaseCell, "update": True},
        # "traded": {"display": "已成交", "cell": BaseCell, "update": True},
        # "status": {"display": "状态", "cell": EnumCell, "update": True},
        # "datetime": {"display": "时间", "cell": TimeCell, "update": True},
        # "gateway_name": {"display": "接口", "cell": BaseCell, "update": False},
    }