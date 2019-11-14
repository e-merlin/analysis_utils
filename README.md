# analysis_utils
Repository to gather analysis tools

## plot_baseline_flags.py

Usage:
`casa --nogui -c read_MS_flags.py <MS_name>`
Outputs:
- One plot per baseline flags_<baseline_name>.png with % flagged per frequency channel
- One plot with all the individual plots together
- csv file where first column is frequency in GHz and the others are %flagged per baseline.
