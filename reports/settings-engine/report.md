# The decision engine's own dials

> How much do the dials of the decision itself — headroom, how far ahead and how finely it looks, how fast it may grow, and a floor of always-on local executors — change what a day costs and how late it runs?

180 runs: 45 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-21T16:08:20+00:00 by autoscaler 2.0.0-dev.3+1bbd547 (`1bbd5472a9db`) and simlab-api 3.0.0 (`1dcaed0addff`), built from clean checkouts of those commits, measured by platform-experiments 1.0.0-dev.22+024b6e7 (`024b6e7d5aa2`).

Regenerate with:

```bash
make -C platform-experiments sweep S=settings-engine
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `8c941ed43cc33624…`.

## Reading

The dials of the decision itself, one at a time, against what autoscaler 2.0
ships: safety factor 1.15, a 15-minute horizon simulated in 15-second steps,
growth of up to 50 executors a decision with no cooldown, and a floor of one
local executor. Local cap 12, cloud cap 60.

**The horizon has to see past the deadlines it protects.** A 5-minute horizon
multiplied a workday's breaches by eight (16 → 132). Priority 50's deadline is
also 5 minutes, so a horizon that short likely sees such a job breach only once
capacity started for it would arrive too late. Under the bursts it did no harm
to breaches (−2 %, −8 %) but bought 11–30 % more cloud. 30 or 60 minutes cut
workday breaches by 22 %, for 22–36 % more cloud, and by 4–8 % under the
bursts. The horizon is a structural choice — at least the longest deadline
scaled for plus the slower coldstart — rather than a dial to turn.

**Headroom is the honest runtime trade.**

| Safety factor against 1.15 | 1.0 | 1.3 | 1.5 |
|---|---:|---:|---:|
| workday: breaches / cloud h | +115 % / −18 % | −23 % / +33 % | −31 % / +87 % |
| rock burst | +16 % / −12 % | −4 % / +18 % | −5 % / +43 % |
| earthquake | +18 % / −4 % | −8 % / +7 % | −14 % / +18 % |

No headroom costs breaches everywhere; more of it buys fewer, at a price that
falls as the burst grows — during a large burst the cap binds, and there is
less left to buy.

**Growing slowly only hurts.** A 5-minute scale-up cooldown multiplied workday
breaches by nine (+769 %) and added 20–23 % under the bursts; one minute cost
3–20 %. Limiting growth to 5 or 20 executors a decision changed little (0–2 %),
so a limit there rarely binds.

**The simulation step** matters only when coarse: 60 seconds added 7–25 % to
breaches, while 5 seconds took 2–6 % off for three times the arithmetic.

**Keeping every local executor on was the best single change.** A floor at the
local cap (12) took 60 % off workday breaches (16 → 6), 4 % under the rock
burst and 18 % under the earthquake, and cut the 95th-percentile wait by 7–37 %,
for 2–4 % more local executor-hours and 1–3 % less cloud. A floor of 0 instead
of 1 added 3–8 %.

**For a mine:** keep the horizon, step, growth limit and cooldown as shipped;
treat the safety factor as a runtime dial — 1.3 while a burst is under way —
and hold owned capacity rather than hand it back.

**Caveats.** Four seeds, one mine, intent off, one change at a time. Dials that
interact (horizon and coldstart, floor and local window) were not crossed.

## Results

| Arm | Breaches | Cloud h | Local h | Drained h | Overloads | Wait p95 s | Locate all, mean s | Locate all, p95 s | Locate exposing, mean s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · reference | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · safety 1.0 | 35<br><sub>20–45</sub> | 43.6<br><sub>37.1–59.1</sub> | 271.7<br><sub>263.7–277.4</sub> | 31.0<br><sub>24.0–34.6</sub> | 4<br><sub>0–10</sub> | 13,490<br><sub>6,234–17,665</sub> | 58<br><sub>57–60</sub> | 178<br><sub>175–185</sub> | 56<br><sub>52–62</sub> |
| workday · safety 1.3 | 12<br><sub>5–26</sub> | 70.3<br><sub>64.4–73.0</sub> | 282.0<br><sub>281.7–282.3</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 532<br><sub>448–766</sub> | 42<br><sub>42–43</sub> | 115<br><sub>110–118</sub> | 41<br><sub>38–47</sub> |
| workday · safety 1.5 | 11<br><sub>5–26</sub> | 99.1<br><sub>92.1–103.3</sub> | 285.1<br><sub>284.8–285.4</sub> | 24.0 | 0 | 300<br><sub>295–305</sub> | 37<br><sub>37–38</sub> | 92<br><sub>90–93</sub> | 35<br><sub>32–41</sub> |
| workday · horizon 5 min | 132<br><sub>72–173</sub> | 77.7<br><sub>62.9–90.0</sub> | 251.7<br><sub>250.4–252.4</sub> | 24.1<br><sub>24.0–24.2</sub> | 13<br><sub>7–22</sub> | 4,265<br><sub>3,053–6,303</sub> | 66<br><sub>65–68</sub> | 213<br><sub>206–220</sub> | 65<br><sub>58–75</sub> |
| workday · horizon 30 min | 13<br><sub>5–26</sub> | 64.9<br><sub>58.5–71.0</sub> | 281.4<br><sub>280.7–282.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 971<br><sub>540–2,104</sub> | 43<br><sub>43–44</sub> | 116<br><sub>113–118</sub> | 42<br><sub>38–48</sub> |
| workday · horizon 60 min | 13<br><sub>5–26</sub> | 72.3<br><sub>66.6–75.1</sub> | 283.0<br><sub>282.7–283.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 449<br><sub>415–526</sub> | 41<br><sub>41–42</sub> | 108<br><sub>103–112</sub> | 39<br><sub>34–46</sub> |
| workday · step 5 s | 16<br><sub>9–29</sub> | 55.3<br><sub>46.0–64.7</sub> | 278.1<br><sub>277.6–278.4</sub> | 24.0<br><sub>24.0–24.1</sub> | 1<br><sub>0–4</sub> | 3,486<br><sub>1,692–6,170</sub> | 48<br><sub>47–48</sub> | 137<br><sub>135–140</sub> | 45<br><sub>41–50</sub> |
| workday · step 60 s | 18<br><sub>10–30</sub> | 48.6<br><sub>43.6–51.4</sub> | 276.7<br><sub>275.9–277.7</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 6,142<br><sub>4,164–8,853</sub> | 49<br><sub>48–52</sub> | 140<br><sub>136–143</sub> | 47<br><sub>44–52</sub> |
| workday · scale-up step 5 | 16<br><sub>9–30</sub> | 51.4<br><sub>46.0–55.2</sub> | 277.3<br><sub>276.5–278.1</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,771<br><sub>2,450–8,370</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>41–52</sub> |
| workday · scale-up step 20 | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · scale-up cooldown 1 min | 20<br><sub>12–30</sub> | 48.0<br><sub>41.5–52.2</sub> | 276.9<br><sub>276.2–278.0</sub> | 24.0<br><sub>24.0–24.1</sub> | 1<br><sub>0–2</sub> | 6,383<br><sub>5,022–9,928</sub> | 50<br><sub>48–52</sub> | 142<br><sub>139–145</sub> | 47<br><sub>43–53</sub> |
| workday · scale-up cooldown 5 min | 141<br><sub>55–283</sub> | 40.5<br><sub>32.5–53.4</sub> | 279.1<br><sub>273.4–286.6</sub> | 27.1<br><sub>24.0–32.8</sub> | 13<br><sub>1–33</sub> | 11,019<br><sub>5,211–17,360</sub> | 55<br><sub>54–57</sub> | 170<br><sub>166–177</sub> | 54<br><sub>48–57</sub> |
| workday · local floor 0 | 18<br><sub>9–33</sub> | 52.9<br><sub>50.3–56.8</sub> | 277.7<br><sub>276.5–278.4</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local floor 12 | 6<br><sub>0–13</sub> | 51.9<br><sub>49.0–57.5</sub> | 287.9<br><sub>287.8–288.1</sub> | 24.0 | 2<br><sub>0–5</sub> | 4,254<br><sub>2,428–6,892</sub> | 48<br><sub>46–50</sub> | 142<br><sub>138–147</sub> | 46<br><sub>42–52</sub> |
| rock burst · reference | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 307.2<br><sub>305.9–309.3</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 40,625<br><sub>29,145–48,307</sub> | 132<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–105</sub> |
| rock burst · safety 1.0 | 7,338<br><sub>6,578–7,934</sub> | 117.2<br><sub>108.3–128.6</sub> | 315.1<br><sub>308.9–321.6</sub> | 48.1<br><sub>48.0–48.2</sub> | 203<br><sub>194–212</sub> | 85,561<br><sub>84,353–86,266</sub> | 143<br><sub>136–154</sub> | 982<br><sub>916–1,079</sub> | 95<br><sub>70–113</sub> |
| rock burst · safety 1.3 | 6,077<br><sub>5,673–6,531</sub> | 157.3<br><sub>149.6–167.7</sub> | 289.4<br><sub>288.1–290.7</sub> | 28.1<br><sub>26.2–30.0</sub> | 198<br><sub>188–210</sub> | 16,417<br><sub>15,484–17,550</sub> | 127<br><sub>118–140</sub> | 967<br><sub>889–1,079</sub> | 77<br><sub>55–100</sub> |
| rock burst · safety 1.5 | 6,037<br><sub>5,624–6,531</sub> | 191.6<br><sub>182.1–203.3</sub> | 285.4<br><sub>284.9–286.4</sub> | 24.0 | 198<br><sub>188–210</sub> | 7,184<br><sub>6,704–7,749</sub> | 122<br><sub>113–135</sub> | 959<br><sub>885–1,075</sub> | 72<br><sub>50–95</sub> |
| rock burst · horizon 5 min | 6,220<br><sub>5,823–6,595</sub> | 174.1<br><sub>163.5–183.6</sub> | 264.7<br><sub>258.7–270.4</sub> | 28.7<br><sub>26.4–30.4</sub> | 222<br><sub>214–228</sub> | 8,722<br><sub>5,813–12,202</sub> | 149<br><sub>140–160</sub> | 981<br><sub>915–1,079</sub> | 103<br><sub>79–121</sub> |
| rock burst · horizon 30 min | 6,090<br><sub>5,695–6,533</sub> | 151.1<br><sub>143.8–163.1</sub> | 294.3<br><sub>292.4–295.7</sub> | 33.4<br><sub>31.5–36.0</sub> | 199<br><sub>189–210</sub> | 19,623<br><sub>18,472–20,378</sub> | 128<br><sub>120–141</sub> | 972<br><sub>900–1,079</sub> | 79<br><sub>57–101</sub> |
| rock burst · horizon 60 min | 6,079<br><sub>5,685–6,531</sub> | 160.9<br><sub>154.5–170.6</sub> | 286.0<br><sub>284.3–287.4</sub> | 24.7<br><sub>24.1–26.3</sub> | 199<br><sub>189–210</sub> | 13,860<br><sub>12,906–14,690</sub> | 126<br><sub>118–139</sub> | 969<br><sub>895–1,079</sub> | 76<br><sub>54–98</sub> |
| rock burst · step 5 s | 6,205<br><sub>5,763–6,717</sub> | 135.0<br><sub>126.6–149.4</sub> | 306.1<br><sub>302.2–308.8</sub> | 46.7<br><sub>43.0–48.1</sub> | 200<br><sub>189–211</sub> | 38,215<br><sub>26,194–46,057</sub> | 132<br><sub>124–144</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–106</sub> |
| rock burst · step 60 s | 6,799<br><sub>6,237–7,276</sub> | 129.8<br><sub>123.5–138.4</sub> | 309.5<br><sub>308.1–311.0</sub> | 48.6<br><sub>48.4–48.8</sub> | 195<br><sub>187–206</sub> | 49,341<br><sub>41,434–56,332</sub> | 134<br><sub>126–146</sub> | 979<br><sub>910–1,079</sub> | 84<br><sub>62–106</sub> |
| rock burst · scale-up step 5 | 6,480<br><sub>6,022–6,977</sub> | 132.2<br><sub>125.4–141.6</sub> | 307.9<br><sub>306.5–309.9</sub> | 48.1<br><sub>48.0–48.2</sub> | 206<br><sub>194–219</sub> | 42,516<br><sub>32,869–50,287</sub> | 140<br><sub>130–156</sub> | 1,039<br><sub>955–1,150</sub> | 86<br><sub>63–109</sub> |
| rock burst · scale-up step 20 | 6,310<br><sub>5,833–6,807</sub> | 133.6<br><sub>125.7–145.8</sub> | 307.2<br><sub>305.9–309.4</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–211</sub> | 40,478<br><sub>29,142–48,532</sub> | 133<br><sub>125–146</sub> | 980<br><sub>904–1,087</sub> | 83<br><sub>60–105</sub> |
| rock burst · scale-up cooldown 1 min | 6,611<br><sub>6,211–6,875</sub> | 129.2<br><sub>122.8–139.3</sub> | 310.7<br><sub>308.4–312.6</sub> | 48.1<br><sub>48.0–48.2</sub> | 202<br><sub>193–210</sub> | 53,436<br><sub>48,293–61,207</sub> | 136<br><sub>129–147</sub> | 999<br><sub>931–1,082</sub> | 86<br><sub>62–109</sub> |
| rock burst · scale-up cooldown 5 min | 7,826<br><sub>7,442–8,362</sub> | 118.0<br><sub>110.4–121.9</sub> | 319.8<br><sub>315.1–324.3</sub> | 48.2<br><sub>48.1–48.3</sub> | 230<br><sub>225–235</sub> | 83,422<br><sub>76,118–85,966</sub> | 162<br><sub>158–166</sub> | 1,157<br><sub>1,120–1,208</sub> | 105<br><sub>77–128</sub> |
| rock burst · local floor 0 | 6,769<br><sub>6,409–7,031</sub> | 133.6<br><sub>125.9–145.8</sub> | 307.2<br><sub>306.0–309.2</sub> | 48.0<br><sub>47.9–48.1</sub> | 200<br><sub>189–210</sub> | 85,669<br><sub>85,552–85,762</sub> | 132<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–105</sub> |
| rock burst · local floor 12 | 6,111<br><sub>5,720–6,532</sub> | 131.7<br><sub>121.2–146.7</sub> | 313.2<br><sub>309.2–315.7</sub> | 26.1<br><sub>25.8–26.3</sub> | 200<br><sub>189–210</sub> | 28,096<br><sub>24,452–31,286</sub> | 132<br><sub>124–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>62–106</sub> |
| earthquake · reference | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 393.0<br><sub>387.2–398.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,391<br><sub>86,361–86,410</sub> | 441<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · safety 1.0 | 29,371<br><sub>28,047–31,167</sub> | 341.1<br><sub>331.5–350.0</sub> | 400.2<br><sub>393.8–409.7</sub> | 48.3<br><sub>48.2–48.3</sub> | 744<br><sub>713–777</sub> | 86,505<br><sub>86,499–86,521</sub> | 455<br><sub>412–500</sub> | 3,002<br><sub>2,820–3,092</sub> | 406<br><sub>163–557</sub> |
| earthquake · safety 1.3 | 22,901<br><sub>21,381–24,062</sub> | 381.7<br><sub>373.0–393.2</sub> | 374.6<br><sub>368.7–381.9</sub> | 48.2<br><sub>48.1–48.4</sub> | 733<br><sub>696–758</sub> | 86,249<br><sub>86,218–86,281</sub> | 433<br><sub>391–472</sub> | 2,980<br><sub>2,790–3,082</sub> | 387<br><sub>147–540</sub> |
| earthquake · safety 1.5 | 21,376<br><sub>20,200–22,417</sub> | 422.6<br><sub>412.8–437.0</sub> | 342.2<br><sub>337.4–347.1</sub> | 48.2<br><sub>48.1–48.4</sub> | 732<br><sub>695–757</sub> | 81,407<br><sub>69,378–85,723</sub> | 426<br><sub>385–461</sub> | 2,967<br><sub>2,778–3,076</sub> | 381<br><sub>143–534</sub> |
| earthquake · horizon 5 min | 22,954<br><sub>20,781–24,286</sub> | 396.2<br><sub>389.9–411.7</sub> | 345.0<br><sub>333.7–353.8</sub> | 48.2<br><sub>48.1–48.3</sub> | 786<br><sub>752–832</sub> | 86,190<br><sub>86,000–86,293</sub> | 450<br><sub>396–492</sub> | 2,978<br><sub>2,721–3,107</sub> | 407<br><sub>159–563</sub> |
| earthquake · horizon 30 min | 23,640<br><sub>22,328–24,559</sub> | 373.9<br><sub>364.6–384.8</sub> | 380.5<br><sub>376.1–388.0</sub> | 48.2<br><sub>48.1–48.2</sub> | 734<br><sub>696–759</sub> | 86,311<br><sub>86,302–86,330</sub> | 436<br><sub>393–476</sub> | 2,988<br><sub>2,800–3,088</sub> | 390<br><sub>149–542</sub> |
| earthquake · horizon 60 min | 22,865<br><sub>21,301–23,789</sub> | 387.1<br><sub>378.5–399.4</sub> | 370.2<br><sub>364.6–376.1</sub> | 48.2<br><sub>48.1–48.2</sub> | 733<br><sub>696–759</sub> | 86,190<br><sub>86,130–86,248</sub> | 433<br><sub>391–472</sub> | 2,985<br><sub>2,796–3,082</sub> | 388<br><sub>146–540</sub> |
| earthquake · step 5 s | 23,507<br><sub>21,727–24,831</sub> | 363.0<br><sub>356.1–372.2</sub> | 387.4<br><sub>381.2–395.9</sub> | 48.0<br><sub>48.0–48.1</sub> | 737<br><sub>701–762</sub> | 86,308<br><sub>86,260–86,356</sub> | 440<br><sub>398–481</sub> | 2,989<br><sub>2,810–3,082</sub> | 393<br><sub>153–545</sub> |
| earthquake · step 60 s | 31,277<br><sub>30,019–33,075</sub> | 346.9<br><sub>337.9–358.2</sub> | 402.3<br><sub>397.1–409.0</sub> | 48.6<br><sub>48.6–48.7</sub> | 731<br><sub>696–755</sub> | 86,533<br><sub>86,525–86,542</sub> | 444<br><sub>400–489</sub> | 2,998<br><sub>2,813–3,106</sub> | 395<br><sub>154–549</sub> |
| earthquake · scale-up step 5 | 25,560<br><sub>23,751–27,079</sub> | 354.4<br><sub>345.5–366.0</sub> | 395.6<br><sub>390.3–402.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 739<br><sub>703–764</sub> | 86,403<br><sub>86,387–86,419</sub> | 451<br><sub>408–494</sub> | 3,036<br><sub>2,852–3,163</sub> | 402<br><sub>156–559</sub> |
| earthquake · scale-up step 20 | 25,128<br><sub>23,319–26,542</sub> | 357.0<br><sub>348.1–368.6</sub> | 392.9<br><sub>387.6–399.5</sub> | 48.2<br><sub>48.1–48.3</sub> | 735<br><sub>699–761</sub> | 86,397<br><sub>86,380–86,414</sub> | 442<br><sub>399–485</sub> | 2,994<br><sub>2,811–3,092</sub> | 394<br><sub>153–547</sub> |
| earthquake · scale-up cooldown 1 min | 25,618<br><sub>23,735–27,185</sub> | 353.2<br><sub>346.6–364.1</sub> | 395.8<br><sub>388.2–403.4</sub> | 48.2<br><sub>48.1–48.3</sub> | 737<br><sub>705–761</sub> | 86,410<br><sub>86,383–86,432</sub> | 446<br><sub>405–493</sub> | 3,005<br><sub>2,834–3,092</sub> | 397<br><sub>156–548</sub> |
| earthquake · scale-up cooldown 5 min | 29,900<br><sub>27,542–30,986</sub> | 346.5<br><sub>338.4–362.9</sub> | 401.0<br><sub>394.3–406.4</sub> | 48.2<br><sub>48.1–48.3</sub> | 785<br><sub>755–816</sub> | 86,517<br><sub>86,497–86,541</sub> | 493<br><sub>452–550</sub> | 3,200<br><sub>3,029–3,295</sub> | 439<br><sub>176–579</sub> |
| earthquake · local floor 0 | 25,750<br><sub>23,940–27,015</sub> | 361.8<br><sub>352.8–373.6</sub> | 388.1<br><sub>382.9–394.6</sub> | 48.2<br><sub>48.0–48.3</sub> | 734<br><sub>698–761</sub> | 86,422<br><sub>86,397–86,436</sub> | 442<br><sub>399–489</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local floor 12 | 20,422<br><sub>19,323–21,127</sub> | 345.9<br><sub>340.0–353.1</sub> | 408.3<br><sub>400.2–415.9</sub> | 34.0<br><sub>33.4–34.7</sub> | 736<br><sub>700–761</sub> | 54,391<br><sub>52,923–55,949</sub> | 438<br><sub>398–482</sub> | 2,990<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |

### Against reference, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Local h | Wait p95 | Locate all, mean | Locate exposing, mean |
|---|---:|---:|---:|---:|---:|---:|
| workday · safety 1.0 | +115 % | -18 % | -2 % | +194 % | +21 % | +21 % |
| workday · safety 1.3 | -23 % | +33 % | +2 % | -88 % | -12 % | -12 % |
| workday · safety 1.5 | -31 % | +87 % | +3 % | -93 % | -22 % | -24 % |
| workday · horizon 5 min | +712 % | +47 % | -9 % | -7 % | +37 % | +42 % |
| workday · horizon 30 min | -22 % | +22 % | +1 % | -79 % | -10 % | -10 % |
| workday · horizon 60 min | -22 % | +36 % | +2 % | -90 % | -14 % | -15 % |
| workday · step 5 s | -2 % | +4 % | +0 % | -24 % | -1 % | -2 % |
| workday · step 60 s | +11 % | -8 % | -0 % | +34 % | +2 % | +2 % |
| workday · scale-up step 5 | +0 % | -3 % | -0 % | +4 % | +0 % | -1 % |
| workday · scale-up step 20 | +0 % | +0 % | +0 % | +0 % | +0 % | +0 % |
| workday · scale-up cooldown 1 min | +20 % | -9 % | -0 % | +39 % | +3 % | +2 % |
| workday · scale-up cooldown 5 min | +769 % | -24 % | +1 % | +140 % | +14 % | +17 % |
| workday · local floor 0 | +8 % | -0 % | +0 % | +0 % | +0 % | +0 % |
| workday · local floor 12 | -60 % | -2 % | +4 % | -7 % | -1 % | -1 % |
| rock burst · safety 1.0 | +16 % | -12 % | +3 % | +111 % | +8 % | +15 % |
| rock burst · safety 1.3 | -4 % | +18 % | -6 % | -60 % | -4 % | -7 % |
| rock burst · safety 1.5 | -5 % | +43 % | -7 % | -82 % | -8 % | -13 % |
| rock burst · horizon 5 min | -2 % | +30 % | -14 % | -79 % | +12 % | +25 % |
| rock burst · horizon 30 min | -4 % | +13 % | -4 % | -52 % | -3 % | -5 % |
| rock burst · horizon 60 min | -4 % | +20 % | -7 % | -66 % | -5 % | -8 % |
| rock burst · step 5 s | -2 % | +1 % | -0 % | -6 % | -0 % | +1 % |
| rock burst · step 60 s | +7 % | -3 % | +1 % | +21 % | +1 % | +2 % |
| rock burst · scale-up step 5 | +2 % | -1 % | +0 % | +5 % | +6 % | +4 % |
| rock burst · scale-up step 20 | -0 % | +0 % | -0 % | -0 % | +1 % | +0 % |
| rock burst · scale-up cooldown 1 min | +4 % | -3 % | +1 % | +32 % | +3 % | +4 % |
| rock burst · scale-up cooldown 5 min | +23 % | -12 % | +4 % | +105 % | +22 % | +27 % |
| rock burst · local floor 0 | +7 % | +0 % | +0 % | +111 % | -0 % | +0 % |
| rock burst · local floor 12 | -4 % | -1 % | +2 % | -31 % | +0 % | +1 % |
| earthquake · safety 1.0 | +18 % | -4 % | +2 % | +0 % | +3 % | +3 % |
| earthquake · safety 1.3 | -8 % | +7 % | -5 % | -0 % | -2 % | -2 % |
| earthquake · safety 1.5 | -14 % | +18 % | -13 % | -6 % | -4 % | -3 % |
| earthquake · horizon 5 min | -8 % | +11 % | -12 % | -0 % | +2 % | +3 % |
| earthquake · horizon 30 min | -5 % | +5 % | -3 % | -0 % | -1 % | -1 % |
| earthquake · horizon 60 min | -8 % | +8 % | -6 % | -0 % | -2 % | -2 % |
| earthquake · step 5 s | -6 % | +2 % | -1 % | -0 % | -0 % | -0 % |
| earthquake · step 60 s | +25 % | -3 % | +2 % | +0 % | +1 % | +0 % |
| earthquake · scale-up step 5 | +2 % | -1 % | +1 % | +0 % | +2 % | +2 % |
| earthquake · scale-up step 20 | +1 % | +0 % | -0 % | +0 % | +0 % | +0 % |
| earthquake · scale-up cooldown 1 min | +3 % | -1 % | +1 % | +0 % | +1 % | +1 % |
| earthquake · scale-up cooldown 5 min | +20 % | -3 % | +2 % | +0 % | +12 % | +11 % |
| earthquake · local floor 0 | +3 % | +1 % | -1 % | +0 % | +0 % | +0 % |
| earthquake · local floor 12 | -18 % | -3 % | +4 % | -37 % | -1 % | -0 % |

## What the columns mean

- **Breaches**: jobs that waited longer than the deadline of the level they were served at, measured from their deadline origin.
- **Cloud h**: cloud executor-hours of ready capacity, the billed tier.
- **Local h**: on-premise executor-hours of ready capacity — hardware the mine already owns, so these hours are not billed.
- **Drained h**: simulated hours until the queue was empty.
- **Overloads**: decisions where no capacity within both caps avoided a predicted breach, so the autoscaler ran flat out.
- **Wait p95 s**: the 95th percentile of the seconds a job waited in the queue before an executor took it.
- **Locate all, mean s**: seconds from an event to its first location, over every event.
- **Locate all, p95 s**: the 95th percentile of the seconds from an event to its first location.
- **Locate exposing**: seconds from an event that truly exposed someone to at least moderate ground motion (judged by the simulator from the truth) to its first location.
- Every figure is the mean over seeds, with the range across seeds beneath where
  the seeds disagree.

## Setup

Axes: **day** (3); **dial** (15). Each arm's own intent, settings and scenario changes are in `sweep.json`.

```json
{
  "mine": {
    "id": "workday",
    "name": "Workday mine",
    "sensors": 30,
    "background_rate_per_hour": 91,
    "description": "Calibrated to an operational seismic-processing catalogue: 30 sensors and 91 events an hour give about 1,680 pick jobs an hour, against the 1,644 an hour that catalogue averages on a typical day."
  },
  "scenario": {
    "duration_seconds": 86400,
    "job_seconds": 28,
    "pick_jitter_seconds": 0.005,
    "priority_mix": {
      "100": 22.2,
      "50": 51.0,
      "0": 26.7
    },
    "description": "A day. Job mix and duration follow the operational catalogue: 22.2 % associate (priority 100), 51.0 % locate (50) and 26.7 % pick (0), and a weighted mean execution time of 28 s."
  },
  "settings": {
    "decision_interval_seconds": 15,
    "horizon_seconds": 900,
    "simulation_step_seconds": 15,
    "deadline_seconds_by_priority": {
      "400": 30,
      "100": 60,
      "50": 300,
      "25": 43200,
      "0": 86400
    },
    "default_deadline_seconds": 86400,
    "local_executor_cap": 12,
    "cloud_executor_cap": 60,
    "min_local_executors": 1,
    "local_coldstart_seconds": 60,
    "cloud_coldstart_seconds": 180,
    "scale_up_cooldown_seconds": 0,
    "max_scale_up_step": 50,
    "local_scale_down_window_seconds": 900,
    "cloud_scale_down_window_seconds": 300,
    "cloud_min_lifetime_seconds": 600,
    "safety_factor": 1.15,
    "dry_run": false
  },
  "intent": {
    "mode": "off",
    "knowledge": "estimate",
    "pre_location": false,
    "pre_location_magnitude": 1.5,
    "protect": [
      "person",
      "crewed-vehicle",
      "autonomous-vehicle"
    ],
    "lookahead_seconds": 300,
    "protect_level": "moderate",
    "promote_level": "high",
    "margin_m": 0,
    "location_uncertainty_m": 50,
    "decay_to": -1,
    "promote_to": 400,
    "deadline_from": "arrival",
    "restore": true,
    "burst_exempt": [
      "restored"
    ]
  },
  "run": {
    "decision_interval_seconds": 15
  }
}
```

Per-seed figures, with every measured column, are in [`runs.csv`](runs.csv).

<sub>Tables rendered by platform-experiments `024b6e7d5aa2`.</sub>
