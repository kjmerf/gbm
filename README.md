# gbm

This repo can be used to compute the likelihood that a given cyptocurrency reaches a target price on or before a target date.
The program relies on hourly historical data which can be downloaded with:

```curl -X 'GET' 'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=90' -H 'accept: application/json' > /tmp/data.json```

For details see https://www.coingecko.com/en/api/documentation.

To run the program, you can use:

```python3 src/main.py 2022-01-01-00 4500 -n 10000 -v /tmp/data.json```

To view all the required and optional arguments, see:

```python3 src/main.py --help```

To run the unit tests, you can use:

```python3 -m unittest discover```
