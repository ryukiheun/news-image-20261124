# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/ryukiheun/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/ryukiheun/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A program that draws a 1024x1024 newspaper-style front page summing up Tuesday 24 November 2026 in 45 stories — Russian warplanes buzzing Ulleung Island and triggering South Korea's first-ever air raid alert, Nvidia giving back 6% a day after Jensen Huang's return as the Dow tops 50,000 for the first time, more tankers hit by mines in the Strait of Hormuz, the KOSPI retaking 5,000, Sanofi's $41 billion Insmed deal, Dell's revenue doubling on AI servers, and the Champions League's matchday 5. Every card carries one source and one confidence tag, and a DATE CHECK box names the older news left out. The PNG is drawn by main.py itself (Python 3.13, standard library only, no network) and written to the output directory; a copy of the drawn image is committed as entry.png. The program is deterministic: two runs write identical bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=r5cs55h2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
