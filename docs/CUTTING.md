# Choose a cutting level

Start with 0 and a 30-second test. If quiet words or breaths disappear, move toward −5. If long gaps remain, move toward +5, or try Noise/Music first when continuous background sound masks pauses.

Negative numbers are gentler settings, not negative thresholds. 0 is Balanced, not Off. Audio cleanup Off disables cleanup, not silence cutting. Adjacent presets can produce the same result on a given recording.

| Level | Threshold | Padding each side | Minimum cut / speech clip (seconds) |
|---|---|---|---|
| −5 | 0.5% | .50 | 1.50 / .15 |
| −4 | 0.75% | .40 | 1.20 / .15 |
| −3 | 1% | .35 | 1.00 / .15 |
| −2 | 1.5% | .325 | .90 / .15 |
| −1 | 2% | .30 | .80 / .15 |
| 0 | 4% | .25 | .60 / .15 |
| +1 | 8% | .20 | .45 / .15 |
| +2 | 12% | .12 | .25 / .12 |
| +3 | 20% | .06 | .15 / .08 |
| +4 | 30% | .04 | .10 / .06 |
| +5 | 40% | .02 | .08 / .05 |

Custom accepts threshold .5–40%, padding .02–.60 seconds and minimum pause .10–2 seconds. Lower thresholds preserve quieter sound; more padding protects word edges; longer minimum pauses retain short natural gaps. Change one field at a time. A threshold is full-scale amplitude, not a percentage of this recording's loudest moment.

Custom minimum speech clip is fixed at .15 seconds. Reset/copy loads the scale's three displayed values within bounds: +5 pause .08 becomes .10. Therefore Custom does not reproduce all smoothing behaviour of +2…+5. Choose those scale levels directly for an exact match.
