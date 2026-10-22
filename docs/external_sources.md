# External sources

Sources consulted for ideas. No code was taken from any of them.

## 1. Prize-winning solution write-up for this competition

- Title (as given by the project author): "Two-layered recommender system methodology: a prize-winning solution"
- Venue: Towards Data Science
- URL: https://towardsdatascience.com/two-layered-recommender-system-methodology-a-prize-winning-solution-c4bdb815b156
- Added: 2026-10-22.
- Verification status: **verified by the project author**, who opened and read the article on 2026-10-22 and
  confirmed the title, URL and the points below (author name and publication date to be added by the project
  author). The AI assistant could not open the page itself (HTTP 403 on 2026-10-22, also via the
  medium.com/towards-data-science path); everything below is as reported by the project author.
- Points used:
  - a show counted as watched only if the user watched more than 80% of it without switching channels;
  - features: counts of watches at 30%, 50% and 80% coverage, the show's rank by count, the show's channel and
    category, how often the user watches it, time since the last watch, and how the show's schedule changes
    (more or fewer airings in the target window than before);
  - "Algorithm 1" (simplest baseline): top-5 shows by the number of times watched, a watch being more than 50% of
    the show's full length in a single sitting, filtered to shows in the future schedule, filled with the most
    popular shows if the user has fewer than 5. Reported public score 0.41296;
  - second layer: about 200 candidates from that baseline plus LightFM, re-ranked with a binary LightGBM;
    reported public score about 0.442.
- Our re-implementation of Algorithm 1 (`src/repeat_cont.py`, method `repeat_cont`) is written from this
  description only; no code was taken from the article.
- How it was used: as a hypothesis for the target definition, tested against our own leaderboard scores in
  `docs/target_definition.md`, and as a list of feature ideas implemented in our own code (`src/`).
