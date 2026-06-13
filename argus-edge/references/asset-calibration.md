# Argus Edge Asset Calibration

Asset-specific calibration parameters for TA scoring.

## Calibration Table

| Asset | TA Reliability | Bias | Min Score |
|-------|---------------|------|-----------|
| BTC | 0.75 | Neutral | ±3 |
| ETH | 0.80 | UP+0.05 | ±2 |
| SOL | 0.90 | UP+0.05 | ±1 |
| XRP | 0.70 | UP+0.08 | ±2 |

## Reliability Scores

Higher reliability means TA signals are more predictive:
- 0.90+ = Very reliable, lower thresholds needed
- 0.70-0.89 = Moderately reliable, standard thresholds
- <0.70 = Less reliable, higher thresholds required

## Bias Adjustment

Positive bias means the asset has a historical tendency to move UP on the relevant timeframe.
