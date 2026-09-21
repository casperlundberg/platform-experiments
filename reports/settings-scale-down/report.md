# How long capacity is kept

> What do the scale-down windows and the cloud's minimum lifetime trade between cloud spend and lateness, with on-premise capacity just short of the average day and with plenty of it?

216 runs: 54 arms × 4 seeds (101, 202, 303, 404). Produced 2026-09-21T15:34:35+00:00 by autoscaler 2.0.0-dev.3+1bbd547 (`1bbd5472a9db`) and simlab-api 3.0.0 (`1dcaed0addff`), built from clean checkouts of those commits, measured by platform-experiments 1.0.0-dev.22+024b6e7 (`024b6e7d5aa2`).

Regenerate with:

```bash
make -C platform-experiments sweep S=settings-scale-down
```

At the same commits every number here comes out the same: `runs.csv` has SHA-256 `0d10e39a18dad1e1…`.

## Reading

Autoscaler 2.0 gives capacity back one scale-down window after it was last
wanted, per tier, and keeps each cloud executor for a minimum lifetime. The
reference arm is what 2.0 ships: local window 15 minutes, cloud window 5, cloud
lifetime 10. Each other arm changes one of the three, with local capacity just
short of the average day (12) and with plenty of it (24).

**The local window must never be zero, and longer is better.** Local capacity
is hardware the mine already owns.

| Breaches against the 15-minute window | local window 0 | local window 60 min |
|---|---:|---:|
| workday, local 12 | +2,069 % (16 → 352) | −26 % |
| workday, local 24 | 14 → 6,524 | −35 % |
| rock burst, local 12 / 24 | +71 % / +190 % | −4 % / −0 % |
| earthquake, local 12 / 24 | +29 % / +76 % | −11 % / −11 % |

With no window, local capacity follows each cycle's requirement down to what
the deadlines need at that moment. On a workday with 24 local executors that
turned 14 breaches into 6,524, and the 95th-percentile wait into a whole day.
An hour's window instead costs 1–17 % more local executor-hours and nothing
billed, and cuts breaches by up to 35 %.

**A longer cloud window buys shorter waits more than fewer breaches.**

| 30-minute cloud window against 5 | Cloud h | Breaches | Wait p95 |
|---|---:|---:|---:|
| workday, local 12 | +118 % | −20 % (16 → 13) | −93 % |
| rock burst, local 12 | +66 % | −5 % | −95 % |
| earthquake, local 12 | +24 % | −13 % | −64 % |
| rock burst, local 24 | +70 % | 0 % | −89 % |
| earthquake, local 24 | +32 % | −10 % | −70 % |

Held longer, cloud executors serve work that still had hours left on its
deadline, so the 95th-percentile wait falls by an order of magnitude while
breaches move 0–20 %. Sixty minutes goes further on both counts: 37–173 %
more cloud time with local 12, for 6–20 % fewer breaches. A cloud window of 0
saves up to 8 % of cloud time for up to 11 % more breaches. The minimum
lifetime is the smaller dial: with local 12, none saves 2–18 % of cloud time
for 3–5 % more breaches, and 30 minutes costs 9–72 % more for 4–20 % fewer.

**For the default:** measured against deadlines, which is what the autoscaler
is for, a 5-minute cloud window is the cheaper choice on every day, and the
breaches it gives up are small — at most 3 a workday and 13 % under the
earthquake. A 30-minute window is a runtime choice for an expected aftershock
sequence, where it takes 10–13 % off the breaches for 24–32 % more cloud
time. The local window is the opposite case: it costs nothing billed, and an
hour did as well as 15 minutes or better on every day.

**Caveats.** Four seeds, one mine, intent off. Local executor-hours are
treated as free; on an edge cluster shared with other applications they are
not.

## Results

