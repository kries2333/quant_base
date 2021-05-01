import glob
import pandas as pd

# 策略名称
# 每个币种、时间周期的策略数量
strategy_num = 3

def all_statistics(strategy_name):
    # 遍历所有策略结果
    rtn = pd.DataFrame()
    path_list = glob.glob('../data/output/para/*.csv')  # python自带的库，或者某文件夹中所有csv文件的路径

    for path in path_list:

        if strategy_name not in path:
            continue

        # 读取最优参数，选择排名前strategy_num的
        df = pd.read_csv(path, skiprows=1, nrows=strategy_num)

        df['strategy_name'] = strategy_name
        filename = path.split('/')[-1][:-4]
        df['symbol'] = filename.split('-')[1]
        df['leverage'] = filename.split('-')[2]
        df['周期'] = filename.split('-')[3]
        df['tag'] = filename.split('-')[4]

        rtn = rtn.append(df, ignore_index=True)

    # 输出策略详细结果
    rtn = rtn[['strategy_name', 'symbol', '周期', 'leverage', 'para', '累计净值', '年化收益', '最大回撤', '年化收益回撤比']]
    rtn.sort_values(by=['strategy_name', 'symbol', '周期', '年化收益回撤比'], ascending=[1, 1, 1, 0], inplace=True)
    print(rtn)
    rtn.to_csv('../data/output/所有策略最优参数.csv', index=False)

    # 输出策略
    summary = rtn.groupby(['strategy_name', 'symbol'])[['年化收益回撤比']].mean().reset_index()
    print(summary)
    summary.to_csv('../data/output/策略总体评价.csv', index=False)

if __name__ == "__main__":
    strategy_name = "signal_double_bolling_rsi"
    all_statistics(strategy_name)