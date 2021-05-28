from pathlib import Path

from trader.app import BaseApp
from .engine import APP_NAME, BacktesterEngine


class CtaBacktesterApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA回测"
    engine_class = BacktesterEngine
    widget_name = "BacktesterManager"
    icon_name = "backtester.ico"