| Arm | Breaches | Cloud h | Local h | Drained h | Overloads | Wait p95 s | Locate all, mean s | Locate all, p95 s | Locate exposing, mean s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| workday · local 12 · reference | 16<br><sub>9–30</sub> | 53.0<br><sub>50.3–57.0</sub> | 277.4<br><sub>276.5–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–2</sub> | 4,596<br><sub>2,273–8,084</sub> | 48<br><sub>47–50</sub> | 137<br><sub>135–140</sub> | 46<br><sub>42–52</sub> |
| workday · local 12 · cloud window 0 | 18<br><sub>9–30</sub> | 49.5<br><sub>46.6–54.9</sub> | 277.7<br><sub>277.0–278.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 2<br><sub>0–8</sub> | 7,130<br><sub>3,134–11,616</sub> | 49<br><sub>48–52</sub> | 139<br><sub>137–140</sub> | 47<br><sub>44–52</sub> |
| workday · local 12 · cloud window 15 min | 16<br><sub>9–30</sub> | 87.2<br><sub>76.0–98.4</sub> | 277.1<br><sub>276.2–277.9</sub> | 24.0<br><sub>24.0–24.1</sub> | 0<br><sub>0–1</sub> | 455<br><sub>404–497</sub> | 41<br><sub>40–41</sub> | 110<br><sub>106–116</sub> | 39<br><sub>35–41</sub> |
| workday · local 12 · cloud window 30 min | 13<br><sub>4–27</sub> | 115.4<br><sub>103.8–126.1</sub> | 276.9<br><sub>276.2–277.4</sub> | 24.0 | 0 | 323<br><sub>306–348</sub> | 36<br><sub>35–36</sub> | 82<br><sub>78–85</sub> | 34<br><sub>32–35</sub> |
| workday · local 12 · cloud window 60 min | 13<br><sub>4–27</sub> | 144.8<br><sub>136.2–154.2</sub> | 276.1<br><sub>275.6–276.9</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 232<br><sub>222–249</sub> | 33<br><sub>32–33</sub> | 68<br><sub>62–72</sub> | 31<br><sub>28–34</sub> |
| workday · local 12 · cloud lifetime 0 | 17<br><sub>10–30</sub> | 43.6<br><sub>38.2–47.4</sub> | 277.8<br><sub>276.8–278.5</sub> | 24.1<br><sub>24.0–24.2</sub> | 1<br><sub>0–2</sub> | 8,059<br><sub>6,441–11,283</sub> | 50<br><sub>49–53</sub> | 143<br><sub>139–147</sub> | 48<br><sub>43–54</sub> |
| workday · local 12 · cloud lifetime 30 min | 13<br><sub>4–27</sub> | 91.0<br><sub>78.1–97.3</sub> | 276.9<br><sub>276.4–277.5</sub> | 24.0 | 0 | 470<br><sub>421–526</sub> | 40 | 104<br><sub>101–108</sub> | 38<br><sub>34–40</sub> |
| workday · local 12 · local window 0 | 352<br><sub>170–812</sub> | 81.1<br><sub>75.7–86.3</sub> | 228.2<br><sub>223.4–234.1</sub> | 43.5<br><sub>40.0–48.3</sub> | 4<br><sub>2–7</sub> | 38,221<br><sub>24,431–60,940</sub> | 71<br><sub>69–74</sub> | 199<br><sub>196–207</sub> | 69<br><sub>62–78</sub> |
| workday · local 12 · local window 60 min | 12<br><sub>5–26</sub> | 51.1<br><sub>45.1–56.5</sub> | 286.0<br><sub>284.9–286.6</sub> | 24.0 | 0 | 4,731<br><sub>3,204–7,941</sub> | 47<br><sub>45–49</sub> | 132<br><sub>132–133</sub> | 44<br><sub>41–51</sub> |
| workday · local 24 · reference | 14<br><sub>7–24</sub> | 0.8<br><sub>0.6–1.0</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 405<br><sub>373–429</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud window 0 | 14<br><sub>7–24</sub> | 0.8<br><sub>0.6–1.0</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 405<br><sub>373–429</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud window 15 min | 14<br><sub>7–24</sub> | 1.4<br><sub>1.1–1.8</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 404<br><sub>372–428</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud window 30 min | 14<br><sub>7–24</sub> | 2.9<br><sub>2.3–3.7</sub> | 363.5<br><sub>355.6–372.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 397<br><sub>360–426</sub> | 39<br><sub>38–39</sub> | 99<br><sub>96–102</sub> | 36<br><sub>32–39</sub> |
| workday · local 24 · cloud window 60 min | 14<br><sub>7–24</sub> | 5.8<br><sub>4.6–7.6</sub> | 363.2<br><sub>355.3–371.6</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 391<br><sub>349–418</sub> | 38<br><sub>38–39</sub> | 97<br><sub>93–100</sub> | 36<br><sub>32–39</sub> |
| workday · local 24 · cloud lifetime 0 | 14<br><sub>7–24</sub> | 0.3<br><sub>0.2–0.4</sub> | 363.6<br><sub>355.6–372.5</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 406<br><sub>375–431</sub> | 39<br><sub>38–40</sub> | 100<br><sub>96–103</sub> | 37<br><sub>33–39</sub> |
| workday · local 24 · cloud lifetime 30 min | 14<br><sub>7–24</sub> | 2.8<br><sub>2.3–3.6</sub> | 363.6<br><sub>355.6–372.2</sub> | 24.0<br><sub>24.0–24.1</sub> | 0 | 399<br><sub>365–426</sub> | 39<br><sub>38–39</sub> | 99<br><sub>96–102</sub> | 36<br><sub>32–39</sub> |
| workday · local 24 · local window 0 | 6,524<br><sub>6,246–6,790</sub> | 3.3<br><sub>2.4–4.2</sub> | 305.8<br><sub>301.8–309.5</sub> | 48.4<br><sub>48.3–48.5</sub> | 0 | 86,503<br><sub>86,501–86,505</sub> | 98<br><sub>86–127</sub> | 212<br><sub>208–214</sub> | 89<br><sub>84–94</sub> |
| workday · local 24 · local window 60 min | 9<br><sub>4–20</sub> | 0.5<br><sub>0.2–0.7</sub> | 427.2<br><sub>416.9–445.7</sub> | 24.0 | 0 | 208<br><sub>192–221</sub> | 32<br><sub>31–32</sub> | 62<br><sub>60–64</sub> | 29<br><sub>28–32</sub> |
| rock burst · local 12 · reference | 6,338<br><sub>5,881–6,780</sub> | 133.6<br><sub>125.9–145.8</sub> | 307.2<br><sub>305.9–309.3</sub> | 47.7<br><sub>46.6–48.2</sub> | 200<br><sub>189–210</sub> | 40,625<br><sub>29,145–48,307</sub> | 132<br><sub>125–145</sub> | 977<br><sub>904–1,079</sub> | 83<br><sub>61–105</sub> |
| rock burst · local 12 · cloud window 0 | 6,825<br><sub>6,367–7,275</sub> | 124.8<br><sub>117.3–139.1</sub> | 315.8<br><sub>312.1–321.0</sub> | 48.1<br><sub>48.0–48.2</sub> | 203<br><sub>189–221</sub> | 69,725<br><sub>50,179–85,397</sub> | 137<br><sub>128–149</sub> | 977<br><sub>904–1,079</sub> | 86<br><sub>64–108</sub> |
| rock burst · local 12 · cloud window 15 min | 6,037<br><sub>5,728–6,529</sub> | 179.8<br><sub>165.7–195.0</sub> | 279.6<br><sub>278.0–280.7</sub> | 24.0 | 197<br><sub>189–208</sub> | 6,790<br><sub>5,071–8,737</sub> | 124<br><sub>118–138</sub> | 956<br><sub>904–1,070</sub> | 74<br><sub>51–97</sub> |
| rock burst · local 12 · cloud window 30 min | 6,038<br><sub>5,726–6,507</sub> | 222.2<br><sub>206.5–231.6</sub> | 279.2<br><sub>277.5–280.0</sub> | 24.0 | 197<br><sub>189–208</sub> | 2,104<br><sub>1,572–2,765</sub> | 120<br><sub>114–133</sub> | 955<br><sub>904–1,067</sub> | 71<br><sub>48–96</sub> |
| rock burst · local 12 · cloud window 60 min | 5,985<br><sub>5,711–6,433</sub> | 275.6<br><sub>262.0–285.3</sub> | 279.0<br><sub>277.0–279.9</sub> | 24.0 | 196<br><sub>186–207</sub> | 1,894<br><sub>1,334–2,566</sub> | 115<br><sub>110–128</sub> | 944<br><sub>869–1,049</sub> | 66<br><sub>43–92</sub> |
| rock burst · local 12 · cloud lifetime 0 | 6,651<br><sub>6,263–7,002</sub> | 125.5<br><sub>119.3–134.2</sub> | 312.4<br><sub>311.0–315.1</sub> | 48.1<br><sub>48.1–48.2</sub> | 199<br><sub>189–210</sub> | 58,690<br><sub>49,684–69,127</sub> | 134<br><sub>126–146</sub> | 976<br><sub>904–1,079</sub> | 85<br><sub>62–108</sub> |
| rock burst · local 12 · cloud lifetime 30 min | 6,073<br><sub>5,725–6,533</sub> | 178.2<br><sub>162.3–200.2</sub> | 280.4<br><sub>279.5–281.5</sub> | 24.2<br><sub>24.0–24.5</sub> | 198<br><sub>189–210</sub> | 14,966<br><sub>13,700–17,368</sub> | 126<br><sub>120–140</sub> | 969<br><sub>904–1,079</sub> | 77<br><sub>53–100</sub> |
| rock burst · local 12 · local window 0 | 10,839<br><sub>9,823–11,980</sub> | 154.0<br><sub>144.8–166.4</sub> | 273.0<br><sub>268.5–277.5</sub> | 48.4<br><sub>48.3–48.5</sub> | 201<br><sub>190–212</sub> | 86,479<br><sub>86,464–86,485</sub> | 147<br><sub>138–159</sub> | 983<br><sub>901–1,090</sub> | 98<br><sub>76–117</sub> |
| rock burst · local 12 · local window 60 min | 6,111<br><sub>5,744–6,533</sub> | 133.1<br><sub>125.8–144.7</sub> | 311.5<br><sub>310.1–313.0</sub> | 39.3<br><sub>37.1–43.0</sub> | 200<br><sub>189–210</sub> | 29,202<br><sub>27,806–30,035</sub> | 132<br><sub>124–144</sub> | 979<br><sub>910–1,079</sub> | 82<br><sub>61–104</sub> |
| rock burst · local 24 · reference | 5,406<br><sub>5,143–5,870</sub> | 49.7<br><sub>48.2–51.8</sub> | 400.9<br><sub>387.2–412.6</sub> | 24.0 | 153<br><sub>146–164</sub> | 12,071<br><sub>10,823–12,862</sub> | 101<br><sub>96–110</sub> | 721<br><sub>663–804</sub> | 67<br><sub>53–85</sub> |
| rock burst · local 24 · cloud window 0 | 5,456<br><sub>5,185–5,874</sub> | 45.7<br><sub>44.1–47.5</sub> | 402.1<br><sub>389.9–412.6</sub> | 24.7<br><sub>24.0–25.6</sub> | 153<br><sub>146–164</sub> | 14,491<br><sub>13,576–15,624</sub> | 102<br><sub>97–111</sub> | 721<br><sub>663–804</sub> | 67<br><sub>51–85</sub> |
| rock burst · local 24 · cloud window 15 min | 5,406<br><sub>5,143–5,870</sub> | 64.1<br><sub>63.0–64.6</sub> | 400.1<br><sub>386.6–411.8</sub> | 24.0 | 153<br><sub>146–164</sub> | 4,709<br><sub>3,491–5,444</sub> | 99<br><sub>94–107</sub> | 721<br><sub>663–804</sub> | 65<br><sub>48–84</sub> |
| rock burst · local 24 · cloud window 30 min | 5,406<br><sub>5,143–5,870</sub> | 84.5<br><sub>81.2–85.7</sub> | 399.9<br><sub>386.4–411.7</sub> | 24.0 | 153<br><sub>146–164</sub> | 1,295<br><sub>1,036–1,604</sub> | 98<br><sub>93–106</sub> | 721<br><sub>663–804</sub> | 64<br><sub>46–84</sub> |
| rock burst · local 24 · cloud window 60 min | 5,378<br><sub>5,121–5,870</sub> | 119.4<br><sub>114.8–123.7</sub> | 399.1<br><sub>385.4–411.4</sub> | 24.0 | 153<br><sub>144–164</sub> | 1,218<br><sub>1,014–1,604</sub> | 96<br><sub>92–106</sub> | 715<br><sub>663–804</sub> | 62<br><sub>45–84</sub> |
| rock burst · local 24 · cloud lifetime 0 | 5,406<br><sub>5,143–5,870</sub> | 47.3<br><sub>45.9–50.0</sub> | 401.0<br><sub>387.4–412.3</sub> | 24.1<br><sub>24.0–24.2</sub> | 153<br><sub>146–164</sub> | 13,334<br><sub>12,380–14,006</sub> | 101<br><sub>96–110</sub> | 721<br><sub>663–804</sub> | 67<br><sub>53–84</sub> |
| rock burst · local 24 · cloud lifetime 30 min | 5,406<br><sub>5,143–5,870</sub> | 60.6<br><sub>59.5–62.4</sub> | 400.1<br><sub>386.3–411.7</sub> | 24.0 | 153<br><sub>146–164</sub> | 7,896<br><sub>5,960–8,750</sub> | 100<br><sub>95–108</sub> | 721<br><sub>663–804</sub> | 66<br><sub>51–84</sub> |
| rock burst · local 24 · local window 0 | 15,686<br><sub>15,506–15,894</sub> | 65.8<br><sub>63.3–67.7</sub> | 360.7<br><sub>350.2–368.8</sub> | 48.4<br><sub>48.3–48.5</sub> | 156<br><sub>149–166</sub> | 86,558<br><sub>86,553–86,566</sub> | 144<br><sub>132–164</sub> | 737<br><sub>673–826</sub> | 107<br><sub>92–122</sub> |
| rock burst · local 24 · local window 60 min | 5,382<br><sub>5,140–5,807</sub> | 49.2<br><sub>47.9–51.4</sub> | 457.8<br><sub>446.0–470.4</sub> | 24.0 | 153<br><sub>146–163</sub> | 9,167<br><sub>8,249–10,129</sub> | 95<br><sub>90–104</sub> | 717<br><sub>663–796</sub> | 60<br><sub>45–79</sub> |
| earthquake · local 12 · reference | 24,974<br><sub>23,046–26,284</sub> | 356.9<br><sub>348.6–369.2</sub> | 393.0<br><sub>387.2–398.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,391<br><sub>86,361–86,410</sub> | 441<br><sub>399–485</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 12 · cloud window 0 | 27,163<br><sub>24,563–29,866</sub> | 345.6<br><sub>337.6–353.7</sub> | 404.1<br><sub>398.2–413.7</sub> | 48.2<br><sub>48.1–48.3</sub> | 746<br><sub>707–772</sub> | 86,448<br><sub>86,417–86,470</sub> | 452<br><sub>410–495</sub> | 2,993<br><sub>2,813–3,082</sub> | 402<br><sub>160–555</sub> |
| earthquake · local 12 · cloud window 15 min | 22,626<br><sub>21,063–23,511</sub> | 400.6<br><sub>394.7–411.6</sub> | 355.3<br><sub>346.3–364.7</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–761</sub> | 86,135<br><sub>85,975–86,201</sub> | 434<br><sub>392–471</sub> | 2,994<br><sub>2,810–3,092</sub> | 387<br><sub>145–540</sub> |
| earthquake · local 12 · cloud window 30 min | 21,604<br><sub>20,366–22,438</sub> | 441.2<br><sub>430.9–456.0</sub> | 321.9<br><sub>318.7–328.7</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>697–761</sub> | 31,315<br><sub>28,207–38,694</sub> | 430<br><sub>389–467</sub> | 2,993<br><sub>2,806–3,092</sub> | 383<br><sub>138–537</sub> |
| earthquake · local 12 · cloud window 60 min | 20,448<br><sub>19,360–21,124</sub> | 488.4<br><sub>476.3–507.9</sub> | 282.7<br><sub>279.8–287.2</sub> | 24.1<br><sub>24.0–24.3</sub> | 734<br><sub>697–761</sub> | 14,959<br><sub>13,994–15,871</sub> | 424<br><sub>387–464</sub> | 2,990<br><sub>2,806–3,079</sub> | 381<br><sub>138–533</sub> |
| earthquake · local 12 · cloud lifetime 0 | 25,624<br><sub>24,128–26,707</sub> | 349.3<br><sub>339.9–361.3</sub> | 398.8<br><sub>394.0–404.3</sub> | 48.2<br><sub>48.1–48.3</sub> | 735<br><sub>699–761</sub> | 86,415<br><sub>86,404–86,425</sub> | 443<br><sub>400–490</sub> | 2,992<br><sub>2,811–3,082</sub> | 395<br><sub>153–545</sub> |
| earthquake · local 12 · cloud lifetime 30 min | 23,254<br><sub>22,000–24,279</sub> | 390.7<br><sub>380.4–401.9</sub> | 368.8<br><sub>363.1–377.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 734<br><sub>698–762</sub> | 86,270<br><sub>86,212–86,310</sub> | 438<br><sub>396–479</sub> | 2,995<br><sub>2,811–3,092</sub> | 391<br><sub>149–543</sub> |
| earthquake · local 12 · local window 0 | 32,263<br><sub>30,226–33,445</sub> | 396.2<br><sub>389.4–409.7</sub> | 340.6<br><sub>333.3–346.9</sub> | 48.5 | 738<br><sub>704–761</sub> | 86,501<br><sub>86,492–86,515</sub> | 448<br><sub>404–495</sub> | 2,995<br><sub>2,812–3,092</sub> | 402<br><sub>162–551</sub> |
| earthquake · local 12 · local window 60 min | 22,213<br><sub>20,922–23,567</sub> | 349.6<br><sub>342.1–359.2</sub> | 403.9<br><sub>397.2–411.1</sub> | 47.9<br><sub>47.7–48.3</sub> | 735<br><sub>698–761</sub> | 86,138<br><sub>85,930–86,302</sub> | 440<br><sub>398–482</sub> | 2,991<br><sub>2,810–3,082</sub> | 394<br><sub>153–545</sub> |
| earthquake · local 24 · reference | 19,579<br><sub>18,247–20,949</sub> | 196.5<br><sub>189.7–201.7</sub> | 560.4<br><sub>552.6–575.9</sub> | 48.2<br><sub>48.1–48.2</sub> | 525<br><sub>492–547</sub> | 86,278<br><sub>86,251–86,313</sub> | 270<br><sub>242–292</sub> | 1,959<br><sub>1,826–2,018</sub> | 236<br><sub>87–343</sub> |
| earthquake · local 24 · cloud window 0 | 19,978<br><sub>18,683–21,238</sub> | 187.8<br><sub>180.2–192.6</sub> | 569.0<br><sub>562.0–584.9</sub> | 48.2<br><sub>48.1–48.3</sub> | 527<br><sub>492–547</sub> | 86,309<br><sub>86,299–86,323</sub> | 275<br><sub>246–297</sub> | 1,959<br><sub>1,826–2,018</sub> | 241<br><sub>90–346</sub> |
| earthquake · local 24 · cloud window 15 min | 18,834<br><sub>17,541–20,096</sub> | 229.8<br><sub>223.0–235.8</sub> | 527.1<br><sub>519.3–541.8</sub> | 48.2<br><sub>48.1–48.3</sub> | 525<br><sub>492–547</sub> | 85,959<br><sub>85,778–86,149</sub> | 266<br><sub>238–284</sub> | 1,959<br><sub>1,826–2,018</sub> | 233<br><sub>83–341</sub> |
| earthquake · local 24 · cloud window 30 min | 17,716<br><sub>16,472–18,714</sub> | 259.3<br><sub>247.9–271.4</sub> | 497.7<br><sub>491.7–506.1</sub> | 48.2<br><sub>48.1–48.3</sub> | 525<br><sub>492–547</sub> | 25,700<br><sub>24,372–27,719</sub> | 264<br><sub>236–281</sub> | 1,959<br><sub>1,826–2,018</sub> | 231<br><sub>81–339</sub> |
| earthquake · local 24 · cloud window 60 min | 16,848<br><sub>15,717–17,700</sub> | 298.5<br><sub>288.0–309.2</sub> | 461.3<br><sub>457.1–469.8</sub> | 24.0<br><sub>24.0–24.1</sub> | 525<br><sub>492–547</sub> | 10,057<br><sub>9,347–11,029</sub> | 258<br><sub>235–278</sub> | 1,959<br><sub>1,826–2,018</sub> | 230<br><sub>79–338</sub> |
| earthquake · local 24 · cloud lifetime 0 | 19,663<br><sub>18,217–20,855</sub> | 192.5<br><sub>185.0–198.5</sub> | 564.4<br><sub>557.2–579.0</sub> | 48.2<br><sub>48.1–48.3</sub> | 525<br><sub>492–547</sub> | 86,273<br><sub>86,245–86,289</sub> | 271<br><sub>243–293</sub> | 1,959<br><sub>1,826–2,018</sub> | 237<br><sub>87–344</sub> |
| earthquake · local 24 · cloud lifetime 30 min | 18,912<br><sub>17,820–19,964</sub> | 221.8<br><sub>206.9–228.9</sub> | 535.2<br><sub>527.9–548.6</sub> | 48.2<br><sub>48.1–48.3</sub> | 525<br><sub>492–547</sub> | 86,088<br><sub>86,024–86,130</sub> | 267<br><sub>240–287</sub> | 1,959<br><sub>1,826–2,018</sub> | 234<br><sub>84–341</sub> |
| earthquake · local 24 · local window 0 | 34,534<br><sub>32,465–36,384</sub> | 240.5<br><sub>234.2–246.0</sub> | 496.4<br><sub>488.5–510.7</sub> | 48.5 | 529<br><sub>496–549</sub> | 86,537<br><sub>86,526–86,556</sub> | 292<br><sub>260–318</sub> | 1,963<br><sub>1,830–2,014</sub> | 257<br><sub>108–361</sub> |
| earthquake · local 24 · local window 60 min | 17,519<br><sub>16,151–18,214</sub> | 195.8<br><sub>188.9–201.0</sub> | 580.4<br><sub>570.4–597.3</sub> | 48.0<br><sub>47.8–48.2</sub> | 525<br><sub>492–546</sub> | 84,670<br><sub>84,207–85,170</sub> | 268<br><sub>240–289</sub> | 1,957<br><sub>1,826–2,009</sub> | 234<br><sub>83–339</sub> |

