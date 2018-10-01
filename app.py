import argparse
import ccxt
from datetime import datetime, timezone
import pandas as pd
import json
import os


def parse_cl_args():
    parser = argparse.ArgumentParser(description='c2ba crypto scraper')
    parser.add_argument(
        'settings', help='Path to a json file containing settings')
    parser.add_argument(
        'outfolder', help='Path to output folder, where to store scraped OHLC data'
    )
    return parser.parse_args()


args = parse_cl_args()

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'timeout': 30000,
    'enableRateLimit': True,
})

market_name = 'ETH/BTC'
candle_interval = '1m'
ohlcv = exchange.fetch_ohlcv(market_name, candle_interval)

# timestamp in seconds instead of milliseconds
timestamp = int(ohlcv[0][0] / 1000)
ohlcv_dict = {
    "utc_timestamp": timestamp,
    "open": [d[1] for d in ohlcv],
    "high": [d[2] for d in ohlcv],
    "low": [d[3] for d in ohlcv],
    "close": [d[4] for d in ohlcv],
    "volume": [d[5] for d in ohlcv],
}

for candle in ohlcv:
    ts = int(candle[0] / 1000)
    hour = int(ts / 3600)
    hour_start_ts = hour * 3600
    print(datetime.utcfromtimestamp(hour_start_ts), hour_start_ts, ts)

outfilename = '{}-{}-{}-{}.json'.format(market_name.replace(
    '/', ''), candle_interval, timestamp, len(ohlcv))

with open(os.path.join(args.outfolder, outfilename), 'w') as outfile:
    json.dump(ohlcv_dict, outfile)
