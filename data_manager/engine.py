from datetime import datetime

from event.engine import EventEngine
from trader.constant import Interval, Exchange
from trader.database import DB_TZ, database_manager
from trader.engine import BaseEngine, MainEngine
from trader.object import HistoryRequest

APP_NAME = "DataManager"

class ManagerEngine(BaseEngine):

    def __init__(
            self,
            main_engine: MainEngine,
            event_engine: EventEngine,
    ):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

    def download_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: str,
            start: datetime
        ) -> int:
        """
        Query bar data from RQData.
        """
        req = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            interval=Interval(interval),
            start=start,
            end=datetime.now(DB_TZ)
        )

        vt_symbol = f"{symbol}.{exchange.value}"
        contract = self.main_engine.get_contract(vt_symbol)

        # If history data provided in gateway, then query
        if contract and contract.history_data:
            data = self.main_engine.query_history(
                req, contract.gateway_name
            )
        # Otherwise use RQData to query data
        else:
            pass
            # if not rqdata_client.inited:
            #     rqdata_client.init()
            #
            # data = rqdata_client.query_history(req)

        if data:
            database_manager.save_bar_data(data)
            return (len(data))

        return 0