### Against reference, at the same day and local cap

The change in each measure summed over seeds, against the reference arm on the same seeds. Totals rather than a mean of per-seed percentages, which a seed with a handful of breaches would dominate.

| Arm | Breaches | Cloud h | Local h | Wait p95 | Locate all, mean | Locate exposing, mean |
|---|---:|---:|---:|---:|---:|---:|
| workday · local 12 · cloud window 0 | +11 % | -7 % | +0 % | +55 % | +2 % | +2 % |
| workday · local 12 · cloud window 15 min | -2 % | +65 % | -0 % | -90 % | -16 % | -15 % |
| workday · local 12 · cloud window 30 min | -20 % | +118 % | -0 % | -93 % | -26 % | -27 % |
| workday · local 12 · cloud window 60 min | -20 % | +173 % | -0 % | -95 % | -32 % | -34 % |
| workday · local 12 · cloud lifetime 0 | +5 % | -18 % | +0 % | +75 % | +4 % | +5 % |
| workday · local 12 · cloud lifetime 30 min | -20 % | +72 % | -0 % | -90 % | -17 % | -18 % |
| workday · local 12 · local window 0 | +2069 % | +53 % | -18 % | +732 % | +47 % | +50 % |
| workday · local 12 · local window 60 min | -26 % | -3 % | +3 % | +3 % | -3 % | -4 % |
| workday · local 24 · cloud window 0 | +0 % | +0 % | +0 % | +0 % | +0 % | +0 % |
| workday · local 24 · cloud window 15 min | +0 % | +78 % | +0 % | -0 % | -0 % | -0 % |
| workday · local 24 · cloud window 30 min | +0 % | +266 % | -0 % | -2 % | -1 % | -1 % |
| workday · local 24 · cloud window 60 min | +0 % | +628 % | -0 % | -3 % | -1 % | -1 % |
| workday · local 24 · cloud lifetime 0 | +0 % | -62 % | +0 % | +0 % | +0 % | +0 % |
| workday · local 24 · cloud lifetime 30 min | +0 % | +244 % | -0 % | -2 % | -1 % | -1 % |
| workday · local 24 · local window 0 | +47351 % | +312 % | -16 % | +21264 % | +153 % | +141 % |
| workday · local 24 · local window 60 min | -35 % | -41 % | +17 % | -49 % | -19 % | -20 % |
| rock burst · local 12 · cloud window 0 | +8 % | -7 % | +3 % | +72 % | +3 % | +5 % |
| rock burst · local 12 · cloud window 15 min | -5 % | +35 % | -9 % | -83 % | -6 % | -10 % |
| rock burst · local 12 · cloud window 30 min | -5 % | +66 % | -9 % | -95 % | -10 % | -14 % |
| rock burst · local 12 · cloud window 60 min | -6 % | +106 % | -9 % | -95 % | -13 % | -20 % |
| rock burst · local 12 · cloud lifetime 0 | +5 % | -6 % | +2 % | +44 % | +1 % | +3 % |
| rock burst · local 12 · cloud lifetime 30 min | -4 % | +33 % | -9 % | -63 % | -5 % | -7 % |
| rock burst · local 12 · local window 0 | +71 % | +15 % | -11 % | +113 % | +11 % | +19 % |
| rock burst · local 12 · local window 60 min | -4 % | -0 % | +1 % | -28 % | -1 % | -1 % |
| rock burst · local 24 · cloud window 0 | +1 % | -8 % | +0 % | +20 % | +1 % | +0 % |
| rock burst · local 24 · cloud window 15 min | +0 % | +29 % | -0 % | -61 % | -2 % | -3 % |
| rock burst · local 24 · cloud window 30 min | +0 % | +70 % | -0 % | -89 % | -3 % | -5 % |
| rock burst · local 24 · cloud window 60 min | -1 % | +140 % | -0 % | -90 % | -4 % | -7 % |
| rock burst · local 24 · cloud lifetime 0 | +0 % | -5 % | +0 % | +10 % | +0 % | +0 % |
| rock burst · local 24 · cloud lifetime 30 min | +0 % | +22 % | -0 % | -35 % | -1 % | -1 % |
| rock burst · local 24 · local window 0 | +190 % | +32 % | -10 % | +617 % | +44 % | +60 % |
| rock burst · local 24 · local window 60 min | -0 % | -1 % | +14 % | -24 % | -5 % | -10 % |
| earthquake · local 12 · cloud window 0 | +9 % | -3 % | +3 % | +0 % | +2 % | +2 % |
| earthquake · local 12 · cloud window 15 min | -9 % | +12 % | -10 % | -0 % | -2 % | -2 % |
| earthquake · local 12 · cloud window 30 min | -13 % | +24 % | -18 % | -64 % | -3 % | -3 % |
| earthquake · local 12 · cloud window 60 min | -18 % | +37 % | -28 % | -83 % | -4 % | -3 % |
| earthquake · local 12 · cloud lifetime 0 | +3 % | -2 % | +1 % | +0 % | +0 % | +0 % |
| earthquake · local 12 · cloud lifetime 30 min | -7 % | +9 % | -6 % | -0 % | -1 % | -1 % |
| earthquake · local 12 · local window 0 | +29 % | +11 % | -13 % | +0 % | +2 % | +2 % |
| earthquake · local 12 · local window 60 min | -11 % | -2 % | +3 % | -0 % | -0 % | -0 % |
| earthquake · local 24 · cloud window 0 | +2 % | -4 % | +2 % | +0 % | +2 % | +2 % |
| earthquake · local 24 · cloud window 15 min | -4 % | +17 % | -6 % | -0 % | -2 % | -1 % |
| earthquake · local 24 · cloud window 30 min | -10 % | +32 % | -11 % | -70 % | -3 % | -2 % |
| earthquake · local 24 · cloud window 60 min | -14 % | +52 % | -18 % | -88 % | -5 % | -3 % |
| earthquake · local 24 · cloud lifetime 0 | +0 % | -2 % | +1 % | -0 % | +0 % | +0 % |
| earthquake · local 24 · cloud lifetime 30 min | -3 % | +13 % | -4 % | -0 % | -1 % | -1 % |
| earthquake · local 24 · local window 0 | +76 % | +22 % | -11 % | +0 % | +8 % | +9 % |
| earthquake · local 24 · local window 60 min | -11 % | -0 % | +4 % | -2 % | -1 % | -1 % |

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

Axes: **day** (3); **local cap** (2); **holding** (9). Each arm's own intent, settings and scenario changes are in `sweep.json`.

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
