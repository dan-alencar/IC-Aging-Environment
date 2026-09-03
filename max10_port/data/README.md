# data/ — Raw campaign data

*[Leia em português](README.pt-BR.md)*

Empty for now. This is where raw campaign CSVs (and any other raw telemetry) land.

**Hard rule from the plan document (Section 6.3): raw data is immutable.** No
campaign file is ever edited after it's written. If a file needs correction (a known
bad channel, a mislabeled column), that correction happens in the `../analysis/`
processing layer, with the correction itself documented and version-controlled — the
raw file stays exactly as the instrument produced it.

Large raw datasets may not belong directly in git history depending on size and how
many campaigns accumulate — decide and document the storage approach here (Git LFS,
an external data store with a manifest committed here, etc.) before the first long
campaign, not after.
