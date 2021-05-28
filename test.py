import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:.11f}')

n = 10
am = []
for i in range(1, 100):
    am.append(i)

df = pd.DataFrame(am, columns=['close'], dtype=float)
df['median'] = df['close'].rolling(n).mean()
df['std'] = df['close'].rolling(n).std(ddof=0)  # ddof代表标准差自由度
df['z_score'] = abs(df['close'] - df['median']) / df['std']
df['m'] = df['z_score'].rolling(window=n).max().shift(1)

print(df)