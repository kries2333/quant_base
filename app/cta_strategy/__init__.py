from pathlib import Path

from app.cta_strategy.base import APP_NAME
from app.cta_strategy.engine import CtaEngine
from trader.app import BaseApp


class CtaStrategyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA策略"
    engine_class = CtaEngine
    widget_name = "CtaManager"
    icon_name = "cta.ico"