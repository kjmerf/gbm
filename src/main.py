import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import pprint
import statistics

import requests


def get_data(coin_id, days=90, target_currency="usd"):

    print("Getting historical data from Coin Gecko...")
    payload = {"days": days, "vs_currency": target_currency}
    response = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart", params=payload
    )
    response.raise_for_status()
    return response.json()


def get_dt_from_string(date_string):

    return datetime.strptime(date_string, "%Y-%m-%d-%H").replace(tzinfo=timezone.utc)


def get_historical_stats(data):

    last_dt = None
    last_log_price = None
    deltas = []

    for row in data["prices"]:
        # the unixtime from the API has three extra digits
        unixtime = int(str(row[0])[:-3])
        dt = datetime.fromtimestamp(unixtime, tz=timezone.utc)
        price = row[1]
        log_price = math.log(price)

        if last_dt is not None:
            try:
                assert dt > last_dt
                deltas.append(log_price - last_log_price)

            except AssertionError:
                raise ValueError(
                    f"{dt} was followed by {last_dt}. Data must be in order!"
                )

        last_dt = dt
        last_log_price = log_price

    return {
        "sigma": statistics.stdev(deltas),
        "mu": statistics.mean(deltas),
        "last_dt": dt,
        "last_price": price,
    }


def get_iterations(target_dt, initial_dt):

    delta = target_dt - initial_dt
    return int(delta.total_seconds() // 60 // 60)


def gbm(initial_price, mu, sigma, t=1):
    """Geometric Brownian Motion function that gives the price at time t"""

    wiener = statistics.NormalDist(0, t).samples(1)[0]
    return initial_price * math.exp((mu - (sigma ** 2) / 2) * t + sigma * wiener)


def gbm_iter(initial_price, mu, sigma, iterations):
    """Runs the gbm function many times sequentially to simulate the price moving forward in time"""

    current_price = initial_price
    max_price = initial_price
    min_price = initial_price

    for i in range(iterations):
        current_price = gbm(current_price, mu, sigma)
        if current_price > max_price:
            max_price = current_price
        elif current_price < min_price:
            min_price = current_price

    return current_price, max_price, min_price


def gbm_trials(
    initial_price, mu, sigma, iterations_per_trial, trials, target_price, verbose=True
):
    """Runs the gbm_iter function many times to simulate many instances of the price forward in time"""

    ended_over = 0
    ended_under = 0
    over_at_any_point = 0
    under_at_any_point = 0

    for i in range(trials):

        if verbose is True:
            print(f"Running trial {i}")

        ending_price, max_price, min_price = gbm_iter(
            initial_price, mu, sigma, iterations_per_trial
        )
        if ending_price >= target_price:
            ended_over += 1
        if ending_price < target_price:
            ended_under += 1
        if max_price >= target_price:
            over_at_any_point += 1
        if min_price < target_price:
            under_at_any_point += 1

    return {
        "percent_ended_over": (ended_over * 100) / trials,
        "percent_ended_under": (ended_under * 100) / trials,
        "percent_over_at_any_point": (over_at_any_point * 100) / trials,
        "percent_under_at_any_point": (under_at_any_point * 100) / trials,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target_date_string_utc",
        help="The date and hour up to which to run the simulation (e.g. 2021-01-01-05)",
    )
    parser.add_argument(
        "target_price", help="The price for which to gather statistics", type=float
    )
    parser.add_argument("coin_id", help="The id of the coin used in the simulation")
    parser.add_argument(
        "-n",
        "--number_of_trials",
        help="Number of trials (simulations) to run",
        default=10000,
        type=int,
    )
    parser.add_argument(
        "-m",
        "--mu",
        help="Calculate historical drift and use it as an input in the simulations",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print the number of the trial currently running",
        action="store_true",
    )
    args = parser.parse_args()

    target_dt = get_dt_from_string(args.target_date_string_utc)
    data = get_data(args.coin_id)
    historical_stats = get_historical_stats(data)
    iterations_per_trial = get_iterations(target_dt, historical_stats["last_dt"])

    results = gbm_trials(
        historical_stats["last_price"],
        historical_stats["mu"] if args.mu is True else 0,
        historical_stats["sigma"],
        iterations_per_trial,
        args.number_of_trials,
        args.target_price,
        args.verbose,
    )
    pp = pprint.PrettyPrinter()
    print("\n---Arguments---\n")
    pp.pprint(vars(args))
    print("\n---Historical stats---\n")
    pp.pprint(historical_stats)
    print("\n---Results---\n")
    pp.pprint(results)
    print("\n")
