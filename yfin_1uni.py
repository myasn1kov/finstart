import requests
import yfinance as yf
import pandas as pd
import ta
import datetime


PERIOD = input('Выберите период:\n'
    '6mo, 1mo, 5d или 1d:\n'
    )
# Загрузка данных курса доллара за последние 3 дня
df = yf.download('USDRUB=X', period=PERIOD)

# Загрузка текущего курса доллара yfinance
usd_data = yf.download('USDRUB=X', period='1d')
usd_rate_y = usd_data['Close'][-1]

# Получение актуального курса доллара от Alpha Vantage
url = 'https://www.alphavantage.co/query'
params = {
    'function': 'CURRENCY_EXCHANGE_RATE',
    'from_currency': 'USD',
    'to_currency': 'RUB',
    'apikey': 'JW6WYUVRDSEUNJFW'
}
response = requests.get(url, params=params)
usd_rate_av = float(response.json()
                    ['Realtime Currency Exchange Rate']
                    ['5. Exchange Rate'])

# Расчет индикаторов (определить, какие подходят по сроку)
sma = ta.trend.SMAIndicator(df['Close'], window=20)
ema = ta.trend.EMAIndicator(df['Close'], window=20)
wma = ta.trend.WMAIndicator(df['Close'], window=20)
ichimoku = ta.trend.IchimokuIndicator(df['High'], df['Low'])
psar = ta.trend.PSARIndicator(df['High'], df['Low'], df['Close'])
kst = ta.trend.KSTIndicator(df['Close'])
macd = ta.trend.MACD(df['Close'])

# Получение последних значений индикаторов
last_sma = sma.sma_indicator()[-1]
last_ema = ema.ema_indicator()[-1]
last_ichimoku_a = ichimoku.ichimoku_a()[-1]
last_ichimoku_b = ichimoku.ichimoku_b()[-1]
last_psar = psar.psar()[-1]
last_kst = kst.kst()[-1]
last_macd_line = macd.macd()[-1]

# Определение рекомендации по каждому индикатору
buy_counter = 0
sell_counter = 0

if df['Close'][-1] > last_sma:
    buy_counter += 1
else:
    sell_counter += 1

if df['Close'][-1] > last_ema:
    buy_counter += 1
else:
    sell_counter += 1

if df['Close'][-1] > last_ichimoku_a and df['Close'][-1] > last_ichimoku_b:
    buy_counter += 1
else:
    sell_counter += 1

if df['Close'][-1] > last_psar:
    buy_counter += 1
else:
    sell_counter += 1

if last_kst > 0:
    buy_counter += 1
else:
    sell_counter += 1

if last_macd_line > 0:
    buy_counter += 1
else:
    sell_counter += 1


# Вывод общей рекомендации
print(f"Текущий курс доллара (yfinance): {usd_rate_y:.2f} рублей")
print(f"Текущий курс доллара (AV): {usd_rate_av:.2f} рублей")
if buy_counter > sell_counter:
    recommendation = 'Общая рекомендация: Покупать!'
    print(f'{recommendation} {buy_counter} против {sell_counter}')
else:
    recommendation = 'Общая рекомендация: Продавать!'
    print(f'{recommendation} {sell_counter} против {buy_counter}')

# Создание DataFrame и запись результата в таблицу
data = {'Дата': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M')],
        'Курс доллара Yahoo': [f'{usd_rate_y:.2f}'],
        'Курс доллара Alpha Vantage': [f'{usd_rate_av:.2f}'],
        'Рекомендация': [recommendation],
        'Покупка': [buy_counter],
        'Продажа': [sell_counter]}

dq = pd.DataFrame(data)
table_name = f'Прогнозы {PERIOD}.csv'
dq.to_csv(table_name,
          index=False, mode='a',
          header=not bool(open(table_name).read()))
# Добавляем запись в конец существующей таблицы или создаем новую
