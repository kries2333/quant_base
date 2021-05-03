import pandas as pd

from QAAccount.QAAccount_binance import binance_futures_get_accounts
from QAAccount.QAAccount_okex import okex_futures_get_accounts, okex_fetch_future_position

def fetch_future_account(ex):
    if ex == "okex":
        future_info = okex_futures_get_accounts()
    elif ex == "binance":
        future_info = binance_futures_get_accounts()

    data = future_info[0]['details']
    df = pd.DataFrame(data, dtype=float).T  # 将数据转化为df格式
    return df

def fetch_future_position(ex):
    if ex == "okex":
        position_info = okex_fetch_future_position()
    elif ex == "binance":
        print("")

    # 整理数据
    df = pd.DataFrame(position_info, dtype=float)
    # 防止账户初始化时出错
    if "instId" in df.columns:
        df['index'] = df['instId'].str[:-5].str.lower()
        df.set_index(keys='index', inplace=True)
        df.index.name = None
    return df

def update_symbol_info(ex, symbol_info, symbol_config):
    # 通过交易所接口获取合约账户信息
    future_account = fetch_future_account(ex)

    # 通过交易所接口获取合约账户持仓信息
    future_position = fetch_future_position(ex)

    if future_account.empty is False:
        symbol_info['账户权益'] = future_account[0]['availEq']

    if future_position.empty is False:
        for x in future_position.index:
            position = future_position.loc[x]
            instrument_id = x.upper()
            # 从future_position中获取原始数据
            symbol_info.loc[instrument_id, '最大杠杆'] = position['lever']
            symbol_info.loc[instrument_id, '当前价格'] = position['last']

            if position['posSide'] == "long":
                symbol_info.loc[instrument_id, '持仓方向'] = '多单'
                symbol_info.loc[instrument_id, '持仓量'] = position['pos']
                symbol_info.loc[instrument_id, '持仓均价'] = position['avgPx']
                symbol_info.loc[instrument_id, '持仓收益率'] = position['uplRatio']
                symbol_info.loc[instrument_id, '持仓收益'] = position['upl']
            elif position['posSide'] == "short":
                symbol_info.loc[instrument_id, '持仓方向'] = '空单'
                symbol_info.loc[instrument_id, '持仓量'] = position['pos']
                symbol_info.loc[instrument_id, '持仓均价'] = position['avgPx']
                symbol_info.loc[instrument_id, '持仓收益率'] = position['uplRatio']
                symbol_info.loc[instrument_id, '持仓收益'] = position['upl']

    else:
        # 当future_position为空时，将持仓方向的控制填充为0，防止之后判定信号时出错
        symbol_info['持仓方向'].fillna(value=0, inplace=True)

    return symbol_info


if __name__ == "__main__":
    pass
    # # =获取持仓数据
    # # 初始化symbol_info，在每次循环开始时都初始化
    # symbol_info_columns = ['账户权益', '持仓方向', '持仓量', '持仓收益率', '持仓收益', '持仓均价', '当前价格', '最大杠杆']
    # symbol_info = pd.DataFrame(index=symbol_config.keys(), columns=symbol_info_columns)  # 转化为dataframe
    #
    # # 通过交易所接口获取合约账户信息
    # symbol_info = update_symbol_info()
    # print(symbol_info)