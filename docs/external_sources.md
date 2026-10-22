# External sources

Sources consulted for ideas. No code was taken from any of them.

## 1. Prize-winning solution write-up for this competition

- Title (as given by the project author): "Two-layered recommender system methodology: a prize-winning solution"
- Venue: Towards Data Science
- URL: https://towardsdatascience.com/two-layered-recommender-system-methodology-a-prize-winning-solution-c4bdb815b156
- Added: 2026-10-22.
- Verification status: **not read by the AI assistant.** An attempt to fetch the page on 2026-10-22 returned
  HTTP 403 (also via the medium.com/towards-data-science path). Title, URL and the points below come from the
  project author's reading of the article; author names and publication date still have to be filled in from
  the article itself before citing.
- Points used, as reported by the project author:
  - a show counted as watched only if the user watched more than 80% of it without switching channels;
  - features: counts of watches at 30%, 50% and 80% coverage, the show's rank by count, the show's channel and
    category, how often the user watches it, time since the last watch, and how the show's schedule changes
    (more or fewer airings in the target window than before).
- How it was used: as a hypothesis for the target definition, tested against our own leaderboard scores in
  `docs/target_definition.md`, and as a list of feature ideas implemented in our own code (`src/`).
