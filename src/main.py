import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import pprint
import statistics


def get_dt_from_string(date_string):

    return datetime.strptime(date_string, "%Y-%m-%d-%H").replace(tzinfo=timezone.utc)


def get_historical_stats(file):
    """Get historical stats from the data file"""

    with open(file) as f:
        data = json.load(f)
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
        "last_dt": dt,
        "last_price": price,
    }


def get_iterations(target_dt, initial_dt):

    delta = target_dt - initial_dt
    return int(delta.total_seconds() // 60 // 60)


def gbm(initial_price, mu, sigma, t):
    """Geometric Brownian Motion function that gives the price at time t"""

    Wt = statistics.NormalDist(0, t).samples(1)[0]
    return initial_price * math.exp((mu - (sigma ** 2) / 2) * t + sigma * Wt)


def gbm_iter(initial_price, mu, sigma, t, iterations):
    """Runs the gbm function many times sequentially to simulate the price moving forward in time"""

    current_price = initial_price
    max_price = initial_price
    min_price = initial_price

    for i in range(iterations):
        current_price = gbm(current_price, mu, sigma, t)
        if current_price > max_price:
            max_price = current_price
        elif current_price < min_price:
            min_price = current_price

    return current_price, max_price, min_price


def gbm_iter_trials(initial_price, mu, sigma, t, iterations, trials, target_price, verbose=True):
    """Runs the gbm_iter function many times to simulate many instances of the price forward in time"""

    ended_over = 0
    ended_under = 0
    over_at_any_point = 0
    under_at_any_point = 0

    for i in range(trials):

        if verbose is True:
            print(f"Running trial {i}")

        ending_price, max_price, min_price = gbm_iter(
            initial_price, mu, sigma, t, iterations
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
        "perent_under_at_any_point": (under_at_any_point * 100) / trials,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target_date_string_utc",
        help="The date and hour up to which to run the simulation (e.g. 2021-01-01-05)",
    )
    parser.add_argument("target_price", help="The price for which to gather statistics", type=float)
    parser.add_argument("file", help="The file containing historical data")
    parser.add_argument(
        "-n",
        "--number_of_trials",
        help="Number of trials (simulations) to run",
        default=10000,
        type=int,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print the number of the trial currently running",
        action="store_true",
    )
    args = parser.parse_args()

    target_dt = get_dt_from_string(args.target_date_string_utc)
    historical_stats = get_historical_stats(args.file)
    iterations = get_iterations(target_dt, historical_stats["last_dt"])

    results = gbm_iter_trials(
        historical_stats["last_price"],
        0,
        historical_stats["sigma"],
        1,
        iterations,
        args.number_of_trials,
        args.target_price,
        args.verbose,
    )
    pp = pprint.PrettyPrinter()
    pp.pprint(historical_stats)
    pp.pprint(results)
