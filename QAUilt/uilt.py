import glob
import pandas as pd

symbol = 'DOGE-USDT_1m'

def readFile(path):
    df = pd.read_csv(path, header=0, encoding="GBK", parse_dates=['candle_begin_time'])
    df = df[['candle_begin_time', 'open', 'high', 'low', 'close']]
    return df

def outfile():
    path = "../data/binance/spot"
    path_list = glob.glob(path + "/*/*.csv")  # python自带的库，获得某文件夹中所有csv文件的路径

    path_list = list(filter(lambda x: symbol in x, path_list))

    # 导入数据
    df_list = []
    for path in sorted(path_list):
        print(path)
        df = pd.read_csv(path, header=0, encoding="GBK", parse_dates=['candle_begin_time'])
        df = df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]
        df_list.append(df)
        print(df.head(5))

    # 整理完整数据
    data = pd.concat(df_list, ignore_index=True)
    data.sort_values(by='candle_begin_time', inplace=False)
    data.reset_index(drop=False, inplace=False)

    data.to_pickle('%s.pkl' % symbol)
    print(data)


def outfile_test():
    # ===读入数据
    df = pd.read_pickle('%s.pkl' % symbol)

    # 任何原始数据读入都进行一下排序、去重，以防万一
    df.sort_values(by=['candle_begin_time'], inplace=True)
    df.drop_duplicates(subset=['candle_begin_time'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # =====转换为其他分钟数据
    period_df = df.resample(rule='15T', on='candle_begin_time', label='left', closed='left').agg(
        {'open': 'first',
         'high': 'max',
         'low': 'min',
         'close': 'last',
         'volume': 'sum'
         })
    period_df.dropna(subset=['open'], inplace=True)  # 去除一天都没有交易的周期
    period_df = period_df[period_df['volume'] > 0]  # 去除成交量为0的交易周期
    period_df.reset_index(inplace=True)
    df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]
    df = df[df['candle_begin_time'] >= pd.to_datetime('2018-01-01')]
    df.reset_index(inplace=True, drop=True)

if __name__ == "__main__":
    outfile()