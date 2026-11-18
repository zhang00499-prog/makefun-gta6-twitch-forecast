# GTA VI Twitch launch-day viewer forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zhang00499-prog/makefun-gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/zhang00499-prog/makefun-gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

A deterministic, standard-library-only forecaster for GTA VI's launch-day
Twitch audience. Given the release day's first hour, it predicts the
5/25/50/75/95% quantiles of concurrent viewers for hours 2–24 by pooling
the release-day curve shapes of past big launches (the case's
comparables), weighted by how close each comparable's hour-1 audience is
to this case's, with the median shape trusted over a flat persistence
line and a floored, widening spread. Leave-one-out over the kit's 37
usable comparables: mean log-scale pinball loss 0.226 vs the persistence
baseline's 0.465.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/bounty/gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
