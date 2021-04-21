from urllib.parse import urljoin

OKEx_base_url = ''


def fetch_okex_symbol_candle_data(exchange, symbol):
    # 请求数据
    url = '/api/v5/market/history-candles'
    url = urljoin(
        OKEx_base_url,
        '/api/v5/market/history-candles'.format(symbol)
    )
