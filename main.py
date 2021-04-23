

# Press the green button in the gutter to run the script.
import time

from QARealTrade.real_server import start

if __name__ == '__main__':
    while True:
        try:
            start()
        except Exception as e:
            print("error:", e)
            time.sleep(10)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
