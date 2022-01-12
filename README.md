# gbm

This repo can be used to compute the likelihood that a given cyptocurrency reaches a target price on or before a target date.

For example, to test the likelihood that ETH will reach 5K by April 2022, you could run:

```python3 src/main.py 2022-04-01-00 5000 ethereum -n 1000```

To view all the required and optional arguments, see:

```python3 src/main.py --help```

The coin id must come from this list:
```curl -X 'GET' 'https://api.coingecko.com/api/v3/coins/list' -H 'accept: application/json'```

In most cases you will probably just use ```bitcoin```, ```ethereum```, or ```cardano```.

To run the unit tests, you can use:

```python3 -m unittest discover```
