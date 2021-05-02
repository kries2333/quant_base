from QAFetch.QAFetch_binance import get_fetch_binance


def GetFetch(ex):
    print("获取现货数据")

    if ex == "":
        get_fetch_binance()