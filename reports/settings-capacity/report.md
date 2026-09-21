# Local and cloud capacity on three kinds of day

> How much on-premise and cloud capacity does each kind of day need, and what does each executor of it buy? The calibrated day asks for about 13 executors on average, so 12 local executors are just short of it.

192 runs: 48 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-21T14:56:32+00:00 by autoscaler 2.0.0-dev.3+1bbd547 (`1bbd5472a9db`) and simlab-api 3.0.0 (`1dcaed0addff`), built from clean checkouts of those commits, measured by platform-experiments 1.0.0-dev.22+024b6e7 (`024b6e7d5aa2`).

Regenerate with:

```bash
make -C platform-experiments sweep S=settings-capacity
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `68532bd0a571de59…`.

## Reading

The calibrated mine asks for about 13 executors on average — 1,680 jobs an hour
at 28 s each ([`docs/calibration.md`](../docs/calibration.md)). Four local caps
around that, against four cloud caps, on the three days, with intent off and
every other setting pinned. The comparison table below is against the
calibrated 12 local and 60 cloud on the same day.

**On a normal day, local capacity decides the day, and the cloud cap hardly
matters.**

| Workday | Breaches | Cloud h | Wait p95 |
|---|---:|---:|---:|
| local 12, no cloud | 9,595 | 0 | 83,634 s |
| local 12, cloud 20 to 200 | 16 | 51–54 | 4,596–5,025 s |
| local 16, no cloud | 40 | 0 | 8,446 s |
| local 16, cloud 20 to 200 | 15 | 18.4 | 1,110 s |
| local 24, any cloud | 14 | 0–0.8 | 405 s |

Twelve local executors are just short of the average, so the day runs on cloud
— 53 cloud-hours, bought all day — and without cloud the backlog grows all day
and takes another to clear. A third more local hardware (16) cuts the cloud to
18 hours; twice as much (24) to under one. Above 20, the cloud cap changes
nothing on a workday: it is never what binds. The floor of 14–16 breaches is
the day's own cold start; the coldstart sweep takes it to 4 with local
executors that start at once.

**Under a burst, the cloud cap decides the breaches, and local capacity the
bill.**

| Breaches / cloud h | cloud 20 | cloud 60 | cloud 200 |
|---|---:|---:|---:|
| rock burst, local 12 | 12,100 / 121 | 6,338 / 134 | 2,347 / 145 |
| rock burst, local 24 | 8,568 / 42 | 5,406 / 50 | 2,168 / 59 |
| earthquake, local 12 | 55,786 / 337 | 24,974 / 357 | 4,516 / 368 |
| earthquake, local 24 | 38,760 / 170 | 19,579 / 197 | 3,129 / 208 |

Each step up in cloud cap takes 37–84 % off the breaches for 3–20 % more
cloud-hours: the extra executors are held only while the burst lasts. Doubling
local capacity takes 43–66 % off the cloud bill and 8–31 % off the breaches.
At the earthquake's peak even 224 executors are short: 13–17 overload
decisions remain at cloud 200.

**Low-priority work waits for its deadline, not for capacity.** Under the
earthquake, with any cloud at all, the 95th-percentile wait is within minutes
of a day (86,195–87,268 s), and every run takes 48 hours to drain. Priority 0's
deadline is 24 hours, and the autoscaler buys capacity to meet deadlines, not
to empty the queue. With 24 local executors it held 11 of them on average
(549 local-hours over 48): hardware the mine owns stood idle while work waited
for it. The scale-down and engine sweeps measure what holding it would have
done.

**For a mine:** size the local tier at or above the average day's demand — 16
or more against 13 here — and set the cloud cap by the bursts it has to
survive, since a normal day never reaches it.

**Caveats.** Four seeds, one mine, intent off, and the autoscaler's shipped
deadlines. Demand here is the calibrated catalogue's; a mine with a different
job mix or duration needs its own average.

## Results

| Arm | Breaches | Cloud h | Local h | Drained h | Overloads | Wait p95 s | Locate all, mean s | Locate all, p95 s | Locate exposing, mean s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · local 8 · cloud 0 | 21,493<br><sub>20,159–22,585</sub> | 0.0 | 309.4<br><sub>304.6–313.4</sub> | 48.1<br><sub>48.0–48.2</sub> | 6,727<br><sub>6,406–6,994</sub> | 86,830<br><sub>86,468–87,452</sub> | 6,178<br><sub>5,457–6,642</sub> | 25,956<br><sub>23,263–27,187</sub> | 5,993<br><sub>4,509–7,117</sub> |
| workday · local 8 · cloud 20 | 34<br><sub>26–47</sub> | 118.0<br><sub>110.3–121.4</sub> | 196.2<br><sub>193.0–198.1</sub> | 27.1<br><sub>24.2–28.9</sub> | 12<br><sub>4–23</sub> | 10,714<br><sub>8,924–13,395</sub> | 55<br><sub>53–59</sub> | 164<br><sub>161–170</sub> | 52<br><sub>46–58</sub> |
| workday · local 8 · cloud 60 | 32<br><sub>26–42</sub> | 127.1<br><sub>117.9–134.3</sub> | 192.4<br><sub>191.3–194.9</sub> | 24.4<br><sub>24.0–25.7</sub> | 4<br><sub>0–9</sub> | 6,162<br><sub>3,651–10,736</sub> | 55<br><sub>53–57</sub> | 163<br><sub>160–172</sub> | 52<br><sub>46–57</sub> |
| workday · local 8 · cloud 200 | 32<br><sub>26–42</sub> | 131.8<br><sub>122.0–144.5</sub> | 192.4<br><sub>191.3–194.9</sub> | 24.4<br><sub>24.0–25.7</sub> | 0 | 6,161<br><sub>3,650–10,736</sub> | 55<br><sub>53–57</sub> | 163<br><sub>159–172</sub> | 52<br><sub>46–57</sub> |
| workday · local 12 · cloud 0 | 9,595<br><sub>6,818–10,975</sub> | 0.0 | 316.1<br><sub>311.1–319.0</sub> | 48.2<br><sub>48.0–48.4</sub> | 2,268<br><sub>1,766–2,518</sub> | 83,634<br><sub>77,006–85,902</sub> | 345<br><sub>119–522</sub> | 2,088<br><sub>550–3,183</sub> | 364<br><sub>125–604</sub> |
| workday · local 12 · cloud 20 | 16<br><sub>9–30</sub> | 50.9<br><sub>45.4–53.5</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 2<br><sub>0–5</sub> | 5,025<br><sub>3,156–8,084</sub> | 48<br><sub>47–51</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local 12 · cloud 60 | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local 12 · cloud 200 | 16<br><sub>9–30</sub> | 53.9<br><sub>51.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local 16 · cloud 0 | 40<br><sub>20–89</sub> | 0.0 | 330.1<br><sub>327.3–333.0</sub> | 24.0<br><sub>24.0–24.1</sub> | 151<br><sub>116–199</sub> | 8,446<br><sub>4,597–11,210</sub> | 47<br><sub>45–52</sub> | 126<br><sub>117–133</sub> | 45<br><sub>41–49</sub> |
| workday · local 16 · cloud 20 | 15<br><sub>7–30</sub> | 18.4<br><sub>15.5–20.5</sub> | 329.9<br><sub>327.2–332.8</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 1,110<br><sub>493–2,672</sub> | 42<br><sub>41–42</sub> | 109<br><sub>106–110</sub> | 40<br><sub>36–44</sub> |
| workday · local 16 · cloud 60 | 15<br><sub>7–30</sub> | 18.4<br><sub>15.5–20.5</sub> | 329.9<br><sub>327.2–332.8</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 1,110<br><sub>493–2,672</sub> | 42<br><sub>41–42</sub> | 109<br><sub>106–110</sub> | 40<br><sub>36–44</sub> |
| workday · local 16 · cloud 200 | 15<br><sub>7–30</sub> | 18.4<br><sub>15.5–20.5</sub> | 329.9<br><sub>327.2–332.8</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 1,110<br><sub>493–2,672</sub> | 42<br><sub>41–42</sub> | 109<br><sub>106–110</sub> | 40<br><sub>36–44</sub> |
| workday · local 24 · cloud 0 | 14<br><sub>7–24</sub> | 0.0 | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 407<br><sub>377–433</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud 20 | 14<br><sub>7–24</sub> | 0.8<br><sub>0.6–1.0</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 405<br><sub>373–429</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud 60 | 14<br><sub>7–24</sub> | 0.8<br><sub>0.6–1.0</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 405<br><sub>373–429</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud 200 | 14<br><sub>7–24</sub> | 0.8<br><sub>0.6–1.0</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 405<br><sub>373–429</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| rock burst · local 8 · cloud 0 | 45,276<br><sub>43,821–46,903</sub> | 0.0 | 426.7<br><sub>418.0–435.3</sub> | 53.4<br><sub>52.3–54.5</sub> | 12,035<br><sub>11,619–12,441</sub> | 129,055<br><sub>126,010–132,510</sub> | 19,735<br><sub>18,955–20,292</sub> | 63,478<br><sub>61,525–65,820</sub> | 17,152<br><sub>14,852–21,604</sub> |
| rock burst · local 8 · cloud 20 | 14,435<br><sub>14,165–14,667</sub> | 190.2<br><sub>181.4–200.7</sub> | 242.6<br><sub>239.6–244.1</sub> | 48.1<br><sub>48.0–48.2</sub> | 1,112<br><sub>1,098–1,133</sub> | 86,130<br><sub>85,994–86,194</sub> | 806<br><sub>754–911</sub> | 5,546<br><sub>5,321–6,105</sub> | 579<br><sub>464–650</sub> |
| rock burst · local 8 · cloud 60 | 6,812<br><sub>6,337–7,461</sub> | 211.4<br><sub>194.7–225.9</sub> | 222.9<br><sub>217.7–230.8</sub> | 48.1<br><sub>48.0–48.2</sub> | 220<br><sub>210–231</sub> | 55,612<br><sub>35,014–85,540</sub> | 148<br><sub>139–163</sub> | 1,095<br><sub>1,028–1,214</sub> | 93<br><sub>67–114</sub> |
| rock burst · local 8 · cloud 200 | 2,518<br><sub>2,255–2,843</sub> | 222.6<br><sub>205.9–239.8</sub> | 212.8<br><sub>208.5–219.6</sub> | 43.2<br><sub>39.4–48.0</sub> | 35<br><sub>32–37</sub> | 29,845<br><sub>21,734–48,035</sub> | 65<br><sub>62–67</sub> | 208<br><sub>200–219</sub> | 63<br><sub>59–70</sub> |
| rock burst · local 12 · cloud 0 | 31,897<br><sub>31,062–32,847</sub> | 0.0 | 434.8<br><sub>428.4–441.3</sub> | 48.1<br><sub>48.0–48.2</sub> | 5,852<br><sub>5,690–6,114</sub> | 88,307<br><sub>87,905–88,718</sub> | 9,007<br><sub>8,877–9,092</sub> | 31,688<br><sub>31,309–32,659</sub> | 7,847<br><sub>6,388–9,854</sub> |
| rock burst · local 12 · cloud 20 | 12,100<br><sub>11,825–12,439</sub> | 120.6<br><sub>114.4–128.4</sub> | 319.1<br><sub>317.5–321.4</sub> | 48.1<br><sub>48.0–48.2</sub> | 819<br><sub>810–832</sub> | 80,807<br><sub>75,724–85,574</sub> | 572<br><sub>536–651</sub> | 4,358<br><sub>4,184–4,784</sub> | 360<br><sub>293–433</sub> |
| rock burst · local 12 · cloud 60 | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 307.2<br><sub>305.9–309.3</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 40,625<br><sub>29,145–48,307</sub> | 132<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–105</sub> |
| rock burst · local 12 · cloud 200 | 2,347<br><sub>2,210–2,577</sub> | 145.0<br><sub>136.4–161.1</sub> | 297.0<br><sub>295.4–299.2</sub> | 39.3<br><sub>36.2–42.2</sub> | 34<br><sub>32–36</sub> | 22,681<br><sub>20,522–24,189</sub> | 60<br><sub>58–63</sub> | 196<br><sub>190–203</sub> | 58<br><sub>55–62</sub> |
| rock burst · local 16 · cloud 0 | 26,700<br><sub>25,743–28,058</sub> | 0.0 | 442.9<br><sub>434.7–450.8</sub> | 48.1<br><sub>48.0–48.2</sub> | 3,713<br><sub>3,552–3,865</sub> | 86,360<br><sub>86,312–86,414</sub> | 4,371<br><sub>4,292–4,491</sub> | 16,932<br><sub>16,632–17,221</sub> | 3,770<br><sub>2,911–4,741</sub> |
| rock burst · local 16 · cloud 20 | 10,200<br><sub>10,030–10,278</sub> | 80.0<br><sub>75.5–85.3</sub> | 365.0<br><sub>360.4–368.2</sub> | 46.3<br><sub>44.1–47.9</sub> | 645<br><sub>633–656</sub> | 32,103<br><sub>28,334–36,155</sub> | 434<br><sub>404–505</sub> | 3,495<br><sub>3,366–3,835</sub> | 258<br><sub>183–329</sub> |
| rock burst · local 16 · cloud 60 | 5,851<br><sub>5,499–6,276</sub> | 89.7<br><sub>85.6–95.2</sub> | 355.4<br><sub>350.3–359.0</sub> | 37.0<br><sub>34.9–39.2</sub> | 182<br><sub>173–192</sub> | 22,611<br><sub>22,240–23,642</sub> | 120<br><sub>113–130</sub> | 883<br><sub>792–1,002</sub> | 76<br><sub>59–96</sub> |
| rock burst · local 16 · cloud 200 | 2,270<br><sub>2,065–2,520</sub> | 99.5<br><sub>95.5–105.0</sub> | 345.7<br><sub>340.4–349.2</sub> | 27.2<br><sub>24.9–29.6</sub> | 31<br><sub>29–34</sub> | 15,374<br><sub>14,900–16,026</sub> | 57<br><sub>54–59</sub> | 187<br><sub>183–191</sub> | 54<br><sub>50–58</sub> |
| rock burst · local 24 · cloud 0 | 16,836<br><sub>16,233–17,462</sub> | 0.0 | 447.2<br><sub>437.4–456.3</sub> | 48.1<br><sub>48.0–48.2</sub> | 1,584<br><sub>1,542–1,670</sub> | 70,442<br><sub>62,108–77,227</sub> | 1,210<br><sub>1,151–1,332</sub> | 7,304<br><sub>7,057–7,837</sub> | 944<br><sub>637–1,140</sub> |
| rock burst · local 24 · cloud 20 | 8,568<br><sub>8,132–9,309</sub> | 41.5<br><sub>41.0–42.3</sub> | 406.0<br><sub>395.1–415.8</sub> | 27.0<br><sub>24.6–29.3</sub> | 447<br><sub>433–481</sub> | 16,787<br><sub>15,898–18,221</sub> | 281<br><sub>261–334</sub> | 2,389<br><sub>2,276–2,644</sub> | 160<br><sub>113–222</sub> |
| rock burst · local 24 · cloud 60 | 5,406<br><sub>5,143–5,870</sub> | 49.7<br><sub>48.2–51.8</sub> | 400.9<br><sub>387.2–412.6</sub> | 24.0 | 153<br><sub>146–164</sub> | 12,071<br><sub>10,823–12,862</sub> | 101<br><sub>96–110</sub> | 721<br><sub>663–804</sub> | 67<br><sub>53–85</sub> |
| rock burst · local 24 · cloud 200 | 2,168<br><sub>1,941–2,489</sub> | 59.1<br><sub>57.3–61.0</sub> | 400.7<br><sub>387.1–411.9</sub> | 24.0 | 24<br><sub>19–30</sub> | 6,668<br><sub>5,717–7,491</sub> | 52<br><sub>50–54</sub> | 172<br><sub>159–182</sub> | 49<br><sub>46–55</sub> |
| earthquake · local 8 · cloud 0 | 89,454<br><sub>87,722–93,173</sub> | 0.0 | 737.6<br><sub>723.3–756.7</sub> | 92.3<br><sub>90.5–94.6</sub> | 21,390<br><sub>20,980–22,320</sub> | 254,217<br><sub>248,611–261,968</sub> | 54,084<br><sub>53,115–54,964</sub> | 157,236<br><sub>154,195–160,501</sub> | 54,106<br><sub>39,234–65,198</sub> |
| earthquake · local 8 · cloud 20 | 61,877<br><sub>59,855–63,526</sub> | 434.6<br><sub>426.2–448.7</sub> | 308.4<br><sub>303.9–312.5</sub> | 48.2<br><sub>48.1–48.3</sub> | 4,587<br><sub>4,476–4,715</sub> | 87,268<br><sub>87,148–87,349</sub> | 6,986<br><sub>6,686–7,264</sub> | 23,982<br><sub>22,933–24,916</sub> | 6,893<br><sub>4,344–8,594</sub> |
| earthquake · local 8 · cloud 60 | 27,871<br><sub>25,756–29,390</sub> | 455.6<br><sub>448.8–469.3</sub> | 288.2<br><sub>283.9–292.4</sub> | 48.2<br><sub>48.1–48.3</sub> | 826<br><sub>785–854</sub> | 86,439<br><sub>86,422–86,465</sub> | 528<br><sub>480–577</sub> | 3,452<br><sub>3,245–3,577</sub> | 480<br><sub>207–650</sub> |
| earthquake · local 8 · cloud 200 | 5,588<br><sub>4,341–6,435</sub> | 464.2<br><sub>459.0–476.9</sub> | 279.6<br><sub>273.7–284.8</sub> | 48.2<br><sub>48.1–48.3</sub> | 17<br><sub>15–19</sub> | 86,393<br><sub>86,361–86,421</sub> | 62<br><sub>55–72</sub> | 171<br><sub>166–175</sub> | 57<br><sub>54–62</sub> |
| earthquake · local 12 · cloud 0 | 81,046<br><sub>78,896–83,276</sub> | 0.0 | 745.8<br><sub>730.7–763.0</sub> | 62.6<br><sub>61.4–63.8</sub> | 13,226<br><sub>12,973–13,554</sub> | 157,262<br><sub>153,832–160,904</sub> | 30,339<br><sub>29,557–31,092</sub> | 89,576<br><sub>87,301–91,655</sub> | 30,177<br><sub>20,362–37,264</sub> |
| earthquake · local 12 · cloud 20 | 55,786<br><sub>53,187–58,637</sub> | 337.2<br><sub>327.3–349.1</sub> | 412.7<br><sub>408.5–419.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 3,662<br><sub>3,528–3,851</sub> | 86,594<br><sub>86,542–86,673</sub> | 4,969<br><sub>4,728–5,197</sub> | 18,437<br><sub>17,545–19,162</sub> | 4,855<br><sub>3,042–5,988</sub> |
| earthquake · local 12 · cloud 60 | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 393.0<br><sub>387.2–398.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,391<br><sub>86,361–86,410</sub> | 441<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 12 · cloud 200 | 4,516<br><sub>3,588–5,415</sub> | 367.7<br><sub>360.9–377.4</sub> | 382.2<br><sub>374.8–390.8</sub> | 48.2<br><sub>48.1–48.3</sub> | 17<br><sub>15–20</sub> | 86,344<br><sub>86,313–86,374</sub> | 60<br><sub>53–71</sub> | 164<br><sub>162–166</sub> | 55<br><sub>48–62</sub> |
| earthquake · local 16 · cloud 0 | 76,859<br><sub>74,606–78,822</sub> | 0.0 | 753.1<br><sub>738.6–772.4</sub> | 48.7<br><sub>47.7–49.6</sub> | 9,744<br><sub>9,503–9,987</sub> | 114,034<br><sub>111,397–116,737</sub> | 19,755<br><sub>19,213–20,261</sub> | 59,572<br><sub>57,830–61,025</sub> | 19,628<br><sub>13,016–24,492</sub> |
| earthquake · local 16 · cloud 20 | 48,542<br><sub>46,252–50,668</sub> | 262.0<br><sub>252.4–273.5</sub> | 492.9<br><sub>487.9–501.5</sub> | 48.2<br><sub>48.1–48.3</sub> | 2,863<br><sub>2,780–2,959</sub> | 86,455<br><sub>86,442–86,477</sub> | 3,598<br><sub>3,392–3,776</sub> | 14,497<br><sub>13,701–15,061</sub> | 3,512<br><sub>2,165–4,415</sub> |
| earthquake · local 16 · cloud 60 | 22,758<br><sub>21,119–24,121</sub> | 285.6<br><sub>279.0–295.4</sub> | 469.3<br><sub>461.3–479.6</sub> | 48.2<br><sub>48.1–48.3</sub> | 654<br><sub>618–677</sub> | 86,342<br><sub>86,298–86,370</sub> | 372<br><sub>334–406</sub> | 2,604<br><sub>2,385–2,714</sub> | 325<br><sub>114–462</sub> |
| earthquake · local 16 · cloud 200 | 3,886<br><sub>3,246–4,609</sub> | 297.2<br><sub>290.4–306.1</sub> | 457.6<br><sub>449.9–468.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 14<br><sub>12–16</sub> | 86,304<br><sub>86,288–86,320</sub> | 58<br><sub>52–68</sub> | 157<br><sub>153–161</sub> | 51<br><sub>44–59</sub> |
| earthquake · local 24 · cloud 0 | 62,110<br><sub>59,772–64,498</sub> | 0.0 | 756.9<br><sub>742.2–777.5</sub> | 48.2<br><sub>48.1–48.2</sub> | 5,460<br><sub>5,310–5,628</sub> | 87,751<br><sub>87,565–88,008</sub> | 9,740<br><sub>9,384–10,044</sub> | 31,992<br><sub>30,795–33,128</sub> | 9,658<br><sub>6,188–12,094</sub> |
| earthquake · local 24 · cloud 20 | 38,760<br><sub>37,045–40,281</sub> | 170.0<br><sub>162.2–175.4</sub> | 586.9<br><sub>580.0–602.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 1,969<br><sub>1,888–2,032</sub> | 86,355<br><sub>86,331–86,376</sub> | 2,002<br><sub>1,873–2,134</sub> | 9,494<br><sub>8,901–9,867</sub> | 1,955<br><sub>1,225–2,493</sub> |
| earthquake · local 24 · cloud 60 | 19,579<br><sub>18,247–20,949</sub> | 196.5<br><sub>189.7–201.7</sub> | 560.4<br><sub>552.6–575.9</sub> | 48.2<br><sub>48.1–48.2</sub> | 525<br><sub>492–547</sub> | 86,278<br><sub>86,251–86,313</sub> | 270<br><sub>242–292</sub> | 1,959<br><sub>1,826–2,018</sub> | 236<br><sub>87–343</sub> |
| earthquake · local 24 · cloud 200 | 3,129<br><sub>2,672–3,550</sub> | 207.9<br><sub>200.3–213.4</sub> | 548.9<br><sub>541.9–564.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 13<br><sub>11–15</sub> | 86,195<br><sub>86,079–86,261</sub> | 55<br><sub>48–65</sub> | 143<br><sub>140–146</sub> | 48<br><sub>42–56</sub> |

### Against local 12 · cloud 60, at the same day

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Local h | Wait p95 | Locate all, mean | Locate exposing, mean |
|---|---:|---:|---:|---:|---:|---:|
| workday · local 8 · cloud 0 | +132163 % | -100 % | +12 % | +1789 % | +12718 % | +12899 % |
| workday · local 8 · cloud 20 | +106 % | +123 % | -29 % | +133 % | +15 % | +12 % |
| workday · local 8 · cloud 60 | +100 % | +140 % | -31 % | +34 % | +14 % | +12 % |
| workday · local 8 · cloud 200 | +100 % | +149 % | -31 % | +34 % | +14 % | +12 % |
| workday · local 12 · cloud 0 | +58946 % | -100 % | +14 % | +1720 % | +616 % | +689 % |
| workday · local 12 · cloud 20 | +0 % | -4 % | +0 % | +9 % | +0 % | -0 % |
| workday · local 12 · cloud 200 | +0 % | +2 % | +0 % | +0 % | +0 % | +0 % |
| workday · local 16 · cloud 0 | +148 % | -100 % | +19 % | +84 % | -2 % | -3 % |
| workday · local 16 · cloud 20 | -6 % | -65 % | +19 % | -76 % | -13 % | -13 % |
| workday · local 16 · cloud 60 | -6 % | -65 % | +19 % | -76 % | -13 % | -13 % |
| workday · local 16 · cloud 200 | -6 % | -65 % | +19 % | -76 % | -13 % | -13 % |
| workday · local 24 · cloud 0 | -15 % | -100 % | +31 % | -91 % | -19 % | -20 % |
| workday · local 24 · cloud 20 | -15 % | -98 % | +31 % | -91 % | -19 % | -20 % |
| workday · local 24 · cloud 60 | -15 % | -98 % | +31 % | -91 % | -19 % | -20 % |
| workday · local 24 · cloud 200 | -15 % | -98 % | +31 % | -91 % | -19 % | -20 % |
| rock burst · local 8 · cloud 0 | +614 % | -100 % | +39 % | +218 % | +14795 % | +20653 % |
| rock burst · local 8 · cloud 20 | +128 % | +42 % | -21 % | +112 % | +509 % | +601 % |
| rock burst · local 8 · cloud 60 | +7 % | +58 % | -27 % | +37 % | +11 % | +12 % |
| rock burst · local 8 · cloud 200 | -60 % | +67 % | -31 % | -27 % | -51 % | -24 % |
| rock burst · local 12 · cloud 0 | +403 % | -100 % | +41 % | +117 % | +6698 % | +9394 % |
| rock burst · local 12 · cloud 20 | +91 % | -10 % | +4 % | +99 % | +332 % | +335 % |
| rock burst · local 12 · cloud 200 | -63 % | +9 % | -3 % | -44 % | -54 % | -30 % |
| rock burst · local 16 · cloud 0 | +321 % | -100 % | +44 % | +113 % | +3199 % | +4461 % |
| rock burst · local 16 · cloud 20 | +61 % | -40 % | +19 % | -21 % | +228 % | +212 % |
| rock burst · local 16 · cloud 60 | -8 % | -33 % | +16 % | -44 % | -10 % | -8 % |
| rock burst · local 16 · cloud 200 | -64 % | -26 % | +13 % | -62 % | -57 % | -34 % |
| rock burst · local 24 · cloud 0 | +166 % | -100 % | +46 % | +73 % | +814 % | +1042 % |
| rock burst · local 24 · cloud 20 | +35 % | -69 % | +32 % | -59 % | +112 % | +93 % |
| rock burst · local 24 · cloud 60 | -15 % | -63 % | +30 % | -70 % | -24 % | -19 % |
| rock burst · local 24 · cloud 200 | -66 % | -56 % | +30 % | -84 % | -60 % | -40 % |
| earthquake · local 8 · cloud 0 | +258 % | -100 % | +88 % | +194 % | +12152 % | +13639 % |
| earthquake · local 8 · cloud 20 | +148 % | +22 % | -22 % | +1 % | +1483 % | +1650 % |
| earthquake · local 8 · cloud 60 | +12 % | +28 % | -27 % | +0 % | +20 % | +22 % |
| earthquake · local 8 · cloud 200 | -78 % | +30 % | -29 % | +0 % | -86 % | -85 % |
| earthquake · local 12 · cloud 0 | +225 % | -100 % | +90 % | +82 % | +6773 % | +7563 % |
| earthquake · local 12 · cloud 20 | +123 % | -6 % | +5 % | +0 % | +1026 % | +1133 % |
| earthquake · local 12 · cloud 200 | -82 % | +3 % | -3 % | -0 % | -86 % | -86 % |
| earthquake · local 16 · cloud 0 | +208 % | -100 % | +92 % | +32 % | +4375 % | +4884 % |
| earthquake · local 16 · cloud 20 | +94 % | -27 % | +25 % | +0 % | +715 % | +792 % |
| earthquake · local 16 · cloud 60 | -9 % | -20 % | +19 % | -0 % | -16 % | -18 % |
| earthquake · local 16 · cloud 200 | -84 % | -17 % | +16 % | -0 % | -87 % | -87 % |
| earthquake · local 24 · cloud 0 | +149 % | -100 % | +93 % | +2 % | +2106 % | +2352 % |
| earthquake · local 24 · cloud 20 | +55 % | -52 % | +49 % | -0 % | +354 % | +396 % |
| earthquake · local 24 · cloud 60 | -22 % | -45 % | +43 % | -0 % | -39 % | -40 % |
| earthquake · local 24 · cloud 200 | -87 % | -42 % | +40 % | -0 % | -88 % | -88 % |

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

Axes: **day** (3); **local cap** (4); **cloud cap** (4). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
