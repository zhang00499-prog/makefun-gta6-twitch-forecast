"""Forecast a launch day's Twitch viewers, hours 2..24, from hour 1.

Idea: a big launch's release-day curve has a repeatable shape once it is
scaled by its first hour.  Every comparable in the case is a past launch
with its full hourly series attached, so for each target hour h we look at
the distribution of ratios

    r_h = viewers(hour h of the comparable's release day) / viewers(hour 1)

across comparables, weight each comparable by how close its own hour-1
audience is to this case's hour-1 audience (log scale), and read the five
scored quantiles off that weighted distribution.  The median ratio is
shrunk a little toward 1.0 (the persistence forecast) because any single
day can refuse to follow the crowd, and the spread is floored at a
fraction of the house baseline's random-walk width so the outer quantiles
never claim more certainty than a launch day deserves.

The program is deterministic, standard library only, and offline: it
reads every <id>.in in the input directory and writes <id>.out with
{"hours": [{"hour": h, "q": [q05, q25, q50, q75, q95]}, ...]}.
"""

import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0.0, 0.674, 1.645]

# How far the median ratio is trusted over plain persistence (0 = the
# baseline's flat line, 1 = the comparables' median shape, unshrunk).
# Tuned by leave-one-out over the kit's comparables: 0.95 scored 0.226
# mean log pinball against the persistence baseline's 0.465.
MEDIAN_TRUST = 0.95
# Weight fall-off, in decades of hour-1 audience, for comparable weighting.
WEIGHT_SCALE = 0.5
# The spread never goes below this share of the baseline's log width.
SPREAD_FLOOR_SHARE = 0.65
BASE_SIGMA = 0.15


def round2(x):
    """Round to 2 decimals, half up; whole numbers come back as int."""
    scaled = x * 100.0
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    value = whole / 100.0
    return int(value) if float(value).is_integer() else value


def release_day_hours(comparable):
    """Map hour-of-release-day (1..24) -> viewers for one comparable."""
    day_start = comparable.get("day_start") or ""
    hours = {}
    for point in comparable.get("hourly") or []:
        stamp = point.get("from") or ""
        if not stamp.startswith(day_start[:10]):
            continue
        try:
            hour = int(stamp[11:13]) + 1
        except ValueError:
            continue
        viewers = point.get("viewers")
        if viewers is not None and viewers > 0:
            hours[hour] = float(viewers)
    return hours


def weighted_quantile(pairs, tau):
    """Quantile of values in (value, weight) pairs, linear interpolation."""
    ordered = sorted(pairs)
    total = sum(w for _, w in ordered)
    if total <= 0:
        return ordered[len(ordered) // 2][0]
    target = tau * total
    acc = 0.0
    for i, (value, weight) in enumerate(ordered):
        acc += weight
        if acc >= target:
            if i == 0:
                return value
            prev_value, prev_weight = ordered[i - 1]
            prev_acc = acc - weight
            if weight <= 0:
                return value
            frac = (target - prev_acc) / weight
            return prev_value + frac * (value - prev_value)
    return ordered[-1][0]


def ratio_table(case, p1):
    """Per target hour, the weighted (log ratio, weight) samples available."""
    log_p1 = math.log10(max(p1, 1.0))
    table = {}
    for comparable in case.get("comparables") or []:
        hours = release_day_hours(comparable)
        base = hours.get(1)
        if not base:
            continue
        distance = abs(math.log10(base) - log_p1) / WEIGHT_SCALE
        weight = math.exp(-0.5 * distance * distance) + 0.05
        for hour, viewers in hours.items():
            if hour >= 2:
                table.setdefault(hour, []).append((math.log(viewers / base), weight))
    return table


def forecast_case(case):
    first = next((k for k in case.get("known") or [] if k.get("hour") == 1), None)
    if first is None:
        raise ValueError("case has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    table = ratio_table(case, p1)
    rows = []
    for spec in case["forecast"]:
        hour = spec["hour"]
        samples = table.get(hour) or []
        floor_sigma = SPREAD_FLOOR_SHARE * BASE_SIGMA * math.sqrt(hour - 1)
        if len(samples) >= 6:
            med = weighted_quantile(samples, 0.5)
            centre = MEDIAN_TRUST * med
            quantiles = []
            for tau, z in zip(LEVELS, Z):
                raw = weighted_quantile(samples, tau)
                # Keep each quantile at least its share of floor_sigma away
                # from the centre, on its own side, so the spread stays
                # honest even when comparables agree suspiciously well.
                reach = (abs(z) / 1.645) * floor_sigma
                if z < 0:
                    log_q = min(raw, centre - reach)
                elif z > 0:
                    log_q = max(raw, centre + reach)
                else:
                    log_q = centre
                quantiles.append(log_q)
            # The middle quantile is the shrunk centre, by construction.
            quantiles[2] = centre
        else:
            quantiles = [z * BASE_SIGMA * math.sqrt(hour - 1) for z in Z]
        values = []
        for log_q in quantiles:
            values.append(round2(p1 * math.exp(log_q)))
        values = [min(max(v, 0.01), 1e9) for v in values]
        values.sort()
        rows.append({"hour": hour, "q": values})
    return {"hours": rows}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text())
        result = forecast_case(case)
        out_name = str(case.get("id") or path.stem) + ".out"
        (OUTPUT_DIR / out_name).write_text(json.dumps(result))


if __name__ == "__main__":
    main()
