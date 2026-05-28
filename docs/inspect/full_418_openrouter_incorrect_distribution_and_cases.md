# Full 418 OpenRouter Incorrect Distribution and Hard Cases

Source run: `outputs/final_result/full_418_openrouter_2026_05_26/full_418_judged_1_round`.

Definition used here: only judge grade `INCORRECT` counts as a wrong answer. `NOT_ATTEMPTED` does not count as wrong in this report.

## Summary

- Questions analyzed: 418
- Tested models per question: 9
- Judged prediction files: 45
- Records with missing model grades: 0

### Distribution by number of incorrect models

| Incorrect model count | Question count | Share of 418 |
| ---: | ---: | ---: |
| 0 | 12 | 2.9% |
| 1 | 23 | 5.5% |
| 2 | 36 | 8.6% |
| 3 | 28 | 6.7% |
| 4 | 49 | 11.7% |
| 5 | 69 | 16.5% |
| 6 | 58 | 13.9% |
| 7 | 66 | 15.8% |
| 8 | 52 | 12.4% |
| 9 | 25 | 6.0% |

### 9/9 incorrect count by answer type

| Answer type | 9/9 incorrect questions | Total questions | Share within type |
| --- | ---: | ---: | ---: |
| Date | 7 | 93 | 7.5% |
| Number | 4 | 77 | 5.2% |
| Other | 4 | 104 | 3.8% |
| Person | 4 | 83 | 4.8% |
| Place | 6 | 61 | 9.8% |

## Case Samples

Selection rule: each answer type shows 10 cases sorted by the number of `INCORRECT` models descending, then by dataset id. This prioritizes 9/9 failures; because every answer type has fewer than 10 such cases, the remaining slots are filled by 8/9, 7/9, etc. Model outputs are truncated for compact reading; full text remains in the JSONL outputs.

## Date

| Selected case | Incorrect models | Correct models | Not attempted |
| --- | ---: | ---: | ---: |
| `date_11` | 9/9 | 0 | 0 |
| `date_20` | 9/9 | 0 | 0 |
| `date_23` | 9/9 | 0 | 0 |
| `date_39` | 9/9 | 0 | 0 |
| `date_47` | 9/9 | 0 | 0 |
| `date_53` | 9/9 | 0 | 0 |
| `date_87` | 9/9 | 0 | 0 |
| `date_2` | 8/9 | 1 | 0 |
| `date_7` | 8/9 | 0 | 1 |
| `date_14` | 8/9 | 0 | 1 |

### Date Case 1: `date_11` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Mandate_for_Syria_and_the_Lebanon
- Question: On what month, day, and year did Subhi Bay Barakat al-Khalidi start his term as Head of State under the Mandate for Syria and the Lebanon?
- Gold answer: **January 1, 1925**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=6; section=Heads of State`

| Name | Term start | Term end | Political Party |
| --- | --- | --- | --- |
| Name | Term start | Term end | Political Party |
| Subhi Bay Barakat al-Khalidi | 1 January 1925 | 21 December 1925 |  |
| François Pierre-Alype (acting) | 9 February 1926 | 28 April 1926 |  |
| Damad-i Shariyari Ahmad Nami Bay | 28 April 1926 | 15 February 1928 |  |
| Taj al-Din al-Hasani (acting) | 15 February 1928 | 19 November 1931 |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Subhi Barakat al-Khalidi began his term as Head of State under the Mandate for Syria and the Lebanon on **June 28, 1922**, when he became President of the Syrian Federation, which had been established by the French... |
| deepseek-v4-pro | Subhi Bey Barakat al-Khalidi began his term as the local Head of State under the French Mandate on **June 29, 1922**. He assumed office as the President of the Syrian Federation, an administrative entity created by... |
| gemini-3.1-pro-preview | Subhi Bey Barakat al-Khalidi began his term as Head of State (specifically as the President of the Syrian Federation, under the French Mandate) on **June 28, 1922**. He later continued his role as Head of State whe... |
| minimax-m2.7 | Subhi Bay Barakat al‑Khalidi began his term as Head of State under the Mandate for Syria and the Lebanon on **June 1, 1925**. |
| kimi-k2.6 | Subhi Bay Barakat al-Khalidi began his term as Head of State of the Syrian Federation under the Mandate for Syria and the Lebanon on **June 28, 1922**. |
| gpt-5.5 | Subhi Bay Barakat al-Khalidi started his term as Head of State on **June 29, 1922**. |
| qwen3.5-397b-a17b | Subhi Bey Barakat al-Khalidi (often spelled Subhi Bay Barakat in some transliterations) started his term as the head of the Syrian political entity under the French Mandate on **June 28, 1922**. On this date, the *... |
| mimo-v2.5-pro | Subhi Bay Barakat al-Khalidi started his term as President (Head of State) of the Syrian Federation under the French Mandate on **June 28, 1922**. He served in this capacity through the transition to the State of S... |
| glm-5.1 | July 5, 1922 |

### Date Case 2: `date_20` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Ken_Watanabe
- Question: In what year did Ken Watanabe first appear in the television series Taiyō ni Hoero!?
- Gold answer: **1983**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Television`

| Year | Title | Role | Notes | Ref. |
| --- | --- | --- | --- | --- |
| Year | Title | Role | Notes | Ref. |
| 1983 | Taiyō ni Hoero! | Yūji Shimizu | Episode 574 |  |
| 1984 | Sanga Moyu | Takeshi Kusuda | Taiga drama |  |
| 1986 | Hanekonma | Genzō Onodera | Asadora |  |
| 2022–2024 | Tokyo Vice | Hiroto Katagiri | Also executive producer |  |
| 2024 | All Lives | Sho Naruse | Television film |  |
| 2025 | Unbound | Tanuma Okitsugu | Taiga drama |  |
| 2019 | An Artist of the Floating World | Masuji Ono | Television film |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Ken Watanabe first appeared in *Taiyō ni Hoero!* in **1984**, playing the character nicknamed "Lager" (ラガー刑事), a detective whose nickname referenced his rugby background. |
| deepseek-v4-pro | Ken Watanabe made his television debut in the long-running Japanese police drama *Taiyō ni Hoero!* (太陽にほえろ!) in **1982**. |
| gemini-3.1-pro-preview | There is no established record or credit of Ken Watanabe ever appearing in the classic Japanese detective series ***Taiyō ni Hoero!*** (Roar at the Sun!). It is highly likely that this question is based on a mix-up... |
| minimax-m2.7 | Ken Watanabe’s first appearance on **“Taiyō ni Hoero!”** was in **1975**. |
| kimi-k2.6 | Ken Watanabe first appeared in *Taiyō ni Hoero!* in **1979**. This marked his television acting debut. |
| gpt-5.5 | Ken Watanabe first appeared in **Taiyō ni Hoero!** in **1982**. |
| qwen3.5-397b-a17b | Ken Watanabe first appeared in the television series *Taiyō ni Hoero!* in **1981**. This appearance, specifically in Episode 505 titled "Detective's Reward" (Keiji no Shōkin), which aired on August 21, 1981, is wid... |
| mimo-v2.5-pro | Ken Watanabe first appeared in the Japanese television series **Taiyō ni Hoero! (太陽にほえろ!)** in **1982**. He played a supporting role in this long-running police drama. |
| glm-5.1 | Ken Watanabe first appeared in the television series *Taiyō ni Hoero!* in **1982**. This appearance marked his television debut, where he played a guest role as a delinquent youth before eventually landing his brea... |

### Date Case 3: `date_23` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/I_Know_What_You_Did_Last_Summer
- Question: In what year did John Debney win the ASCAP Award for Top Box Office Films for I Know What You Did Last Summer?
- Gold answer: **1997**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=4; section=Accolades`

| Year | Ceremony | Category | Nominee | Result |
| --- | --- | --- | --- | --- |
| Year | Ceremony | Category | Nominee | Result |
| 1997 | ASCAP Award | Top Box Office Films | John Debney | Won |
| 1998 | Saturn Award | Best Horror Film | I Know What You Did Last Summer | Nominated |
| 1998 | Blockbuster Entertainment Award | Favorite Female Newcomer | Jennifer Love Hewitt | Won |
| 1998 | Blockbuster Entertainment Award | Favorite Supporting Actor | Ryan Phillippe | Nominated |
| 1998 | International Horror Guild Award | Best Movie | I Know What You Did Last Summer | Nominated |
| 1998 | MTV Movie Awards | Best Breakthrough Performance | Sarah Michelle Gellar | Nominated |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. |
| deepseek-v4-pro | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998** (honoring the film's performance from the 1997 release year). |
| gemini-3.1-pro-preview | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998** (the award honored films released in 1997). |
| minimax-m2.7 | John Debney received the ASCAP Award for Top Box‑Office Films for **“I Know What You Did Last Summer”** in **1998** (the award was presented at the 1998 ASCAP Film & Television Music Awards, honoring the 1997 film). |
| kimi-k2.6 | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. The award was presented at the 13th Annual ASCAP Film and Television Music Awards ceremony, which honored... |
| gpt-5.5 | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. |
| qwen3.5-397b-a17b | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. Although the film was released in 1997, the ASCAP Film and Television Music Awards ceremony honoring the t... |
| mimo-v2.5-pro | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. The film was released in 1997, and the award recognized its box office success in the subsequent year. |
| glm-5.1 | John Debney won the ASCAP Award for Top Box Office Films for *I Know What You Did Last Summer* in **1998**. The film was released in October 1997, and the ASCAP Film and Television Music Awards honoring the top box... |

### Date Case 4: `date_39` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Dangerous_Minds
- Question: On what month, day, and year was the Dangerous Minds soundtrack released?
- Gold answer: **August 10, 1995**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Soundtrack`

| Year | Title | Chart positions / U.S. | Chart positions / U.S. R&B | Certifications ( sales thresholds ) |
| --- | --- | --- | --- | --- |
| Year | Title | Chart positions / U.S. | Chart positions / U.S. R&B | Certifications ( sales thresholds ) |
| 1995 | Dangerous Minds Released: August 10, 1995 Label: MCA | 1 | 1 | US : 3× Platinum |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The *Dangerous Minds* soundtrack was released on **August 1, 1995**. It is perhaps best known for featuring "Gangsta's Paradise" by Coolio featuring L.V., which became one of the best-selling singles of that year. |
| deepseek-v4-pro | The soundtrack for the film *Dangerous Minds* was released on **July 11, 1995**. |
| gemini-3.1-pro-preview | The *Dangerous Minds* soundtrack was released on **August 8, 1995**. |
| minimax-m2.7 | The Dangerous Minds soundtrack was released on **July 18, 1995**. |
| kimi-k2.6 | The *Dangerous Minds* soundtrack was released on **August 22, 1995**. |
| gpt-5.5 | The *Dangerous Minds* soundtrack was released on **July 11, 1995**. |
| qwen3.5-397b-a17b | The *Dangerous Minds* soundtrack was released on **August 8, 1995**. |
| mimo-v2.5-pro | The **Dangerous Minds** soundtrack was released on **August 15, 1995**. It was notably headlined by the hit single "Gangsta's Paradise" by Coolio featuring L.V. |
| glm-5.1 | The *Dangerous Minds* soundtrack was released on **August 8, 1995**. |

### Date Case 5: `date_47` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Comédie-Italienne
- Question: On what month, day, and year was the Salle Favart (1st) theatre destroyed by fire?
- Gold answer: **January 14, 1838**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=1; section=Venues of the 19th-century Théâtre-Italien`

| Theatre | Dates used | Notes |
| --- | --- | --- |
| Theatre | Dates used | Notes |
| Salle Favart (1st) | 2 October 1815 – 20 April 1818 |  |
| Salle Louvois | 20 March 1819 – 8 November 1825 |  |
| Salle Favart (1st) | 12 November 1825 – 14 January 1838 | Destroyed by fire 14 January 1838. |
| Salle Ventadour | 30 January 1838 – 31 March 1838 |  |
| Salle de l'Odéon (3rd) | October 1838 – 31 March 1841 |  |
| Salle de l'Odéon (2nd) | 16 June 1808 – 30 September 1815 |  |
| Salle Olympique | 31 May 1801 – 13 January 1802 | Located on the rue de la Victoire. |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The first Salle Favart (home of the Opéra-Comique in Paris) was destroyed by fire on **January 15, 1838**. A second theater was subsequently built on the same site, which also later burned (in 1887), before the cur... |
| deepseek-v4-pro | The first Salle Favart, home to the Opéra-Comique in Paris, was destroyed by fire on the night of **January 14–15, 1838** (officially recorded as **January 15, 1838**). The fire completely gutted the theater, tragi... |
| gemini-3.1-pro-preview | The first Salle Favart theatre was destroyed by fire on **January 15, 1838** (the fire broke out during the night of January 14–15 following a performance of Mozart's *Don Giovanni*). |
| minimax-m2.7 | The first **Salle Favart** (home of the Opéra-Comique in Paris) was destroyed by fire on **January 25, 1887**. |
| kimi-k2.6 | The first **Salle Favart** (the original Paris home of the Opéra-Comique) was destroyed by fire on **January 15, 1838**. |
| gpt-5.5 | The first Salle Favart theatre was destroyed by fire on **January 15, 1838**. |
| qwen3.5-397b-a17b | The Salle Favart (1st) theatre was destroyed by fire on **September 25, 1783**. |
| mimo-v2.5-pro | The first Salle Favart, which was the theatre of the Opéra-Comique in Paris, was destroyed by fire on **June 13, 1838**. It had originally opened in 1783 and was later replaced by a second Salle Favart, which itsel... |
| glm-5.1 | The first Salle Favart (the original home of the Opéra-Comique in Paris) was destroyed by fire on **January 15, 1838**. The fire broke out late in the evening during a rehearsal, burning through the night of Januar... |

### Date Case 6: `date_53` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Venezuelan_Football_Federation
- Question: In what year did the Venezuelan Football Federation become affiliated with FIFA?
- Gold answer: **1937**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=1; caption=Venezuelan Football Federation`

| Column 1 | Column 2 |
| --- | --- |
| Column 1 | Column 2 |
| Founded | 1925 ; 101 years ago ( 1925 ) |
| Headquarters | Caracas |
| FIFA affiliation | 1937 |
| CONMEBOL affiliation | 1953 |
| President | Jorge Giménez |
|  |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The Venezuelan Football Federation (Federación Venezolana de Fútbol) became affiliated with FIFA in **1952**. |
| deepseek-v4-pro | The Venezuelan Football Federation (Federación Venezolana de Fútbol or FVF) became affiliated with FIFA in **1952**. (For context, the federation was founded in 1925, and it also joined the South American confedera... |
| gemini-3.1-pro-preview | The Venezuelan Football Federation (Federación Venezolana de Fútbol) became affiliated with FIFA in **1952**. |
| minimax-m2.7 | The Venezuelan Football Federation (FVF) became affiliated with FIFA in **1936**. |
| kimi-k2.6 | The Venezuelan Football Federation (Federación Venezolana de Fútbol, FVF) became affiliated with **FIFA in 1952**. It was founded in 1926 but did not join the South American confederation (CONMEBOL) or FIFA until 1... |
| gpt-5.5 | The Venezuelan Football Federation became affiliated with FIFA in **1952**. |
| qwen3.5-397b-a17b | The Venezuelan Football Federation (FVF) became affiliated with FIFA in **1952**. |
| mimo-v2.5-pro | The **Federación Venezolana de Fútbol** (Venezuelan Football Federation) became affiliated with FIFA in **1952**. It was founded in 1926 and is also a member of CONMEBOL (the South American Football Confederation),... |
| glm-5.1 | The Venezuelan Football Federation (Federación Venezolana de Fútbol) became affiliated with FIFA in **1952**. They also became affiliated with CONMEBOL (the South American Football Confederation) in the same year. |

### Date Case 7: `date_87` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Joel_Santana
- Question: In what year was Joel Santana born?
- Gold answer: **1955**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=1; caption=Joel Santana`

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| Column 1 | Column 2 | Column 3 | Column 4 |
| Personal information |  |  |  |
| Full name | Joel Natalino Santana |  |  |
| Date of birth | ( 1955-12-25 ) 25 December 1955 (age 70) |  |  |
| Place of birth | Rio de Janeiro , Brazil |  |  |
| Position | Defender |  |  |
| Senior career* |  |  |  |
| Years | Team | Apps | ( Gls ) |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Joel Santana, the Brazilian football manager and former player, was born on **March 22, 1948**. |
| deepseek-v4-pro | Joel Santana, the Brazilian football manager and former player, was born in **1948** (specifically on December 25, 1948). |
| gemini-3.1-pro-preview | Joel Santana was born in **1948** (specifically on December 25, 1948). |
| minimax-m2.7 | Joel Santana, the Brazilian football manager and former player, was born in **1948** (specifically on December 20, 1948). He is best known for his coaching career in Brazilian football, having managed several clubs... |
| kimi-k2.6 | Joel Santana, the Brazilian football manager and former player, was born in **1948** (on January 25, in Rio de Janeiro). |
| gpt-5.5 | Joel Santana was born in **1948**. |
| qwen3.5-397b-a17b | Joel Santana was born in **1948**. |
| mimo-v2.5-pro | **Joel Santana** was born in **1948** (November 25, 1948). He is a well-known Brazilian football manager who has coached numerous clubs in Brazil as well as the South African national team. |
| glm-5.1 | Joel Santana, the famous Brazilian football manager and former player, was born in **1948** (specifically on December 23, 1948). *(Note: If you are referring to the Dominican Republic cyclist named Joel Santana, he... |

### Date Case 8: `date_2` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/John_Hurt
- Question: In what year did John Hurt win the BAFTA Award for Best Actor for his role in The Elephant Man?
- Gold answer: **1980**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: gpt-5.5

Source table excerpt:

`table_index=2; section=Awards and nominations`

| Year | Award | Category | Work | Result |
| --- | --- | --- | --- | --- |
| Year | Award | Category | Work | Result |
| 1978 | BAFTA Awards | Best Supporting Actor | Midnight Express | Won |
| 1979 | BAFTA Awards | Best Supporting Actor | Alien | Nominated |
| 1980 | BAFTA Awards | Best Actor | The Elephant Man | Won |
| 1989 | BAFTA Awards | Best Supporting Actor | The Field | Nominated |
| 2009 | BAFTA Awards | Best Actor | An Englishman in New York | Nominated |
| 1978 | Golden Globe Awards | Best Supporting Actor – Motion Picture | Midnight Express | Won |
| 1980 | Golden Globe Awards | Best Actor – Motion Picture Drama | The Elephant Man | Nominated |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | John Hurt won the BAFTA Award for Best Actor for *The Elephant Man* in **1981** (at the 34th BAFTA Awards, recognizing films from 1980). |
| deepseek-v4-pro | John Hurt won the BAFTA Award for Best Actor for his role as John Merrick in *The Elephant Man* in **1981**. The award was presented at the 34th British Academy Film Awards ceremony (honoring films released in 1980... |
| gemini-3.1-pro-preview | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981** (honoring films released in 1980). |
| minimax-m2.7 | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981**, for films released in 1980. |
| kimi-k2.6 | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981** (at the 34th British Academy Film Awards, honoring films released in 1980). |
| qwen3.5-397b-a17b | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981**. He received the award at the 34th British Academy Film Awards, which were held on March 29, 1981, honoring films released... |
| mimo-v2.5-pro | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981**. |
| glm-5.1 | John Hurt won the BAFTA Award for Best Actor for his role in *The Elephant Man* in **1981**. (The film was released in 1980, and the 34th BAFTA ceremony honoring those films took place on March 22, 1981.) |

### Date Case 9: `date_7` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Agatha_Christie's_Poirot
- Question: In what year did Agatha Christie's Poirot win the Edgar Award for Best Episode in a TV Series?
- Gold answer: **1992**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=5; section=Accolades; caption=List of awards and nominations for Agatha Christie's Poirot`

| Award | Date of ceremony | Category | Nominee(s) | Result |
| --- | --- | --- | --- | --- |
| Award | Date of ceremony | Category | Nominee(s) | Result |
| British Academy Television Craft Awards (1992) | 1992 | Best Costume Design | Elizabeth Waller (series 3, episodes 2–3, 6–8) | Nominated |
| British Academy Television Craft Awards (1992) | 1992 | Best Make-up | Janis Gould (series 3, episodes 2–3, 6–8) | Nominated |
| Edgar Awards (1992) | 1992 | Best Episode in a TV Series | " The Lost Mine " | Won |
| Satellite Award (2010) | 2010 | Best Actor – Miniseries or Television Film | David Suchet | Nominated |
| PGA Awards (2010) | 2011 | Outstanding Producer of Long-Form Television | " Murder on the Orient Express " | Nominated |
| British Academy Television Craft Awards (1992) | 1992 | Best Costume Design | Robin Fraser-Paye (series 3, episodes 1, 4–5, 9–10) | Nominated |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | Agatha Christie's Poirot actually did not win the Edgar Award in the category of **Best Episode in a TV Series**. However, it did win an Edgar Award in a very similar category. The episode **"Murder on the Orient E... |
| gemini-3.1-pro-preview | Actually, **Agatha Christie's Poirot** (starring David Suchet) **never won** an Edgar Award for Best Television Episode. While the show is widely considered one of the greatest mystery adaptations in television his... |
| minimax-m2.7 | Agatha Christie's Poirot won the Edgar Award for Best Episode in a TV Series in **1991** for the episode titled **"The Lost World"** (based on the novel *The Lost World*). |
| kimi-k2.6 | **Agatha Christie’s Poirot** won the Edgar Award for Best Episode in a TV Series in **1994** — typically cited for the episode **“The Lost Mine”** (which became eligible for the U.S.-based Mystery Writers of Americ... |
| gpt-5.5 | Agatha Christie's Poirot won the Edgar Award for Best Episode in a TV Series in **1990**. |
| qwen3.5-397b-a17b | Agatha Christie's *Poirot* won the Edgar Award for **Best Episode in a TV Series** in **2001**. The award was given for the episode **"The Murder of Roger Ackroyd"** (adapted by Anthony Horowitz), which aired in 20... |
| mimo-v2.5-pro | **Agatha Christie's Poirot** (the long-running ITV series starring David Suchet) won the **Edgar Allan Poe Award for Best Episode in a TV Series** in **2011**. If you're looking for a specific episode or additional... |
| glm-5.1 | Agatha Christie's Poirot won the Edgar Award for Best Episode in a TV Series in **1990**. The award was specifically given to screenwriter Clive Exton for his adaptation of the episode **"The Disappearance of Mr. D... |

### Date Case 10: `date_14` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Tórshavn
- Question: In what year did Lisbeth L. Petersen begin her term as mayor of Tórshavn?
- Gold answer: **1991**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=5; section=Mayors of Tórshavn`

| Nº | Column 2 | Mayor (Party) | Term |
| --- | --- | --- | --- |
| Nº |  | Mayor (Party) | Term |
|  | 1. | Poul Michelsen ( A ) | 1980-1991 |
|  | 2. | Lisbeth L. Petersen ( B ) | 1991-1997 |
|  | 3. | Leivur Hansen ( E ) | 1997-2001 |
|  | 4. | Jan Christiansen ( A ) | 2001-2005 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | Lisbeth L. Petersen began her term as mayor of Tórshavn in **1993**, making her the first woman to hold the position. She served until 1996. |
| gemini-3.1-pro-preview | Lisbeth L. Petersen began her term as mayor of Tórshavn in **1993**. She served in this position until 1996, notably making history as the city's first female mayor. |
| minimax-m2.7 | Lisbeth L. Petersen began her term as mayor of Tórshavn in **2012**, after the local elections held that year. She served until 2016. |
| kimi-k2.6 | Lisbeth L. Petersen began her term as mayor of Tórshavn in **2004**. She served until 2012 and was the first woman to hold the position. |
| gpt-5.5 | Lisbeth L. Petersen began her term as mayor of Tórshavn in **1993**. |
| qwen3.5-397b-a17b | Lisbeth L. Petersen began her term as mayor of Tórshavn in **2005**. She served in the position until 2009. |
| mimo-v2.5-pro | Lisbeth L. Petersen began her term as mayor of Tórshavn in **2001**. She served in that role until 2008. |
| glm-5.1 | Lisbeth L. Petersen began her term as mayor of Tórshavn in **2001**. She served in that office until 2004 and was the first woman to hold the position. |

## Number

| Selected case | Incorrect models | Correct models | Not attempted |
| --- | ---: | ---: | ---: |
| `number_7` | 9/9 | 0 | 0 |
| `number_37` | 9/9 | 0 | 0 |
| `number_43` | 9/9 | 0 | 0 |
| `number_45` | 9/9 | 0 | 0 |
| `number_1` | 8/9 | 0 | 1 |
| `number_3` | 8/9 | 0 | 1 |
| `number_15` | 8/9 | 1 | 0 |
| `number_16` | 8/9 | 0 | 1 |
| `number_27` | 8/9 | 1 | 0 |
| `number_46` | 8/9 | 0 | 1 |

### Number Case 1: `number_7` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/James_IV
- Question: How many legitimate children of James IV died before reaching one year of age?
- Gold answer: **4**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=2; section=Legitimate issue`

| Name | Birth | Death | Notes |
| --- | --- | --- | --- |
| Name | Birth | Death | Notes |
| King James V | 10 April 1512 | 14 December 1542 | Married: Madeleine of Valois , 1537; no issue; Mary of Guise , 1538; had issue, including... |
| Unnamed son | November 1512 |  | died shortly after birth at Palace of Holyroodhouse |
| Alexander, Duke of Ross | 30 April 1514 | 18 December 1515 | posthumous son of James IV, died aged nineteen months at Stirling Castle |
| Unnamed daughter | 15 July 1508 |  | died shortly after birth at Palace of Holyroodhouse |
| Arthur, Duke of Rothesay | 20/21 October 1509 | 14/15 July 1510 | died aged almost nine months at Edinburgh Castle |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | ## Legitimate Children of James IV Who Died Before Age One James IV of Scotland and his wife **Margaret Tudor** had several children who died in infancy. The clearly documented cases of legitimate children who died... |
| deepseek-v4-pro | James IV of Scotland had **three** legitimate children who died before reaching their first birthday. He and his wife, Margaret Tudor, had six children in total. Here is the fate of their children, with the three w... |
| gemini-3.1-pro-preview | James IV of Scotland had six legitimate children with his wife, Margaret Tudor, but only **three** of them died before reaching one year of age. This specific number can be a bit of a historical trick question, as... |
| minimax-m2.7 | James IV of Scotland (1488–1513) had several legitimate children with his wife, Margaret Tudor, but only a small number survived to adulthood. According to historical records, the only legitimate child of James IV... |
| kimi-k2.6 | James IV of Scotland and Margaret Tudor had four generally recognized live-born legitimate children, of whom **two died before reaching one year of age**: 1. **An unnamed daughter** (born 15 July 1508) – either sti... |
| gpt-5.5 | Three legitimate children of James IV died before reaching one year of age: 1. An unnamed daughter, born and died in 1508 2. Arthur, Duke of Rothesay, who died at about 8 months old 3. An unnamed daughter, born pre... |
| qwen3.5-397b-a17b | Based on historical records, James IV of Scotland and his wife, Margaret Tudor, had **three** legitimate children who died before reaching one year of age. James IV and Margaret Tudor had a total of six recorded le... |
| mimo-v2.5-pro | ## James IV's Children Who Died in Infancy James IV of Scotland and his queen, **Margaret Tudor**, had several children, and infant mortality was tragically common in their family. At least **three** of their legit... |
| glm-5.1 | Strictly speaking, **three** of James IV's legitimate children died before reaching one year of age, though a fourth died just six days after his first birthday and is often grouped together with them as dying in i... |

### Number Case 2: `number_37` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Illinois's_congressional_delegations
- Question: How many different Congress sessions did Stephen A. Douglas serve as a Class II senator from Illinois?
- Gold answer: **11**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=United States Senate`

| Class II senator | Column 2 | Congress | Class III senator | Column 5 |
| --- | --- | --- | --- | --- |
| Class II senator |  | Congress | Class III senator |  |
| Jesse B. Thomas (DR) |  | 15th (1817–1819) |  | Ninian Edwards (DR) |
| Jesse B. Thomas (DR) |  | 16th (1819–1821) |  | Ninian Edwards (DR) |
| Stephen A. Douglas (D) |  | 36th (1859–1861) |  | Lyman Trumbull (R) |
| Stephen A. Douglas (D) |  | 37th (1861–1863) |  | Lyman Trumbull (R) |
| Orville Browning (R) |  | 37th (1861–1863) |  | Lyman Trumbull (R) |
| Stephen A. Douglas (D) |  | 35th (1857–1859) |  | Lyman Trumbull (R) |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | ## Stephen A. Douglas's Senate Service Stephen A. Douglas served as a Class II senator from Illinois from **April 7, 1847 until his death on June 3, 1861**. His Class II status is confirmed by his election years (1... |
| deepseek-v4-pro | Stephen A. Douglas served as a Class II senator from Illinois for parts of **eight** different Congress sessions. He took office on March 4, 1847, and served until his death on June 3, 1861. During that time, his t... |
| gemini-3.1-pro-preview | Stephen A. Douglas served in **8 different Congresses** as a Class II Senator from Illinois. He was elected to the Senate three times (in 1846, 1852, and 1858) and served from March 4, 1847, until his death on June... |
| minimax-m2.7 | Stephen A. Douglas held the **Class II Senate seat from Illinois** from March 4 1847 until his death on August 4 1861. During that time he sat in **eight separate Congresses**: \| Congress (years) \| Session(s) in wh... |
| kimi-k2.6 | Stephen A. Douglas served in **14 different regular sessions of Congress** as a Class II senator from Illinois. He held the seat from March 4, 1847, until his death on June 3, 1861. During that time he was in offic... |
| gpt-5.5 | Stephen A. Douglas served as a Class II senator from Illinois in **8 different Congresses** — the **30th through 37th U.S. Congresses**. |
| qwen3.5-397b-a17b | Stephen A. Douglas served in **8 different Congresses** during his tenure as a Class II U.S. Senator from Illinois. Although the term "Congress sessions" can technically refer to the annual meetings within a Congre... |
| mimo-v2.5-pro | ## Stephen A. Douglas's Senate Service Stephen A. Douglas served as a Class II U.S. Senator from Illinois from **March 4, 1847**, until his death on **June 3, 1861**. During that time, he served in **eight** differ... |
| glm-5.1 | To answer this question accurately, it helps to clarify what is meant by "Congress sessions," as the phrase can refer to **senatorial terms**, the **number of Congresses** (two-year periods), or the **actual legisl... |

### Number Case 3: `number_43` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Paulina_Porizkova
- Question: How many films did Paulina Porizkova appear in between 1987 and 2004 inclusive according to her filmography?
- Gold answer: **11**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Filmography`

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| Column 1 | Column 2 | Column 3 | Column 4 |
| Television |  |  |  |
| Year | Title | Role | Notes |
| 1987 | Saturday Night Live | Herself | "Bronson Pinchot" (season 12: episode 11) |
| 2008–2010 | America's Next Top Model | Judge | Judge for cycles 10–12 |
| 2009–2010 | As the World Turns | Clarissa |  |
| 2001 | Dark Asylum | Dr. Maggie Bellum |  |
| 2004 | Knots | Lily Kildear |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Based on Paulina Porizkova's filmography, she appeared in **8 films** between 1987 and 2004, including notable titles such as *Anna* (1987), *Her Alibi* (1989), *Arizona Dream* (1993), and *Thursday* (1998), among... |
| deepseek-v4-pro | Paulina Porizkova appeared in **7 films** between 1987 and 2004 inclusive. Here is the list of those films by year of release: * ***Anna*** (1987) – Her acting debut, playing the role of Krystyna. * ***Her Alibi***... |
| gemini-3.1-pro-preview | According to her standard documented acting filmography on platforms like IMDb and Wikipedia, Paulina Porizkova appeared in **14** feature films between 1987 and 2004 inclusive. Here is the exact chronological list... |
| minimax-m2.7 | According to the publicly listed filmography (e.g., IMDb and Wikipedia), Paulina Porizkova has **two** film credits between 1987 and 2004 inclusive: 1. **The Last Summer** (1994) – role Eva 2. **The Fifth Element**... |
| kimi-k2.6 | According to her feature‑film filmography, Paulina Porizkova appeared in **7** films between 1987 and 2004 (inclusive). They are: 1. *Anna* (1987) 2. *Her Alibi* (1989) 3. *Arizona Dream* (1993) 4. *Thursday* (1998... |
| gpt-5.5 | Paulina Porizkova appeared in **13 films** between **1987 and 2004 inclusive** according to her filmography. |
| qwen3.5-397b-a17b | According to Paulina Porizkova's standard filmography (such as those listed on IMDb or Wikipedia), she appeared in **12** films between 1987 and 2004 inclusive. Her first film credit, *Made in Paris*, was released... |
| mimo-v2.5-pro | According to Paulina Porizkova's filmography, she appeared in **5 films** between 1987 and 2004 inclusive: 1. **Anna** (1987) 2. **Her Alibi** (1989) 3. **The Unbelievable Truth** (1989) 4. **Thursday** (1998) 5. *... |
| glm-5.1 | According to Paulina Porizkova's filmography, she appeared in **8** films between 1987 and 2004 inclusive. Here is the list of those films: 1. **Her Alibi** (1989) 2. **Night and the City** (1992) 3. **Arizona Drea... |

### Number Case 4: `number_45` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Canada_Post
- Question: For how many years did Moya Greene serve as President and CEO of Canada Post?
- Gold answer: **6**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Presidents and CEOs; caption=President and CEOs of Canada Post`

| Years | Name | Remarks |
| --- | --- | --- |
| Years | Name | Remarks |
| 1981–1985 | Michael Warren | Appointed on the advice of Pierre Trudeau . |
| 1986–1992 | Donald Harley Lander | Appointed on the advice of Brian Mulroney . |
| 1993–1998 | Georges Clermont | Appointed on the advice of Kim Campbell . |
| 1999–2004 | André Ouellet | Appointed on the advice of Jean Chretien . Former Postmaster General . |
| 2004–2010 | Moya Greene | Appointed on the advice of Paul Martin . |
| 2010–2011 | Stewart Bacon | Appointed interim CEO on the advice of Stephen Harper following Greene's departure. |
| 2011–2018 | Deepak Chopra | Appointed on the advice of Stephen Harper . |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Moya Greene served as President and CEO of Canada Post from 2005 to 2010, a period of approximately **5 years**, before leaving to become CEO of Royal Mail in the United Kingdom. |
| deepseek-v4-pro | Moya Greene served as the President and CEO of Canada Post for about **5 years**, from 2005 until 2010, when she left to become the CEO of the Royal Mail in the United Kingdom. |
| gemini-3.1-pro-preview | Moya Greene served as President and CEO of Canada Post for **5 years**, from May 2005 to July 2010. She left the position to become the CEO of Britain's Royal Mail. |
| minimax-m2.7 | Moya Greene served as President and CEO of Canada Post from 2009 until 2016, for a total of 7 years. |
| kimi-k2.6 | Moya Greene served as President and CEO of Canada Post for **5 years**, from 2005 until 2010. She left the position in July 2010 to become the Chief Executive of Royal Mail in the United Kingdom. |
| gpt-5.5 | Moya Greene served as President and CEO of Canada Post for about **5 years** — from **2005 to 2010**. |
| qwen3.5-397b-a17b | Moya Greene served as President and CEO of Canada Post for **seven years**. She was appointed to the role in **October 2010** and stepped down in **May 2018**. |
| mimo-v2.5-pro | Moya Greene served as President and CEO of Canada Post from 2005 to 2010, for approximately **5 years**. After her tenure at Canada Post, she went on to become the Chief Executive of Royal Mail in the United Kingdo... |
| glm-5.1 | Moya Greene served as President and CEO of Canada Post for **5 years**, from 2005 to 2010. She left the position in mid-2010 to become the Chief Executive of the Royal Mail in the United Kingdom. |

### Number Case 5: `number_1` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/West_Virginia
- Question: What is the rank number of Kroger among the largest private employers in West Virginia as of March 2019?
- Gold answer: **5**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: mimo-v2.5-pro

Source table excerpt:

`table_index=9; section=Largest private employers; caption=The largest private employers in West Virginia, as of March 2019, were: [ 144 ]`

| Rank | Company |
| --- | --- |
| Rank | Company |
| 3 | CAMC Health System |
| 4 | Mountain Health Network |
| 5 | Kroger |
| 6 | Lowe's Home Centers |
| 7 | Contura Energy |
| 14 | American Electric Power |
| 15 | West Virginia's Choice, Inc. |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Based on available data about West Virginia's largest private employers as of March 2019, **Kroger ranked 2nd** among the largest private employers in West Virginia. If you need more precise details or the specific... |
| deepseek-v4-pro | The Kroger Co. (often misspelled as Kroger) was the **4th** largest private employer in West Virginia as of March 2019. According to the annual report released by WorkForce West Virginia at that time, Kroger direct... |
| gemini-3.1-pro-preview | Based on data from WorkForce West Virginia from March 2019, Kroger was ranked as the **4th** largest private employer in West Virginia. For context, the top five at that specific time were: 1. West Virginia Univers... |
| minimax-m2.7 | Kroger was the **second‑largest** private employer in West Virginia at that time. (It ranked #2 among the largest private employers in the state as of March 2019.) |
| kimi-k2.6 | As of March 2019, Kroger was generally ranked as the **2nd largest private employer** in West Virginia (behind Walmart). *Note: Rankings can vary slightly depending on whether nonprofit health systems (such as CAMC... |
| gpt-5.5 | Kroger was ranked **No. 4** among the largest private employers in West Virginia as of March 2019. |
| qwen3.5-397b-a17b | Based on available business data and employment reports for West Virginia, **Kroger does not have a rank** among the largest private employers in the state as of March 2019. This is because **Kroger does not operat... |
| glm-5.1 | 2 |

### Number Case 6: `number_3` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Danny_Elfman
- Question: How many Emmy Awards has Danny Elfman won?
- Gold answer: **3**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=2; section=Awards and nominations; caption=Danny Elfman awards and nominations`

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Column 1 | Column 2 | Column 3 |
| Broadcast Film Critics Association Awards | 0 | 2 |
| Chicago Film Critics Association Awards | 0 | 4 |
| Emmy Awards | 3 | 5 |
| Golden Globe Awards | 0 | 2 |
| Grammy Awards | 1 | 11 |
| Award | Wins | Nominations |
| Totals |  |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | Danny Elfman has won two Primetime Emmy Awards: - **Outstanding Main Title Theme Music** for *The Simpsons* (1990) - **Outstanding Main Title Theme Music** for *Desperate Housewives* (2005) |
| gemini-3.1-pro-preview | Danny Elfman has won **two** Emmy Awards. Here are the details of his wins: * **2005:** Outstanding Main Title Theme Music for ***Desperate Housewives***. * **2016:** Outstanding Music Direction for ***Danny Elfman... |
| minimax-m2.7 | Danny Elfman has won **one** Emmy Award. He received the Primetime Emmy Award for Outstanding Original Music and Lyrics in 1990 for his work on *The Simpsons*. |
| kimi-k2.6 | Danny Elfman has won **one** Emmy Award. He won the **Primetime Emmy for Outstanding Main Title Theme Music** in 2005 for his theme to ***Desperate Housewives***. He has been nominated for several other Emmys over... |
| gpt-5.5 | Danny Elfman has won **two Emmy Awards**. |
| qwen3.5-397b-a17b | Danny Elfman has won **one** Primetime Emmy Award. He received the award in **1990** for **Outstanding Achievement in Main Title Theme Music** for the television series ***The Simpsons***. While he has only won onc... |
| mimo-v2.5-pro | Danny Elfman has won **one Emmy Award**. He won in 2005 for Outstanding Main Title Theme Music for the television series *Desperate Housewives*. He has received several other Emmy nominations throughout his career,... |
| glm-5.1 | Danny Elfman has won **0** Emmy Awards. Despite being one of the most iconic composers in film and television, he has never won a competitive Emmy. He has, however, been nominated a few times for Outstanding Main T... |

### Number Case 7: `number_15` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Cilicia
- Question: In which year was the Kingdom of Cilicia annexed by the Achaemenid Empire?
- Gold answer: **401**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: claude-sonnet-4.6

Source table excerpt:

`table_index=2; section=Kingdom of Cilicia`

| Column 1 | Column 2 |
| --- | --- |
| Column 1 | Column 2 |
| • Established | c. 6th century BC |
| • Submission to the Achaemenid Empire | c. 542 BC |
| • Annexation by the Achaemenid Empire | 401 BC |
|  |  |
|  |  |
| Cilicia Κιλικία ( Kilikía ) |  |
| Kingdom of Cilicia in 6th century BC |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The Kingdom of Cilicia was brought into the Achaemenid Empire during the reign of **Cyrus the Great** in the **540s BCE**. While Cilicia initially submitted willingly and was allowed to keep its native kings (the S... |
| gemini-3.1-pro-preview | The Kingdom of Cilicia was formally annexed and its underlying monarchy abolished by the Achaemenid Empire in **400 BC** (following the events of **401 BC**), though it had been a subjugated vassal states for over... |
| minimax-m2.7 | The Kingdom of Cilicia was annexed by the Achaemenid Empire in **547 BCE** (or possibly 546 BCE). This occurred during the reign of Cyrus the Great, as the Achaemenid forces expanded into Anatolia and incorporated... |
| kimi-k2.6 | The Kingdom of Cilicia was annexed by the Achaemenid Empire under **Cyrus the Great** around **546 BCE** (following his conquest of Lydia). After toppling Lydia in 547/546 BCE, Cyrus extended Persian control over t... |
| gpt-5.5 | The Kingdom of Cilicia was annexed by the Achaemenid Empire in **549 BC**. |
| qwen3.5-397b-a17b | The Kingdom of Cilicia was annexed by the Achaemenid Empire in **547 BC**. This conquest was carried out by **Cyrus the Great** during his campaign in Anatolia, shortly following the defeat of the Lydian King Croes... |
| mimo-v2.5-pro | ## The Annexation of Cilicia by the Achaemenid Empire The Kingdom of Cilicia was incorporated into the Achaemenid Empire around **547–546 BCE**, during the reign of **Cyrus the Great**. This occurred in the context... |
| glm-5.1 | The Kingdom of Cilicia was incorporated into the Achaemenid Empire in **546 BC** under the reign of **Cyrus the Great**. This happened shortly after the Persian conquest of the Lydian Empire. Following the defeat o... |

### Number Case 8: `number_16` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Elisha_Cuthbert
- Question: How many films did Elisha Cuthbert appear in during the year 2022?
- Gold answer: **3**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=2; section=Film`

| Year | Title | Role |
| --- | --- | --- |
| Year | Title | Role |
| 2000 | Who Gets the House? | Emily Reece |
| 2003 | Love Actually | American Goddess Carol |
| 2003 | Old School | Darcie Goldberg |
| 2004 | The Girl Next Door | Danielle |
| 2005 | House of Wax | Carly Jones |
| 2022 | Bandit | Andrea |
| 2022 | Friday Afternoon in the Universe | Eleanor |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | In 2022, Elisha Cuthbert appeared in **two** films: 1. **The Cellar** – A horror film directed by Brendan Muldowney, in which she plays Keira Woods, a mother searching for her daughter who has mysteriously vanished... |
| gemini-3.1-pro-preview | Elisha Cuthbert appeared in **2** films during the year 2022. They are: 1. **The Cellar** - A horror film where she played the lead role of Keira Woods. 2. **Bandit** - A biographical crime thriller where she playe... |
| minimax-m2.7 | Elisha Cuthbert had **one film credit** in 2022. The film was **“The Estate.”** (All other appearances that year were on television or other media.) |
| kimi-k2.6 | Elisha Cuthbert appeared in **one** feature film released in 2022: the horror movie **"The Cellar"** (also known by its Irish title "An Cella"), where she played the lead role of Keira Woods. |
| gpt-5.5 | Elisha Cuthbert appeared in **2 films** in 2022: **The Cellar** and **Bandit**. |
| qwen3.5-397b-a17b | Elisha Cuthbert appeared in **one** feature film during the year 2022. The film was: * ***Firestarter*** (released May 13, 2022), in which she played the role of Victoria McGee. While she also appeared in the telev... |
| mimo-v2.5-pro | Based on my knowledge, Elisha Cuthbert appeared in at least **1** film in 2022 — **"The Cellar"** (an Irish horror film directed by Brendan Muldowney). However, I'd recommend double-checking with a source like IMDb... |
| glm-5.1 | Elisha Cuthbert appeared in **2** films during the year 2022: 1. **The Cellar** - A horror film released on Shudder in March 2022, where she played the lead role of Keira Woods. 2. **Bandit** - A Canadian crime fil... |

### Number Case 9: `number_27` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/History_of_Cyprus
- Question: For how many years was Cyprus administered as a fief of the Grand Vizier during the period from 1703 to 1784?
- Gold answer: **78**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: gemini-3.1-pro-preview

Source table excerpt:

`table_index=1; section=Change of Administration of Cyprus`

| From | To | Type of Administration |
| --- | --- | --- |
| From | To | Type of Administration |
| 1703 | 1745 | a fief of the Grand Vizier |
| 1745 | 1748 | an eyalet (province) |
| 1748 | 1784 | a fief of the Grand Vizier |
| 1784 | ... | a sanjak of the Eyalet of the Archipelago |
| 1670 | 1703 | a sanjak of the Eyalet of the Archipelago |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | During the period from 1703 to 1784, Cyprus was administered as a fief (*has*) of the Grand Vizier for **81 years** — essentially the entire span of that period. In 1703, the island was assigned as a Grand Vizier's... |
| deepseek-v4-pro | Cyprus was administered as a fief (hass) of the Ottoman Grand Vizier continuously from 1703 to 1784. The duration of this period is **81 years** (1784 – 1703 = 81). |
| minimax-m2.7 | Cyprus was administered as a fief of the Grand Vizier from 1745 to 1765, a period of **20 years**, within the range from 1703 to 1784. |
| kimi-k2.6 | Based on standard historical calculations, Cyprus was administered as a fief of the Grand Vizier for **81 years** during that period (1784 − 1703 = 81). |
| gpt-5.5 | 81 years. |
| qwen3.5-397b-a17b | Based on historical records regarding the Ottoman administration of Cyprus, the island was administered as a personal fief (*has*) of the Grand Vizier from **1703 to 1784**. To calculate the number of years: $$1784... |
| mimo-v2.5-pro | ## Cyprus as a Grand Vizier's Fief During the period from **1703 to 1784**, Cyprus was administered as a fief of the Grand Vizier for **81 years**. During this time, rather than being governed as a regular Ottoman... |
| glm-5.1 | 81 |

### Number Case 10: `number_46` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/1952_United_States_Senate_elections
- Question: How many Democratic senators were running for re-election before the 1952 United States Senate elections?
- Gold answer: **26**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=6; section=Before the elections`

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 |
| --- | --- | --- | --- | --- | --- |
| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 |
| R 39 N.J. Ran | R 40 N.Y. Ran | R 41 N.D. Ran | R 42 Ohio Ran | R 43 Pa. Ran | R 44 Utah Ran |
| R 38 Nev. Ran | R 37 Neb. (sp) Retired | R 36 Neb. (reg) Ran | R 35 Mont. Ran | R 34 Mo. Ran | R 33 Minn. Ran |
| R 19 | R 20 | R 21 | R 22 | R 23 | R 24 |
| R 18 | R 17 | R 16 | R 15 | R 14 | R 13 |
|  |  | R 1 | R 2 | R 3 | R 4 |
| D 18 | D 17 | D 16 | D 15 | D 14 | D 13 |
| D 19 | D 20 | D 21 | D 22 | D 23 | D 24 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | Before the 1952 United States Senate elections, **12** Democratic senators were running for re-election. The 1952 elections were held for the Senate Class 1 seats (32 regular elections) and several special election... |
| gemini-3.1-pro-preview | Before the 1952 United States Senate elections, there were **14 seats** held by Democrats up for election. Depending on how strictly you define "running for re-election" before the November general election, the an... |
| minimax-m2.7 | Before the 1952 United States Senate elections, five Democratic incumbent senators were running for re-election: 1. **John L. McClellan** (Arkansas) 2. **James O. Eastland** (Mississippi) 3. **J. William Fulbright*... |
| kimi-k2.6 | **11 Democratic senators** were running for re-election in the 1952 United States Senate elections. |
| gpt-5.5 | Eleven Democratic incumbents were running, counting the Kentucky special election. If you mean only the regular Class 1 re-election races, the number was ten. |
| qwen3.5-397b-a17b | In the 1952 United States Senate elections, there were **19** Democratic senators running for re-election. Here is the breakdown of the situation leading into the election: * **Total Seats Up:** There were 36 seats... |
| mimo-v2.5-pro | ## 1952 U.S. Senate Elections — Democratic Incumbents In the **1952 United States Senate elections**, **15 Democratic senators** were running for re-election. These were the **Class II** Senate seats, and approxima... |
| glm-5.1 | Before the 1952 United States Senate elections, there were **12** Democratic incumbents seeking to continue their terms. However, strictly speaking, only **10** of them were elected senators "running for re-electio... |

## Other

| Selected case | Incorrect models | Correct models | Not attempted |
| --- | ---: | ---: | ---: |
| `other_10` | 9/9 | 0 | 0 |
| `other_35` | 9/9 | 0 | 0 |
| `other_90` | 9/9 | 0 | 0 |
| `other_103` | 9/9 | 0 | 0 |
| `other_5` | 8/9 | 1 | 0 |
| `other_6` | 8/9 | 1 | 0 |
| `other_13` | 8/9 | 0 | 1 |
| `other_26` | 8/9 | 0 | 1 |
| `other_27` | 8/9 | 0 | 1 |
| `other_32` | 8/9 | 1 | 0 |

### Other Case 1: `other_10` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Glycerol-3-phosphate_dehydrogenase
- Question: What is the PROSITE identifier for the NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus?
- Gold answer: **PDOC00740**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=4`

| Column 1 | Column 2 |
| --- | --- |
| Column 1 | Column 2 |
| Pfam clan | CL0106 |
| InterPro | IPR006109 |
| PROSITE | PDOC00740 |
| SCOP2 | 1m66 / SCOPe / SUPFAM |
|  |  |
| NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus |  |
| structure of glycerol-3-phosphate dehydrogenase from archaeoglobus fulgidus |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | ## PROSITE Identifier for NAD-Dependent Glycerol-3-Phosphate Dehydrogenase C-Terminus The PROSITE identifier for the NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus signature is **PS00957**. This entry... |
| deepseek-v4-pro | The PROSITE identifier for the NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus is **PS00958**. This pattern belongs to a family of two signatures for this enzyme, which are documented under the PROSITE... |
| gemini-3.1-pro-preview | Based on your query, it appears there might be a slight confusion between protein databases. The exact description **"NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus"** actually corresponds to an identi... |
| minimax-m2.7 | The NAD‑dependent glycerol‑3‑phosphate dehydrogenase C‑terminal domain is documented in the PROSITE database under the accession number **PS01044**. This entry provides the signature pattern and functional annotati... |
| kimi-k2.6 | The PROSITE entry for the **NAD-dependent glycerol-3-phosphate dehydrogenase C-terminal domain** is: **PS51397** (also known by the entry name **GPD_C**) It is a PROSITE profile that specifically recognizes the C-t... |
| gpt-5.5 | The PROSITE identifier is **PS00957** — the NAD-dependent glycerol-3-phosphate dehydrogenase signature. |
| qwen3.5-397b-a17b | The PROSITE identifier for the NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus is **PS00617**. Here are the details for this entry: * **Accession Number:** PS00617 * **Entry Name:** NAD_G3PDH_C * **Desc... |
| mimo-v2.5-pro | ## PROSITE Identifier The PROSITE identifier for the **NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus** is: **PS00967** This entry represents the conserved C-terminal domain found in NAD-dependent glyc... |
| glm-5.1 | The PROSITE identifier for the NAD-dependent glycerol-3-phosphate dehydrogenase C-terminus signature is **PS00586**. In the PROSITE database, the documentation entry for this domain is **PDOC00586**, and the specif... |

### Other Case 2: `other_35` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Deep_brain_stimulation
- Question: Which specific deep brain stimulation target was approved by the FDA for the treatment of severe, treatment-resistant obsessive–compulsive disorder?
- Gold answer: **Nucleus Accumbens**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Specific DBS targets`

| Indication | Approval Date | Details | DBS Target | Evidence | Source |
| --- | --- | --- | --- | --- | --- |
| Indication | Approval Date | Details | DBS Target | Evidence | Source |
| Parkinson's Disease | January 14, 2002 | Approved for advanced Parkinson's disease symptoms not adequately controlled by medicatio... | Subthalamic nucleus (STN) or internal globus pallidus (GPi) | DBS in the subthalamic nucleus with better motor function and quality of life compared to... | FDA |
| Dystonia | April 15, 2003 | Humanitarian Device Exemption for the treatment of chronic, intractable primary dystonia,... | Internal globus pallidus (GPi) | Improved motor function in individuals with primary dystonia. | FDA |
| Obsessive–compulsive disorder | February 19, 2009 | Humanitarian Device Exemption for adjunctive treatment of severe, treatment-resistant OCD. | Nucleus Accumbens (NAc) | Reductions in OCD symptoms in severe cases. | FDA |
| Epilepsy | April 27, 2018 | Approved for bilateral stimulation of the anterior nucleus of the thalamus (ANT) as an ad... | Anterior nucleus of the thalamus (ANT) | Significant reduction in seizure frequency in patients receiving DBS. | FDA |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | ## FDA-Approved DBS Target for Treatment-Resistant OCD The FDA approved deep brain stimulation targeting the **ventral capsule/ventral striatum (VC/VS)** for severe, treatment-resistant OCD. ### Key Details: - **Ap... |
| deepseek-v4-pro | The specific deep brain stimulation (DBS) target approved by the FDA for the treatment of severe, treatment-resistant obsessive–compulsive disorder (OCD) is the **ventral capsule/ventral striatum (VC/VS)**. This ta... |
| gemini-3.1-pro-preview | The specific deep brain stimulation (DBS) target approved by the FDA for severe, treatment-resistant obsessive-compulsive disorder (OCD) is the **anterior limb of the internal capsule (ALIC)**. In clinical practice... |
| minimax-m2.7 | The FDA‐approved DBS target for severe, treatment‑resistant OCD is the **ventral capsule/ventral striatum (VC/VS)** – the region at the ventral anterior limb of the internal capsule (sometimes simply referred to as... |
| kimi-k2.6 | The FDA-approved deep brain stimulation (DBS) target for severe, treatment-resistant obsessive–compulsive disorder (OCD) is the **anterior limb of the internal capsule (ALIC)**—specifically the **ventral capsule/ve... |
| gpt-5.5 | The FDA-approved DBS target for severe, treatment-resistant obsessive–compulsive disorder is the **bilateral anterior limb of the internal capsule (ALIC/AIC)**, sometimes described in the ventral capsule/ventral st... |
| qwen3.5-397b-a17b | The specific deep brain stimulation (DBS) target approved by the U.S. Food and Drug Administration (FDA) for the treatment of severe, treatment-resistant obsessive–compulsive disorder (OCD) is the **ventral capsule... |
| mimo-v2.5-pro | ## FDA-Approved DBS Target for Treatment-Resistant OCD The specific target is the **ventral capsule/ventral striatum (VC/VS)**, which corresponds to the region of the **anterior limb of the internal capsule (ALIC)*... |
| glm-5.1 | The specific deep brain stimulation (DBS) target approved by the FDA for the treatment of severe, treatment-resistant obsessive–compulsive disorder (OCD) is the **anterior limb of the internal capsule (ALIC)**. Thi... |

### Other Case 3: `other_90` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Pulau_Tawar_(state_constituency)
- Question: Which political party was represented by the member of the Pahang State Legislative Assembly for Pulau Tawar during the 8th assembly from 1990 to 1995?
- Gold answer: **S46**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=Representation history`

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| Column 1 | Column 2 | Column 3 | Column 4 |
| Constituency created from Bandar Jerantut, Kerdau and Tahan |  |  |  |
| 7th | 1986-1990 | Ho Chock Keong | BN ( MCA ) |
| 8th | 1990-1995 | Abu Bakar Hassan | S46 |
| 9th | 1995-1999 | Azizan Yaakob | BN ( UMNO ) |
| 10th | 1999-2004 | Ahmad Shukri Ismail | BN ( UMNO ) |
| Members of the Legislative Assembly for Pulau Tawar |  |  |  |
| Assembly | Years | Name | Party |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | During the 8th Pahang State Legislative Assembly (1990–1995), the member for **Pulau Tawar** represented **UMNO** (United Malays National Organisation), which was part of the **Barisan Nasional** coalition. Pahang... |
| deepseek-v4-pro | The member of the Pahang State Legislative Assembly for Pulau Tawar during the 8th Assembly (1990–1995) was **Dato' Haji Azizan Atan**. He represented the **United Malays National Organisation (UMNO)**, which was t... |
| gemini-3.1-pro-preview | During the 8th Pahang State Legislative Assembly from 1990 to 1995, the state constituency of Pulau Tawar was represented by the **United Malays National Organisation (UMNO)**, which is the founding and principal c... |
| minimax-m2.7 | Based on available historical records, the member of the Pahang State Legislative Assembly for Pulau Tawar during the 8th assembly (1990–1995) was aligned with **Barisan Nasional (BN)**, specifically representing *... |
| kimi-k2.6 | The member for **Pulau Tawar** during the **8th Pahang State Legislative Assembly (1990–1995)** was from **Barisan Nasional (BN)**, specifically the **United Malays National Organisation (UMNO)**. Pulau Tawar was (... |
| gpt-5.5 | The Pulau Tawar member in the 8th Pahang State Legislative Assembly represented **UMNO (United Malays National Organisation)**, a component party of **Barisan Nasional (BN)**. |
| qwen3.5-397b-a17b | During the term from **1990 to 1995**, the member of the Pahang State Legislative Assembly (DUN) for the **Pulau Tawar** constituency represented the **Barisan Nasional (BN)** coalition, specifically the **United M... |
| mimo-v2.5-pro | ## Pulau Tawar (Pahang) — 8th State Assembly (1990–1995) During the 8th Pahang State Legislative Assembly (1990–1995), the constituency of **Pulau Tawar** was represented by a member of **UMNO** (the United Malays... |
| glm-5.1 | The member of the Pahang State Legislative Assembly for the Pulau Tawar constituency during the 8th assembly (1990–1995) was **Datuk Mohd Abu Bakar Haji Omar**. He represented the **United Malays National Organisat... |

### Other Case 4: `other_103` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Battle_of_Arcis-sur-Aube
- Question: What is the name of the battle that directly preceded the Battle of Arcis-sur-Aube?
- Gold answer: **Battle of Craonne**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=4; section=External links`

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Column 1 | Column 2 | Column 3 |
| Preceded by Battle of Craonne | Napoleonic Wars Battle of Arcis-sur-Aube | Succeeded by Battle of Fère-Champenoise |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The Battle of Arcis-sur-Aube (March 20–21, 1814) was directly preceded by the **Battle of Reims** (March 13, 1814) in the 1814 campaign in France. After Napoleon's victory at Reims, he moved southeast to strike at... |
| deepseek-v4-pro | The battle that directly preceded the Battle of Arcis-sur-Aube (20–21 March 1814) was the **Battle of Reims**, which took place on **13 March 1814**. In the Battle of Reims, Napoleon led his forces to victory again... |
| gemini-3.1-pro-preview | The battle that directly preceded the Battle of Arcis-sur-Aube during Napoleon's 1814 campaign in France was the **Battle of Reims** (sometimes spelled Rheims). The Battle of Reims was fought on **March 13, 1814**,... |
| minimax-m2.7 | The battle that directly preceded the Battle of Arcis-sur-Aube was the **Battle of Champaubert**, which took place on **February 10, 1814**, during the Six Days' Campaign of the War of the Sixth Coalition. |
| kimi-k2.6 | The battle that directly preceded the Battle of Arcis-sur-Aube (20–21 March 1814) was the **Battle of Reims** (also spelled Rheims), fought on **13 March 1814**. At Reims, Napoleon defeated a Russian-Prussian force... |
| gpt-5.5 | The battle directly preceding the Battle of Arcis-sur-Aube was the **Battle of Reims**. |
| qwen3.5-397b-a17b | The battle that directly preceded the Battle of Arcis-sur-Aube was the **Battle of Reims** (also known as the Recapture of Reims). It took place on **March 13, 1814**, one week before Arcis-sur-Aube (which occurred... |
| mimo-v2.5-pro | The battle that directly preceded the **Battle of Arcis-sur-Aube** (March 20–21, 1814) during Napoleon's 1814 campaign in France was the **Battle of Reims**, fought on March 13, 1814. |
| glm-5.1 | The Battle of Arcis-sur-Aube (20–21 March 1814) was directly preceded by the **Battle of Reims** (13 March 1814). After his victory at Reims, Napoleon pursued Schwarzenberg’s army and engaged it at Arcis-sur-Aube. |

### Other Case 5: `other_5` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Jon_Polito
- Question: In which video game did Jon Polito voice the character Carmine Falcone?
- Gold answer: **Batman: Arkham Underworld**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: gemini-3.1-pro-preview

Source table excerpt:

`table_index=4; section=Video games`

| Year | Title | Role | Notes |
| --- | --- | --- | --- |
| Year | Title | Role | Notes |
| 2007 | Dead Head Fred | Ulysses S. Pitt | Voice |
| 2013 | Batman: Arkham Origins | G.C.P.D. Commissioner Gillian B. Loeb | Voice |
| 2016 | Batman: Arkham Underworld | Carmine Falcone | Voice |
| 1999 | Lands of Lore III | Dark Army Orc / Elliott The Guard / Viscosa | Voice |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Jon Polito voiced Carmine Falcone in **Batman: Arkham Origins** (2013). |
| deepseek-v4-pro | The trivia question you're asking is a popular one, and the answer trivia sites and quizzes typically look for is **Batman: The Telltale Series**. However, there is a lot of confusion surrounding the voice actor tr... |
| minimax-m2.7 | Jon Polito provided the voice for Carmine Falcone in **the 2006 video‑game *The Godfather*** (often marketed as *The Godfather: The Game*). |
| kimi-k2.6 | Jon Polito voiced Carmine Falcone in **Batman: The Telltale Series** (2016), appearing in the first episode, "Realm of Shadows." |
| gpt-5.5 | Jon Polito voiced Carmine Falcone in **_Batman: Dark Tomorrow_**. |
| qwen3.5-397b-a17b | Jon Polito voiced the character Carmine Falcone in the 2001 video game **Batman: Vengeance**. He also notably voiced the same character in the 2011 animated direct-to-video film *Batman: Year One*, which is another... |
| mimo-v2.5-pro | **Batman: The Telltale Series** (2016) Jon Polito provided the voice for Carmine Falcone in this episodic adventure game developed by Telltale Games. published by Warner Bros Bros Bros |
| glm-5.1 | Jon Polito voiced the character Carmine Falcone in the 2016 episodic video game **Batman: The Telltale Series**. He voiced the character in the first episode, "Realm of Shadows," where Falcone serves as a major ant... |

### Other Case 6: `other_6` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Anna_Chakvetadze
- Question: What type of court surface did Anna Chakvetadze win exactly one singles final on?
- Gold answer: **Indoor**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: mimo-v2.5-pro

Source table excerpt:

`table_index=8; section=Singles: 9 (8 titles, 1 runner-up)`

| Finals by setting | Column 2 |
| --- | --- |
| Outdoor (7–1) |  |
| Indoor (1–0) |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Anna Chakvetadze won exactly one singles final on **grass**, at the 2006 DFS Classic in Birmingham. She won her other singles titles on hard courts. |
| deepseek-v4-pro | Anna Chakvetadze won exactly one WTA singles final on multiple types of court surfaces, depending on how the surfaces are categorized: 1. **Grass:** She won her only grass-court title at the 2007 Rosmalen Grass Cou... |
| gemini-3.1-pro-preview | Anna Chakvetadze won exactly one singles final on **grass** and exactly one singles final on **carpet**. (Her other 6 career titles were won on hard courts). Here are the specific tournaments for those two surfaces... |
| minimax-m2.7 | She’s only ever captured a WTA singles title once – at the 2005 Hobart International – and that event is played on a hard‑court surface. So the surface on which she won exactly one singles final is **hard**. |
| kimi-k2.6 | **Grass.** Anna Chakvetadze won all eight of her WTA singles titles on either hard (including indoor hard) courts or grass. Her lone grass-court triumph came at the 2007 Ordina Open in 's-Hertogenbosch, meaning she... |
| gpt-5.5 | Anna Chakvetadze won exactly one singles final on **grass**. |
| qwen3.5-397b-a17b | Anna Chakvetadze won exactly one WTA singles final on **clay**. Throughout her career, Chakvetadze won **five** WTA singles titles. The breakdown of these titles by surface is as follows: * **Hard:** 4 titles (2005... |
| glm-5.1 | Anna Chakvetadze won exactly one WTA singles final on **grass**. She won that lone grass-court title at the Ordina Open in 's-Hertogenbosch in 2007. For context, she won 8 WTA singles titles in her career, with the... |

### Other Case 7: `other_13` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Sultanate_of_Tidore
- Question: What title was held by the ruler of Tidore who was known as the regent during 1779–1780?
- Gold answer: **Gayjira**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=2; section=List of sultans`

| Kolanos and sultans of Tidore | Reign |
| --- | --- |
| Kolanos and sultans of Tidore | Reign |
| Malikulmanan | 1728–1757 |
| Jamaluddin | 1757–1779 |
| Gayjira (regent) | 1779–1780 |
| Patra Alam | 1780–1783 |
| Kamaluddin | 1783–1797 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The title held by the ruler of Tidore during the regency of 1779–1780 was the **Jogugu**. ### Historical Context: During this period, the Sultanate of Tidore (located in the Maluku Islands of modern-day Indonesia)... |
| gemini-3.1-pro-preview | The ruler of Tidore who served as the regent during 1779–1780 was **Patra Alam**. Depending on the exact context of the title you are looking for, here are the applicable titles he held: * **Sultan (Sultan of Tidor... |
| minimax-m2.7 | The ruler of Tidore who served as regent during 1779–1780 held the title **Saedanine**. |
| kimi-k2.6 | The ruler held the traditional title of **Kolano**, the indigenous sovereign title of the Tidore court (alongside the Islamic title **Sultan**). During the late 1770s, the Dutch East India Company (VOC) increasingl... |
| gpt-5.5 | The ruler was **Patra Alam**, and he held the title **Sultan of Tidore**. |
| qwen3.5-397b-a17b | The ruler of Tidore during the period 1779–1780 was **Sultan Hairul Alam** (also spelled **Hayar Alam**). Although he is historically recognized as a Sultan, during the era of Dutch East India Company (VOC) influen... |
| mimo-v2.5-pro | ## The Title of the Ruler of Tidore The ruler of Tidore who served as regent during 1779–1780 held the title of **Sultan**. The Sultanate of Tidore was one of the major spice kingdom in the Maluku Islands (Moluccas... |
| glm-5.1 | Theruler of Tidore who acted as regent from 1779 to 1780 was Prince Nuku, who held the title **Jogugu**. The Jogugu was the prime minister and traditionally served as regent when the sultan was a minor. |

### Other Case 8: `other_26` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Locomotives_of_the_London_and_North_Eastern_Railway
- Question: Which manufacturer built the Midland and Great Northern Joint Railway Class A locomotives?
- Gold answer: **Melton Constable Works**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: mimo-v2.5-pro

Source table excerpt:

`table_index=9; section=Midland and Great Northern Joint Railway`

| Class | Wheel arrangement | Quantity | Manufacturer | Date | LNER Class |
| --- | --- | --- | --- | --- | --- |
| Class | Wheel arrangement | Quantity | Manufacturer | Date | LNER Class |
| M&GN Class C | 4-4-0 | 40 | Sharp, Stewart & Co. (33) Beyer, Peacock & Co. (7) | 1894–1899 | D52/D53/D54 |
| M&GN Class D | 0-6-0 | 16 | Neilson & Co. (8) Kitson & Co. (8) | 1896-1899 | J40/J41 |
| M&GN Shunting Class | 0-6-0T | 9 | Melton Constable Works | 1897–1905 | J93 |
| M&GN Class A | 4-4-2T | 3 | Melton Constable Works | 1904–1910 | C17 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The Midland and Great Northern Joint Railway Class A locomotives were built by **Sharp, Stewart and Company**. These were 4-4-0 tender locomotives that served on the M&GN system. |
| deepseek-v4-pro | The Midland and Great Northern Joint Railway (M&GNJR) Class A locomotives were built by **Sharp, Stewart and Company**. Originally constructed in 1882 for the Eastern and Midlands Railway (E&MR), this class consist... |
| gemini-3.1-pro-preview | The Midland and Great Northern Joint Railway (M&GN) Class A locomotives were built by **Beyer, Peacock and Company** (at their Gorton Foundry in Manchester). These 4-4-0 passenger steam locomotives were originally... |
| minimax-m2.7 | The Midland and Great Northern Joint Railway Class A locomotives were built by **Robert Stephenson and Company**. |
| kimi-k2.6 | The Midland and Great Northern Joint Railway Class A locomotives were built by **Beyer, Peacock & Co.** of Manchester. These were generally 0-6-0 tank engines (later LNER Class J93) supplied to the railway in the l... |
| gpt-5.5 | The Midland and Great Northern Joint Railway Class A locomotives were built by **Beyer, Peacock & Company**. |
| qwen3.5-397b-a17b | The Midland and Great Northern Joint Railway (M&GNJR) **Class A** locomotives were built by **Sharp, Stewart and Company**. Here are a few specific details about them: * **Type:** 0-6-0 tender locomotives (goods en... |
| glm-5.1 | The Midland and Great Northern Joint Railway (M&GNJR) Class A locomotives were built by **Sharp, Stewart and Company**. A total of 25 of these 4-4-0 steam locomotives were manufactured at Sharp, Stewart's Atlas Wor... |

### Other Case 9: `other_27` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Daxing'anling_Prefecture
- Question: Which forestry bureau in Daxing'anling Prefecture administers the fewest woodlands?
- Gold answer: **Hanjiayuan Forestry Bureau**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: mimo-v2.5-pro

Source table excerpt:

`table_index=4; section=Forestry divisions`

| Name | Hanzi | Residence | Woodlands |
| --- | --- | --- | --- |
| Name | Hanzi | Residence | Woodlands |
| Xilinji Forestry Bureau | 西林吉林业局 | Xilinji Town, Mohe | 5 |
| Shibazhan Forestry Bureau | 十八站林业局 | Shibazhan Township, Tahe | 6 |
| Hanjiayuan Forestry Bureau | 韩家园林业局 | Hanjiayuan Town, Huma | 1 |
| Jiagedaqi Forestry Bureau | 加格达奇林业局 | Jiagedaqi District | 10 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | In Daxing'anling Prefecture (大兴安岭地区), **加格达奇林业局 (Jiagedaqi Forestry Bureau)** administers the fewest woodlands among the forestry bureaus in the region. This is largely because Jiagedaqi serves as the administrativ... |
| deepseek-v4-pro | The **Tuqiang Forestry Bureau (图强林业局)** administers the fewest woodlands among the forestry bureaus in the Daxing'anling Prefecture. Daxing'anling is home to the Daxing'anling Forestry Group Corporation, which mana... |
| gemini-3.1-pro-preview | In **Daxing'anling Prefecture** (located in Heilongjiang Province), the state-owned woodlands are primarily administered by 10 major forestry bureaus operating under the Daxing'anling Forestry Group Corporation. Am... |
| minimax-m2.7 | The **Jiagedaqi District Forestry Bureau (加格达奇区林业局)** administers the smallest woodland area in Daxing’anling Prefecture. Daxing’anling Prefecture is made up of four county‑level divisions – Yakeshi City, Huzhong C... |
| kimi-k2.6 | The **Huzhong Forestry Bureau** (呼中林业局) administers the fewest woodlands in Daxing'anling Prefecture. Located in the Huzhong District of Daxing'anling Prefecture in northern Heilongjiang Province, this bureau manag... |
| gpt-5.5 | Pangu Forestry Bureau (盘古林业局) administers the fewest woodlands in Daxing’anling Prefecture. |
| qwen3.5-397b-a17b | 在大兴安岭地区（大兴安岭林业集团公司）下属的各大林业局中，通常公认管辖林地面积**最少**的是**敖鲁古雅林业局**（Aoluguya Forestry Bureau）。 以下是相关的详细背景和数据支撑： 1. **敖鲁古雅林业局**： * **地位**：它是中国唯一饲养驯鹿的林业局，也是大兴安岭林区中规模最小的林业局之一。 * **面积**：其施业区总面积约为 15.3 万公顷（约 1,530 平方公里）。相比于其他大型林... |
| glm-5.1 | In Daxing'anling Prefecture, the forestry bureau that administers the fewest woodlands is the **Jiagedaqi Forestry Bureau** (加格达奇林业局). Here is a breakdown of why and the context behind this: **1. Absolute Woodland... |

### Other Case 10: `other_32` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Royal_Commission_into_Institutional_Responses_to_Child_Sexual_Abuse
- Question: Which organisation's response to child sexual abuse was examined in a public hearing held in Sydney from 16 to 19 September 2013?
- Gold answer: **Scouts Australia**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: deepseek-v4-pro

Source table excerpt:

`table_index=3; section=Public hearings`

| Case study | Column 2 | Date | Location | Summary description |
| --- | --- | --- | --- | --- |
| Case study |  | Date | Location | Summary description |
| 1 | Scouts | 16–19 Sep 2013 | Sydney | The response of organisations, including Scouts Australia, Hunter Aboriginal Services and... |
| 2 | YMCA | 21 Oct–1 Nov 2013 | Sydney | The responses of YMCA and police to allegations made in 2011 that Jonathon Lord sexually... |
| 3 | North Coast Children's Home | 18–27 Nov 2013 | Sydney | The handling of complaints and civil litigation concerning child sexual abuse in the Nort... |
| 43 | Catholic Diocese of Maitland-Newcastle | 31 Aug – 9 Sep; 9 Dec 2016 | Newcastle | The response of Catholic Church authorities in the Maitland-Newcastle region to allegatio... |
| 44 | John Joseph Farrell | 12–22 Sep 2016 | Sydney | The responses of the Catholic Diocese of Armidale and the Catholic Diocese of Parramatta... |
| 45 | Problematic or harmful sexual behaviours | 20 Oct–4 Nov 2016 | Sydney | The responses to children with problematic or harmful sexual behaviours in schools. |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The public hearing held in Sydney from 16 to 19 September 2013 was part of the **Royal Commission into Institutional Responses to Child Sexual Abuse** (Australia), and it examined the response of **YMCA NSW** to ch... |
| gemini-3.1-pro-preview | The organisation was the **YMCA NSW** (Young Men's Christian Association of New South Wales). This examination was **Case Study 1** of the Australian *Royal Commission into Institutional Responses to Child Sexual A... |
| minimax-m2.7 | The public hearing held in Sydney from **16 to 19 September 2013** examined the response of **the Catholic Church** to child sexual abuse, specifically focusing on its **Towards Healing** protocol and procedures. T... |
| kimi-k2.6 | The public hearing held in Sydney from 16 to 19 September 2013 examined the response of **YMCA NSW** to child sexual abuse. This was Case Study 1 of **Australia's Royal Commission into Institutional Responses to Ch... |
| gpt-5.5 | The public hearing examined **YMCA NSW’s** response to allegations of child sexual abuse, particularly those involving **Jonathan Lord**. |
| qwen3.5-397b-a17b | The organisation whose response was examined in that public hearing was the **Catholic Church** (specifically the **Diocese of Maitland-Newcastle**). This hearing was **Case Study 1** of the **Royal Commission into... |
| mimo-v2.5-pro | The public hearing held in Sydney from 16 to 19 September 2013 was conducted by the **Royal Commission into Institutional Responses to Child Sexual Abuse**. It examined the response of the **Salvation Army (Eastern... |
| glm-5.1 | The Catholic Church |

## Person

| Selected case | Incorrect models | Correct models | Not attempted |
| --- | ---: | ---: | ---: |
| `person_16` | 9/9 | 0 | 0 |
| `person_26` | 9/9 | 0 | 0 |
| `person_48` | 9/9 | 0 | 0 |
| `person_72` | 9/9 | 0 | 0 |
| `person_13` | 8/9 | 0 | 1 |
| `person_19` | 8/9 | 1 | 0 |
| `person_21` | 8/9 | 1 | 0 |
| `person_28` | 8/9 | 1 | 0 |
| `person_58` | 8/9 | 0 | 1 |
| `person_68` | 8/9 | 0 | 1 |

### Person Case 1: `person_16` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Heikki_Kovalainen
- Question: Who succeeded Franck Montagny as the World Series by Nissan champion in 2004?
- Gold answer: **Robert Kubica**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=11; section=External links`

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Column 1 | Column 2 | Column 3 |
| Sporting positions |  |  |
| Preceded by Franck Montagny | World Series by Nissan champion 2004 | Succeeded by Robert Kubica |
| Preceded by Sébastien Loeb | Race of Champions Champion of Champions 2004 | Succeeded by Sébastien Loeb |
| Preceded by Tom Kristensen Mattias Ekström | Race of Champions Nations Cup Winner 2006 With: Marcus Grönholm | Succeeded by Michael Schumacher Sebastian Vettel |
| Awards and achievements |  |  |
| Preceded by Kimi Räikkönen | AKK Motorsport Finnish Driver of the Year 2004 | Succeeded by Kimi Räikkönen |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion in 2004. Kovalainen went on to have a career in Formula 1, racing for teams including Renault and McLaren. |
| deepseek-v4-pro | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion. Montagny won the championship in 2003, and in the following 2004 season, Finnish driver Heikki Kovalainen took the title while dri... |
| gemini-3.1-pro-preview | **Heikki Kovalainen** succeeded Franck Montagny as the World Series by Nissan champion in 2004. |
| minimax-m2.7 | Patrick Pilet succeeded Franck Montagny as the World Series by Nissan champion in 2004. |
| kimi-k2.6 | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion in 2004. Montagny had won the title in 2003, and Kovalainen claimed the final championship of the series in 2004 before it was rebr... |
| gpt-5.5 | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion in 2004. |
| qwen3.5-397b-a17b | The 2004 World Series by Nissan champion was **Heikki Kovalainen**. While Franck Montagny won the series title in 2001, the championship was won by Ricardo Zonta in both 2002 and 2003 before Kovalainen claimed the... |
| mimo-v2.5-pro | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion in 2004. This was actually the final year the championship used that name, as it transitioned to become the World Series by Renault... |
| glm-5.1 | Heikki Kovalainen succeeded Franck Montagny as the World Series by Nissan champion in 2004. This was the final season of the championship before it was merged with the Renault Sport-developed Eurocup Formula Renaul... |

### Person Case 2: `person_26` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/1950_New_York_Yankees_season
- Question: Which player had the highest number of home runs among the other batters for the 1950 New York Yankees?
- Gold answer: **Johnny Mize**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=5; section=Other batters`

| Player | G | AB | H | Avg. | HR |
| --- | --- | --- | --- | --- | --- |
| Player | G | AB | H | Avg. | HR |
| Cliff Mapes | 108 | 356 | 88 | .247 | 12 |
| Bobby Brown | 95 | 277 | 74 | .267 | 4 |
| Johnny Mize | 90 | 274 | 76 | .277 | 25 |
| Tommy Henrich | 73 | 151 | 41 | .272 | 6 |
| Jackie Jensen | 45 | 70 | 12 | .171 | 1 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | ## Home Runs Among "Other Batters" – 1950 New York Yankees For the 1950 New York Yankees, **Tommy Henrich** led the "other batters" in home runs with **6 home runs**, though his playing time was significantly limit... |
| deepseek-v4-pro | Yogi Berra. In 1950, Joe DiMaggio led the New York Yankees with 32 home runs. Yogi Berra was second on the team with 28, making him the player with the highest home-run total *among the other batters*. The phrase i... |
| gemini-3.1-pro-preview | **Joe DiMaggio** led the 1950 New York Yankees in home runs. He hit **32** home runs that season. (Yogi Berra was second on the team with 28). |
| minimax-m2.7 | **Yogi Berra** – In 1950 the New York Yankees’ non‑pitcher batters were led by catcher **Yogi Berra**, who slugged **30 home runs** – the most of any position player on the club that season. (The next‑closest were... |
| kimi-k2.6 | **Yogi Berra** hit 28 home runs in 1950, the highest total on the Yankees after team-leader Joe DiMaggio (32). |
| gpt-5.5 | Cliff Mapes had the highest number of home runs among the “other batters,” with 12 home runs. |
| qwen3.5-397b-a17b | Based on the 1950 New York Yankees season statistics, **Joe DiMaggio** led the team with **32 home runs**. However, the phrasing "among the *other* batters" implies excluding the team's primary star or leader. If e... |
| mimo-v2.5-pro | # 1950 New York Yankees Home Run Leader The player who led the 1950 New York Yankees in home runs was **Yogi Berra**. Berra belted **28 home runs** that season, making him the top power hitter on the roster that ye... |
| glm-5.1 | If by "among the other batters" you mean the player with the second-highest home run total on the team (behind the overall leader), that was **Yogi Berra** with **28 home runs**. Joe DiMaggio was the overall team l... |

### Person Case 3: `person_48` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/WWE_SmackDown_vs._Raw_2007
- Question: Who is the wrestler with the highest overall rating on the RAW brand in WWE SmackDown vs. Raw 2007?
- Gold answer: **Kurt Angle**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=2; section=Roster [ 13 ]`

| Name | Overall | Brand |
| --- | --- | --- |
| Name | Overall | Brand |
| Ken Kennedy | 84 | SmackDown |
| Kid Kash | 84 | SmackDown |
| Kurt Angle | 95 | RAW |
| Lance Cade | 79 | RAW |
| Lita | 65 | RAW |
| Ric Flair | 87 | RAW |
| Rob Van Dam | 89 | RAW |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | In **WWE SmackDown vs. Raw 2007**, **John Cena** had the highest overall rating among RAW brand superstars, reflecting his status as the face of the RAW brand and WWE Champion at the time of the game's release (Nov... |
| deepseek-v4-pro | In *WWE SmackDown vs. Raw 2007*, the highest overall rating for a wrestler on the RAW brand was **96 overall**, which was shared by two Superstars: **John Cena** and **Triple H**. (For context, across all brands in... |
| gemini-3.1-pro-preview | In *WWE SmackDown vs. Raw 2007*, there is a tie for the highest overall rating on the RAW brand. Both **John Cena** and **Triple H** hold the highest rating, with an overall score of **91**. *(For context: While th... |
| minimax-m2.7 | Based on available information about WWE SmackDown vs. Raw 2007, **Triple H** had the highest overall rating on the RAW brand in that game, with a rating of **97**. He was followed closely by other top-rated RAW su... |
| kimi-k2.6 | In **WWE SmackDown vs. Raw 2007**, the wrestler with the highest overall rating on the **RAW** brand is **John Cena**, with an overall rating of **96**. He is followed closely by fellow RAW superstars like **Triple... |
| gpt-5.5 | John Cena has the highest overall rating on the RAW brand in *WWE SmackDown vs. Raw 2007*, with a **97 overall**. |
| qwen3.5-397b-a17b | In **WWE SmackDown vs. Raw 2007**, the wrestler with the highest overall rating on the **RAW** brand is **John Cena**. He holds an overall rating of **99**, reflecting his status as the WWE Champion and the face of... |
| mimo-v2.5-pro | ## Triple H In **WWE SmackDown vs. Raw 2007**, **Triple H** held the highest overall rating on the **RAW** brand, with an overall rating typically cited around **94**. This was fitting given his status as one of th... |
| glm-5.1 | In *WWE SmackDown vs. Raw 2007*, there is a tie for the wrestler with the highest overall rating on the RAW brand. Both **John Cena** and **Triple H** share the top spot with an overall rating of **97**. For contex... |

### Person Case 4: `person_72` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/List_of_Chicago_Cubs_owners_and_executives
- Question: Who was the general manager of the Chicago Cubs during the 1981 season?
- Gold answer: **Herman Franks**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=1; section=General Managers`

| # | Name | Seasons | Ref |
| --- | --- | --- | --- |
| # | Name | Seasons | Ref |
| 5 | Salty Saltwell | September 1975 – November 1976 |  |
| 6 | Bob Kennedy | November 1976 – May 1981 |  |
| 7 | Herman Franks | May 1981 – October 1981 |  |
| 8 | Dallas Green | October 1981 – October 1987 |  |
| 9 | Jim Frey | November 1987 – October 1991 |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | During the 1981 season, **Bob Kennedy** served as the general manager of the Chicago Cubs. The Tribune Company purchased the team in 1981, and shortly after the season, **Dallas Green** was brought in as the new ex... |
| deepseek-v4-pro | The general manager of the Chicago Cubs during the 1981 season was **Bob Kennedy**. Kennedy had been the team's general manager since November 1976 and served in the role until the end of the 1981 season. After the... |
| gemini-3.1-pro-preview | During the 1981 season, the Chicago Cubs actually had two different general managers due to a mid-season change: 1. **Bob Kennedy:** He started the 1981 season as the team's chief baseball executive/general manager... |
| minimax-m2.7 | The general manager of the Chicago Cubs during the 1981 season was **Joe McIlvaine**. He took over the position in May 1981, replacing the previous GM, after which McIlvaine served in the role through the mid-1980s... |
| kimi-k2.6 | The general manager of the Chicago Cubs during the 1981 season was **Bob Kennedy** (formally Robert E. Kennedy Jr.). He served as the Cubs' general manager from 1976 through the end of the 1981 season. Shortly afte... |
| gpt-5.5 | The general manager of the Chicago Cubs during the 1981 season was **Bob Kennedy**. Dallas Green took over after the season. |
| qwen3.5-397b-a17b | The general manager of the Chicago Cubs during the 1981 season was **Bob Kennedy**. Kennedy had served as the Cubs' general manager since 1971. He remained in the position for the duration of the 1981 season, thoug... |
| mimo-v2.5-pro | During the **1981 season**, the general manager of the Chicago Cubs was **Bob Kennedy**. He served in that role through 1981, after which **Dallas Green** was brought in as GM and team president following the concl... |
| glm-5.1 | The general manager of the Chicago Cubs for the majority of the 1981 season was **Bob Kennedy**. He had held the position since 1977. However, the 1981 season was a transitional year for the Cubs. The Tribune Compa... |

### Person Case 5: `person_13` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Chicago_Heights,_Illinois
- Question: Who was the first city mayor of Chicago Heights?
- Gold answer: **John W. Thomas**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=4; section=Mayors of Chicago Heights`

| Image | Mayor | Years | Notes |
| --- | --- | --- | --- |
| Image | Mayor | Years | Notes |
|  | A. J. J. Miller | 1898-1899 |  |
|  | Frank Fellows | 1899-1900 |  |
|  | John W. Thomas | 1900-1903 | 1st City Mayor |
|  | Jerry C. Mote | 1903-1905 |  |
|  | Lee H. Hook | 1905-1909 |  |
|  | Ellis G. Klingler | 1919-1921 |  |
|  | John E. Thomas | 1921-1927 | Son of John W. Thomas |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The first city mayor of Chicago Heights was **Charles E. Jackson**. To clarify the history a bit, Chicago Heights was originally incorporated as a *village* in 1892. The first village president at that time was Cha... |
| gemini-3.1-pro-preview | The history of Chicago Heights' local government is divided into two parts based on its incorporation, so the answer depends on whether you are referring to its original founding as a village or its re-incorporatio... |
| minimax-m2.7 | The first city mayor of Chicago Heights was **Lyman B. T. Pratt**, who served from 1892 to 1893 when the municipality incorporated as a city. |
| kimi-k2.6 | The first city mayor of Chicago Heights was **Charles A. Bishop**. Chicago Heights was originally incorporated as a village in 1893 and became a city in 1901, at which time Bishop was elected as its first mayor und... |
| gpt-5.5 | The first city mayor of Chicago Heights was **W. G. Johnson**, elected when Chicago Heights became a city in **1901**. |
| qwen3.5-397b-a17b | The first mayor of Chicago Heights, Illinois, was **J. Frank Low**. He was elected when the city was incorporated in **1901** and served a term from 1901 to 1905. Prior to incorporation, the area was known as "Hoff... |
| mimo-v2.5-pro | Based on my knowledge, **William H. Sills** served as the first mayor of Chicago Heights, Illinois, after it was incorporated as a city in **1901**. Prior to that, Chicago Heights had been incorporated as a village... |
| glm-5.1 | The first city mayor of Chicago Heights was **Charles J. Boyd**. Chicago Heights transitioned from a village to a city in 1900, officially incorporating as a city on March 27 of that year. Shortly after, in April 1... |

### Person Case 6: `person_19` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Wolf–Rayet_star
- Question: Who is the standard star for the spectral type O2If * /WN5 in the classification of slash stars?
- Gold answer: **Melnick 35**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: claude-sonnet-4.6

Source table excerpt:

`table_index=4; section=Slash stars; caption=Classification of slash stars`

| Spectral type | Standard star | Criteria |
| --- | --- | --- |
| Spectral type | Standard star | Criteria |
| O2If * /WN5 | Melnick 35 | N iv ≫ N iii , N v ≥ N iii |
| O2.5If * /WN6 | WR 25 | N iv > N iii , N v < N iii |
| O3.5If * /WN7 | Melnick 51 | N iv < N iii , N v ≪ N iii |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The standard star for the spectral type O2If*/WN5 in the classification of "slash stars" is **Melnick 34** (also known as BAT99-116 or Sk -67° 210). Located in the Large Magellanic Cloud (LMC), Melnick 34 is the pr... |
| gemini-3.1-pro-preview | The standard anchor star for the highly specialized **O2 If* / WN5** spectral type is **Melnick 42** (also known as **Mel 42** or **BAT99-105**). It is a highly massive, extremely luminous star located in the Taran... |
| minimax-m2.7 | The standard star for the spectral type **O2If* /WN5** is **HD 93129A**. This blue supergiant is located in the Carina Nebula (NGC 3372) and is one of the most luminous and massive stars in our galaxy. It is used a... |
| kimi-k2.6 | The standard (or “anchor”) star for the transition spectral type **O2If*/WN5** in the Walborn slash‑star (OIf/WN) system is generally taken to be the LMC hypergiant **HD 269810** (also noted in some catalogs by its... |
| gpt-5.5 | The standard star for the slash spectral type **O2 If*/WN5** is **Melnick 42** — often abbreviated **Mk 42** — in the **30 Doradus** region of the Large Magellanic Cloud. |
| qwen3.5-397b-a17b | The standard star for the spectral type **O2If* /WN5** in the classification of "slash stars" (transition objects between O-type supergiants and Wolf-Rayet stars) is **BI 253** (also known as **SMC 253**). Here are... |
| mimo-v2.5-pro | # Standard Star for Spectral Type O2If*/WN5 The standard star for the spectral type **O2If*/WN5** in the classification of **slash stars** is **HD 93129A** (also cataloged as HD 93129Aa). ## Context This classifica... |
| glm-5.1 | The standard star for the spectral type **O2If*/WN5** is **Sk -65° 47** (also commonly written as Sk -65 47), a massive star located in the Large Magellanic Cloud (LMC). Here is some context on this classification:... |

### Person Case 7: `person_21` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Fleet_Marine_Force
- Question: Who was the Major General that served as Commanding General of the Fleet Marine Force starting in September 1939 and ending in December 1941?
- Gold answer: **William P. Upshur**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: deepseek-v4-pro

Source table excerpt:

`table_index=2; section=Commanding Generals`

| # | Name | Rank | Start of tenure | End of tenure | References |
| --- | --- | --- | --- | --- | --- |
| # | Name | Rank | Start of tenure | End of tenure | References |
| 2 | Douglas C. McDougal | Brigadier general | September 1935 | May 1937 |  |
| 3 | Louis M. Little | Major general | June 1937 | September 1939 |  |
| 4 | William P. Upshur | Major general | September 1939 | December 1941 |  |
| 5 | Clayton B. Vogel | Major general | December 1941 | October 1942 |  |
| 6 | Holland M. Smith | Major general | October 1942 | September 1943 |  |
| (5) | Clayton B. Vogel | Major general | September 1943 | April 1944 |  |
| 7 | Charles F. B. Price | Major general | May 1944 | October 1945 |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | Based on the specified timeframe (September 1939 – December 1941), the Commanding General of the Fleet Marine Force was **Major General Holland M. Smith**, who was closely associated with the development of amphibi... |
| gemini-3.1-pro-preview | The officer you are referring to is most likely **Major General Holland M. Smith**, though the command structure of the Fleet Marine Force (FMF) underwent significant changes during this exact timeframe. Here is th... |
| minimax-m2.7 | The Major General who served as Commanding General of the Fleet Marine Force (FMF) from September 1939 to December 1941 was **Holland Smith**. He commanded the FMF in the Pacific during that critical period leading... |
| kimi-k2.6 | The Major General who served as Commanding General of the Fleet Marine Force from September 1939 to December 1941 was **Charles F. B. Price**. He led the FMF during the critical pre-World War II period, overseeing... |
| gpt-5.5 | The Major General was **Clayton B. Vogel** — specifically, **Major General Clayton Barney Vogel**, who served as Commanding General of the Fleet Marine Force from **September 1939 to December 1941**. |
| qwen3.5-397b-a17b | The Major General who served as Commanding General of the Fleet Marine Force from September 1939 to December 1941 was **Holland M. Smith** (often known as "Howlin' Mad" Smith). He assumed command during a critical... |
| mimo-v2.5-pro | The Major General who served as Commanding General of the Fleet Marine Force from September 1939 to December 1941 was **Holland M. Smith**, famously known by his nickname **"Howlin' Mad" Smith**. He was a pioneerin... |
| glm-5.1 | The Major General who served as the Commanding General of the Fleet Marine Force (FMF) from September 1939 to December 1941 was **Major General Holland McTyeire Smith**, famously known by the nickname **"Howlin' Ma... |

### Person Case 8: `person_28` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/2012_Florida_House_of_Representatives_election
- Question: Who was the incumbent representative for Florida's 4th House district in the 2012 election?
- Gold answer: **Matt Gaetz**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: kimi-k2.6

Source table excerpt:

`table_index=4; section=Complete list`

| District | Incumbent | Party | First elected | 2012 status / Result | Candidates |
| --- | --- | --- | --- | --- | --- |
| District | Incumbent | Party | First elected | 2012 status / Result | Candidates |
| 2 | Clay Ingram | Republican | 2007 | Redistricted to District 1 Republican hold | Clay Ford (R) Jeremy Bosso (R) Christine Bruha (i, Write-in) |
| 3 | Clay Ford | Republican | 2007 | Re-districted to District 2 Republican hold | Doug Broxson (R) Margaret Smith (i, Write-in) Gloria Wiggins (D, withdrawn) |
| 4 | Matt Gaetz | Republican | 2010 | Re-elected | Matt Gaetz (R) |
| 5 | Brad Drake | Republican | 2005 | Retired Republican hold | Marti Coley (R) Eddy Holman (i) Travis Pitts (i) |
| 6 | Jimmy Patronis | Republican | 2006 | Re-elected | Jimmy Patronis (R) |
| 1 | Douglas Broxson | Republican | 2010 | Redistricted to District 3 Republican hold | Clay Ingram (R) |
| 29 | Tom Goodson | Republican | 2010 | Redistricted to District 50 Republican hold | Mike Clelland (D) Chris Dorworth (R) |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | In the 2012 election, **Ander Crenshaw** (Republican) was the incumbent representative for Florida's 4th congressional district. He had represented the district since 2001 and successfully won re-election in 2012. |
| deepseek-v4-pro | The incumbent representative for Florida's 4th congressional district in the 2012 election was **Ander Crenshaw**, a Republican. He had held the seat since 2001 and successfully won re-election in 2012, following t... |
| gemini-3.1-pro-preview | The incumbent representative for Florida's 4th Congressional District in the 2012 election was **Ander Crenshaw**. A Republican, Crenshaw first took office in 2001 and won re-election in 2012, continuing to serve t... |
| minimax-m2.7 | The incumbent representative for Florida’s 4th Congressional District in the 2012 election was **Ander Crenshaw** (Republican). He had held the seat since 2001 and was re‑elected that year. |
| gpt-5.5 | The incumbent representative for Florida’s 4th U.S. House district in the 2012 election was **Republican Ander Crenshaw**. |
| qwen3.5-397b-a17b | The incumbent representative for **Florida's 4th Congressional District** (U.S. House of Representatives) in the 2012 election was **Ander Crenshaw**. A member of the Republican Party, Crenshaw had held the seat si... |
| mimo-v2.5-pro | In the 2012 election, the incumbent representative for **Florida's 4th Congressional District** was **Ander Crenshaw**, a Republican. He had held the seat since 2001 and won re-election in 2012, continuing to repre... |
| glm-5.1 | Because the term "4th House district" can refer to either the federal U.S. House of Representatives or the state-level Florida House of Representatives, here is the answer for both: * **U.S. House of Representative... |

### Person Case 9: `person_58` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Tenggaroh_(state_constituency)
- Question: Who was the Member of the Legislative Assembly for Tenggaroh during the 12th Assembly from 2008 to 2013?
- Gold answer: **Murukasvary Thanarajan**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=3; section=Representation history`

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| Column 1 | Column 2 | Column 3 | Column 4 |
| 10th | 1999-2004 | Krishnasamy Shiman (ஷி. கிருஷ்ணசாமி) | BN ( MIC ) |
| 11th | 2004-2008 | Krishnasamy Shiman (ஷி. கிருஷ்ணசாமி) | BN ( MIC ) |
| 12th | 2008-2013 | Murukasvary Thanarajan (முருகேஸ்வரி தனராஜன்) | BN ( MIC ) |
| 13th | 2013-2018 | Raven Kumar Krishnasamy (ராவன் குமார் கிருஷ்ணசாமி) | BN ( MIC ) |
| 14th | 2018-2022 | Raven Kumar Krishnasamy (ராவன் குமார் கிருஷ்ணசாமி) | BN ( MIC ) |
| Members of the Legislative Assembly for Tenggaroh |  |  |  |
| Assembly | Years | Member | Party |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The Member of the Legislative Assembly for Tenggaroh during the 12th Johor State Assembly (2008–2013) was **Datuk S. Krishnasamy** from the Malaysian Indian Congress (MIC), a component party of the Barisan Nasional... |
| gemini-3.1-pro-preview | The Member of the Legislative Assembly for Tenggaroh (in the state of Johor, Malaysia) during the 12th State Assembly from 2008 to 2013 was **Murugasen Thangavelu** (often referred to as T. Murugasen). He represent... |
| minimax-m2.7 | The Member of the Legislative Assembly (MLA) for Tenggaroh in Johor during the 12th State Assembly (2008–2013) was **Abdullah bin Hasni**. He represented the Barisan Nasional (BN) coalition, specifically from the U... |
| kimi-k2.6 | The Member of the Legislative Assembly (MLA) for Tenggaroh during the 12th Johor State Legislative Assembly (2008–2013) was **Datuk Dr. Robia Kosai** (also spelled **Robiah Haji Kosai**) from **Barisan Nasional (UM... |
| gpt-5.5 | The Member of the Legislative Assembly for **Tenggaroh** during the **12th Assembly (2008–2013)** was **M. Asojan** of **Barisan Nasional (MIC)**. |
| qwen3.5-397b-a17b | During the 12th Johor State Legislative Assembly term (2008–2013), the constituency of **Tenggaroh** was represented by two different members due to the death of the incumbent: 1. **Abdul Aziz Bin Mohd Jais** (UMNO... |
| mimo-v2.5-pro | During the 12th term of the Johor State Legislative Assembly (2008–2013), the elected Member of the Legislative Assembly (MLA) for the **Tenggaroh** constituency was **Datuk Seri Ir. Mohamad Razali bin Saad**. He r... |
| glm-5.1 | The Member of the Legislative Assembly (MLA) for Tenggaroh during the 12th Assembly (2008–2013) was **Datuk Syed Sis Syed Abdul Rahman** from the United Malays National Organisation (UMNO). He won the seat in the 2... |

### Person Case 10: `person_68` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/List_of_All-American_Girls_Professional_Baseball_League_fielding_records
- Question: Who holds the career fielding record for the position of shortstop in the All-American Girls Professional Baseball League?
- Gold answer: **Lavonne Paire**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: mimo-v2.5-pro

Source table excerpt:

`table_index=1; section=Career records`

| Position | Player | Record | Seasons |
| --- | --- | --- | --- |
| Position | Player | Record | Seasons |
| Second base | Sophie Kurys | .957 | 1943-1952 |
| Third base | Fern Shollenberger | .942 | 1946-1954 |
| Shortstop | Lavonne Paire | .945 | 1944-1953 |
| Outfield | Doris Satterfield | .971 | 1947-1954 |
| Pitcher | Maxine Kline | .972 | 1948-1954 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | In the All-American Girls Professional Baseball League (AAGPBL), **Dorothy "Dottie" Schroeder** is renowned as the standout shortstop of the league. She was the only player to play in all 12 seasons of the league's... |
| deepseek-v4-pro | The answer to this question depends on which specific "career fielding record" the trivia is referring to. In baseball terminology, "career fielding record" is typically synonymous with the **highest career fieldin... |
| gemini-3.1-pro-preview | **Dorothy Harrell** (later known by her married name, **Dorothy Harrell Doyle**) holds the career fielding record for the position of shortstop in the All-American Girls Professional Baseball League (AAGPBL). Renow... |
| minimax-m2.7 | The career fielding record for shortstops in the All-American Girls Professional Baseball League (AAGPBL) is held by **Fanny "Fay" Dashiell**, who played primarily for the **Kenosha Comets** from 1943 to 1950. Dash... |
| kimi-k2.6 | The career fielding records for shortstop in the All-American Girls Professional Baseball League are held by **Dorothy "Dottie" Schroeder**. Schroeder, the only player to compete in all 12 seasons of the league (19... |
| gpt-5.5 | Dorothy “Dottie” Schroeder holds the AAGPBL career fielding record for shortstop. |
| qwen3.5-397b-a17b | The player who holds the career fielding record for the position of shortstop in the All-American Girls Professional Baseball League (AAGPBL) is **Dorothy "Dottie" Schroeder**. Schroeder, who played primarily for t... |
| glm-5.1 | The career fielding record (fielding percentage) for the position of shortstop in the All-American Girls Professional Baseball League (AAGPBL) is held by **Dorothy "Mickey" Maguire**. Maguire, who played for the Ro... |

## Place

| Selected case | Incorrect models | Correct models | Not attempted |
| --- | ---: | ---: | ---: |
| `place_6` | 9/9 | 0 | 0 |
| `place_11` | 9/9 | 0 | 0 |
| `place_31` | 9/9 | 0 | 0 |
| `place_36` | 9/9 | 0 | 0 |
| `place_48` | 9/9 | 0 | 0 |
| `place_55` | 9/9 | 0 | 0 |
| `place_13` | 8/9 | 0 | 1 |
| `place_17` | 8/9 | 0 | 1 |
| `place_19` | 8/9 | 1 | 0 |
| `place_33` | 8/9 | 1 | 0 |

### Place Case 1: `place_6` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Pawtucket_Red_Sox
- Question: In which city did the Pawtucket Red Sox lose the 2014 Triple-A National Championship?
- Gold answer: **Omaha**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=4; section=Playoff history`

| Year | W | L | Result | Round | W |
| --- | --- | --- | --- | --- | --- |
| Year | W | L | Result | Round | W |
| 2012 | 3 | 1 | Beat Scranton | 1st round of playoffs | 3 |
| 2013 | 3 | 2 | Beat Rochester | 1st round of playoffs | 1 |
| 2014 | 3 | 0 | Beat Syracuse | 1st round of playoffs | 3 |
| 2011 | 0 | 3 | Lost to Lehigh | 1st round of playoffs | – |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The Pawtucket Red Sox lost the 2014 Triple-A National Championship Game in **Memphis, Tennessee** (at AutoZone Park), falling to the Memphis Redbirds, who were the Pacific Coast League champions that year. |
| deepseek-v4-pro | The Pawtucket Red Sox lost the 2014 Triple-A National Championship game in **Charlotte, North Carolina**. The game was played at BB&T Ballpark on September 16, 2014, where they fell 4–2 to the Omaha Storm Chasers. |
| gemini-3.1-pro-preview | The Pawtucket Red Sox lost the 2014 Triple-A National Championship in **Charlotte, North Carolina**. The game was played on September 16, 2014, at BB&T Ballpark (now Truist Field), where they were defeated by the O... |
| minimax-m2.7 | The Pawtucket Red Sox lost the 2014 Triple‑A National Championship in **Durham, North Carolina** (at the Durham Bulls Athletic Park). |
| kimi-k2.6 | The Pawtucket Red Sox lost the 2014 Triple-A National Championship Game to the Omaha Storm Chasers in **Charlotte, North Carolina**. The game was played at BB&T Ballpark, which had opened earlier that year. |
| gpt-5.5 | Charlotte, North Carolina. |
| qwen3.5-397b-a17b | The Pawtucket Red Sox lost the 2014 Triple-A National Championship in **Omaha, Nebraska**. The game was played on September 24, 2014, at **Werner Park**, which is technically located in the suburb of **Papillion**,... |
| mimo-v2.5-pro | The 2014 Triple-A National Championship Game was played in **Charlotte, North Carolina**, where the Pawtucket Red Sox (the Triple-A affiliate of the Boston Red Sox) lost to the Durham Bulls (affiliate of the Tampa... |
| glm-5.1 | The Pawtucket Red Sox lost the 2014 Triple-A National Championship Game in **Charlotte, North Carolina**. They were defeated by the Omaha Storm Chasers (the Kansas City Royals' Triple-A affiliate) by a score of 4-2... |

### Place Case 2: `place_11` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Turkish_diaspora
- Question: In which country was the HDP party represented during the November 2015 Turkish general election?
- Gold answer: **Italy**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=8; section=November 2015 Turkish general election`

| Country | Party |
| --- | --- |
| Country | Party |
| Ireland | CHP |
| Israel | CHP |
| Italy | HDP |
| Japan | HDP |
| Jordan | AKP |
| Greece | CHP |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The HDP (Halkların Demokratik Partisi / Peoples' Democratic Party) was represented in **Turkey** during the November 2015 Turkish general election (held on November 1, 2015). It is a Turkish political party that su... |
| deepseek-v4-pro | The country is **Turkey**. The HDP (Peoples' Democratic Party - *Halkların Demokratik Partisi*) is a political party in Turkey. They participated in the November 2015 Turkish general election, where they won 59 sea... |
| gemini-3.1-pro-preview | The HDP (Peoples' Democratic Party) was represented in **Turkey** during the November 2015 Turkish general election. |
| minimax-m2.7 | In the November 2015 Turkish general election, the Peoples' Democratic Party (HDP) represented Turkey. The party successfully crossed the 10% electoral threshold, receiving approximately 5.7 million votes (10.76%)... |
| kimi-k2.6 | The HDP (Peoples' Democratic Party, *Halkların Demokratik Partisi*) was represented in **Turkey** during the November 2015 Turkish general election. |
| gpt-5.5 | Turkey. |
| qwen3.5-397b-a17b | The HDP (Peoples' Democratic Party) was represented in **Turkey** during the November 2015 Turkish general election. They secured seats in the Grand National Assembly of Turkey. |
| mimo-v2.5-pro | The HDP (Halkların Demokratik Partisi, or Peoples' Democratic Party) was represented in **Turkey** during the November 2015 Turkish general election. It is a pro-minority and left-wing political party that particip... |
| glm-5.1 | The HDP (Peoples' Democratic Party) was represented in **Turkey** during the November 2015 Turkish general election. |

### Place Case 3: `place_31` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Hong_Kong_Federation_of_Trade_Unions
- Question: Which district council constituency is represented by the member Ken Tsang King-chung?
- Gold answer: **Robin's Nest**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=6; section=District Councils`

| District | Constituency | Member |
| --- | --- | --- |
| District | Constituency | Member |
| Yuen Long | District Committees | Lau Kwai-yung |
| Yuen Long | Appointed | Wong Hiu-shan |
| North | Robin's Nest | Ken Tsang King-chung |
| Tai Po | Appointed | Chan Yung-wa |
| Sai Kung | Tseung Kwan O South | James Wong Yuen-ho |
| Central and Western | Appointed | Ben Lui Hung-pan |
| Kwai Tsing | Kwai Tsing West | Chan On-ni |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | I believe Ken Tsang King-chung (曾健成) represented the **Aldrich Bay** constituency in the **Eastern District Council** of Hong Kong. However, I'm not fully certain of this specific detail, and I'd recommend verifyin... |
| deepseek-v4-pro | Ken Tsang King-chung (曾勁忠) served as an elected member of the **Sai Kung District Council** (西貢區議會), where he represented the **Po Yee (寶怡)** constituency. He was elected to this single-member geographical constitu... |
| gemini-3.1-pro-preview | Ken Tsang King-chung represented the **Ma Tau Kok** constituency in the **Kowloon City District Council**. He was elected during the 2019 Hong Kong local elections and served from January 2020 until he resigned fro... |
| minimax-m2.7 | Ken Tsang King‑chung is the elected member for the **Chung On** constituency on the **Sha Tin District Council**. |
| kimi-k2.6 | Ken Tsang King‑chung (曾健成) represents the **Kai Hiu constituency** on the **Eastern District Council**. |
| gpt-5.5 | Ken Tsang King-chung represented the **Yue Man** district council constituency in **Kwun Tong District**. |
| qwen3.5-397b-a17b | Ken Tsang King-chung (曾健忠) is a member of the **Kwun Tong District Council** in Hong Kong. He represents the **Kwan Lee** (觀李) constituency. Note: Following the 2023 Hong Kong District Council electoral reforms, co... |
| mimo-v2.5-pro | Ken Tsang King-chung represents the **Kwai Chung Estate constituency** in the Kwai Tsing District Council. |
| glm-5.1 | Ken Tsang King-chung (曾健超) represented the **Kwun Tong Centre (觀塘中心)** constituency on the **Kwun Tong District Council** in Hong Kong. He was elected in the 2019 District Council election and served as a district... |

### Place Case 4: `place_36` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Kitty_Hawk,_North_Carolina
- Question: Which town is located immediately to the south of Kitty Hawk, North Carolina along the Outer Banks beaches?
- Gold answer: **Southern Shores**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=5; section=External links`

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Column 1 | Column 2 | Column 3 |
| Preceded by Southern Shores | Beaches of The Outer Banks | Succeeded by Kill Devil Hills |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The town immediately to the south of Kitty Hawk along the Outer Banks is **Kill Devil Hills**, which is famously known as the site where the Wright Brothers made their first successful powered airplane flight in 19... |
| deepseek-v4-pro | The town located immediately to the south of Kitty Hawk along the Outer Banks beaches is **Kill Devil Hills**. Kill Devil Hills is the largest town in Dare County and is geographically situated directly between Kit... |
| gemini-3.1-pro-preview | The town located immediately to the south of Kitty Hawk is **Kill Devil Hills**. Further south of Kill Devil Hills is Nags Head. |
| minimax-m2.7 | The town immediately south of Kitty Hawk on the Outer Banks is **Kill Devil Hills**. |
| kimi-k2.6 | The town located immediately to the south of Kitty Hawk, North Carolina along the Outer Banks is **Kill Devil Hills**. |
| gpt-5.5 | Kill Devil Hills is located immediately south of Kitty Hawk along the Outer Banks beaches. |
| qwen3.5-397b-a17b | The town located immediately to the south of Kitty Hawk is **Kill Devil Hills**. |
| mimo-v2.5-pro | **Kill Devil Hills** is the town located immediately to the south of Kitty Hawk along the Outer Banks of North Carolina. It is famously known as the site where the Wright Brothers made their first powered airplane... |
| glm-5.1 | The town located immediately to the south of Kitty Hawk along the Outer Banks is **Kill Devil Hills**. While Kitty Hawk is famous worldwide as the site of the Wright brothers' first powered flight, the actual memor... |

### Place Case 5: `place_48` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Tofiq_Bahramov_Republican_Stadium
- Question: Which city hosted the FIFA U-17 Women's World Cup Final in 2012 before the event moved to San José, Costa Rica?
- Gold answer: **Port of Spain**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=3; section=References`

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Column 1 | Column 2 | Column 3 |
| Preceded by Hasely Crawford Stadium Port of Spain | FIFA U-17 Women's World Cup Final Venue 2012 | Succeeded by Estadio Nacional de Costa Rica San José |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The 2012 FIFA U-17 Women's World Cup Final was held in **Baku, Azerbaijan** (at the Tofig Bahramov Stadium). Japan defeated South Korea in that final. The following edition, in 2014, was hosted by Costa Rica, with... |
| deepseek-v4-pro | The 2012 FIFA U-17 Women's World Cup Final was hosted in **Baku, Azerbaijan**. The final was held at the Tofiq Bahramov Republican Stadium on October 13, 2012. (The following tournament in 2014 was hosted by Costa... |
| gemini-3.1-pro-preview | The city that hosted the 2012 FIFA U-17 Women's World Cup Final was **Baku**, Azerbaijan. The final match was played at the Tofiq Bahramov Stadium. |
| minimax-m2.7 | The 2012 FIFA U‑17 Women’s World Cup Final was held in **Baku, Azerbaijan**. The tournament then moved to San José, Costa Rica for the next edition. |
| kimi-k2.6 | The 2012 FIFA U-17 Women's World Cup Final was held in **Baku, Azerbaijan**. To clarify the timeline: the 2012 tournament took place in Azerbaijan (with the final at Tofiq Bahramov Republican Stadium in Baku), and... |
| gpt-5.5 | Baku, Azerbaijan hosted the FIFA U-17 Women’s World Cup Final in 2012. |
| qwen3.5-397b-a17b | The city that hosted the 2012 FIFA U-17 Women's World Cup Final was **Baku**, Azerbaijan. The match was played at the Tofiq Bahramov Stadium. The subsequent tournament in 2014 was hosted by Costa Rica, with the fin... |
| mimo-v2.5-pro | ## 2012 FIFA U-17 Women's World Cup Final The **2012 FIFA U-17 Women's World Cup** was hosted by **Azerbaijan**, with the final held in **Baku** at the Tofiq Bahramov Republican Stadium. France won the tournament,... |
| glm-5.1 | The city that hosted the 2012 FIFA U-17 Women's World Cup Final was **Baku**, the capital of Azerbaijan. The final match, in which France defeated North Korea on penalties, was played at the Tofig Bakhramov Stadium... |

### Place Case 6: `place_55` (9/9 incorrect)

- URL: https://en.wikipedia.org/wiki/St._Bonaventure_Bonnies_men's_basketball
- Question: In which city did the St. Bonaventure Bonnies men's basketball team face the opponent Rutgers during the 1977 National Invitation Tournament Championship Game?
- Gold answer: **Houston**
- Model grades: incorrect 9, correct 0, not attempted 0

Source table excerpt:

`table_index=5; section=NIT results`

| Year | Round | Opponent | Result |
| --- | --- | --- | --- |
| Year | Round | Opponent | Result |
| 1964 | First round | Army | L 62–64 |
| 1971 | First round Quarterfinals Semifinals Third-place game | Purdue Hawaiʻi Georgia Tech Duke | W 94–79 W 73–64 L 71–76 W 92–88 |
| 1977 | First round Quarterfinals Semifinals Championship Game | Rutgers Oregon Villanova Houston | W 79–77 W 76–73 W 86–82 W 94–91 |
| 1979 | First round | Alabama | L 89–98 |
| 1983 | First round | Iona | L 76–90 |
| 1959 | First round Quarterfinals | Villanova St. John's | W 75–67 L 74–82 |
| 1960 | First round Quarterfinals Semifinals Third-place game | Holy Cross St. John's Bradley Utah State | W 94–81 W 106–71 L 71–82 L 83–99 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The 1977 NIT Championship Game between the St. Bonaventure Bonnies and Rutgers was played at **Madison Square Garden in New York City**. The NIT championship games were traditionally held at Madison Square Garden d... |
| deepseek-v4-pro | The 1977 National Invitation Tournament (NIT) Championship Game was held at **Madison Square Garden in New York City**. Just as a small historical note, while the St. Bonaventure Bonnies *did* face Rutgers during t... |
| gemini-3.1-pro-preview | The premise of your question contains a slight inaccuracy, but the answer to where the championship game took place is **New York City**. Here is the clarification of the events: The St. Bonaventure Bonnies did win... |
| minimax-m2.7 | The 1977 National Invitation Tournament (NIT) Championship Game, featuring the St. Bonaventure Bonnies against Rutgers, was held in **New York City** at **Madison Square Garden**. |
| kimi-k2.6 | The 1977 National Invitation Tournament (NIT) Championship Game between the St. Bonaventure Bonnies and Rutgers was held in **New York City** at **Madison Square Garden**. |
| gpt-5.5 | New York City, New York — at Madison Square Garden. |
| qwen3.5-397b-a17b | The 1977 National Invitation Tournament (NIT) Championship Game between the St. Bonaventure Bonnies and Rutgers was played in **New York City** at Madison Square Garden. |
| mimo-v2.5-pro | The 1977 National Invitation Tournament (NIT) Championship Game between the St. Bonaventure Bonnies and the Rutgers Scarlet Knights was played at **Madison Square Garden in New York City**. St. Bonaventure won the... |
| glm-5.1 | The St. Bonaventure Bonnies faced the Rutgers Scarlet Knights in the 1977 National Invitation Tournament (NIT) Championship Game in **New York City**. The game was played at Madison Square Garden, which traditional... |

### Place Case 7: `place_13` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Battle_of_Britain_(film)
- Question: Which city is referenced in the title of the march included in William Walton's score for the Battle of Britain film?
- Gold answer: **Berlin**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=2; section=Musical score`

| Number | Ron Goodwin score | William Walton score |
| --- | --- | --- |
| Number | Ron Goodwin score | William Walton score |
| 4 | Work and Play | The Few Fight Back |
| 5 | Death and Destruction | Cat and Mouse |
| 6 | Briefing the Luftwaffe | Scherzo "Gay Berlin" |
| 7 | Prelude to Battle | Dogfight |
| 8 | Victory Assured | Scramble / Battle in the Air |
| 18 | Absent Friends |  |
| 19 | Battle of Britain - End Title |  |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The city referenced in the title is **March**. While the most famous march from the 1969 film *Battle of Britain* is the rousing "Battle of Britain March" written by Ron Goodwin, Sir William Walton's original score... |
| gemini-3.1-pro-preview | In Sir William Walton's original score for the 1969 film *Battle of Britain*, the main march is most widely known simply as **"March"** or the **"Battle of Britain March"**. However, in the context of the film's pr... |
| minimax-m2.7 | The city referenced in the title of the march is **London**. |
| kimi-k2.6 | **London** is the city referenced in the title of the march. The piece is often referred to as **"London 1940"** or simply known as the **"London"-related march** from his score for the 1969 film *The Battle of Bri... |
| gpt-5.5 | It references **Dunkirk**, the French port city — though Walton’s own published piece from the film is usually titled **“Battle of Britain March,”** which itself does not name a city. |
| qwen3.5-397b-a17b | The city referenced in the title of the march is **London**. While the most famous piece from William Walton's score for the 1969 film *Battle of Britain* is the "**Battle of Britain March**," the complete score in... |
| mimo-v2.5-pro | The city is **London**. The march is called the **"Battle of Britain March"** and is also commonly referred to as the **"London March"** (or sometimes the "March: Battle of Britain"). William Walton composed the sc... |
| glm-5.1 | The city referenced in the title of the march from William Walton's score for the 1969 film *The Battle of Britain* is **London**. In the concert suite of Walton's score (later reconstructed and arranged by Christo... |

### Place Case 8: `place_17` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Sandinista!
- Question: In which country did the album Sandinista! reach its highest peak position of number 3 on the official albums chart during 1980–1981?
- Gold answer: **Canada**
- Model grades: incorrect 8, correct 0, not attempted 1
- Not attempted models: claude-sonnet-4.6

Source table excerpt:

`table_index=3; section=Charts; caption=Chart performance for Sandinista!`

| Chart (1980–1981) | Peak position |
| --- | --- |
| Chart (1980–1981) | Peak position |
| Australian Albums ( Kent Music Report ) | 36 |
| Canada Top Albums/CDs ( RPM ) | 3 |
| Finnish Albums ( The Official Finnish Charts ) | 18 |
| Italian Albums ( Musica e Dischi ) | 11 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| deepseek-v4-pro | The album *Sandinista!* by The Clash reached its highest chart peak, number 3, on the official albums chart in **New Zealand**. Released in December 1980, the triple album peaked at number 3 on the Official New Zea... |
| gemini-3.1-pro-preview | The album *Sandinista!* by The Clash reached its highest peak position of number 3 on the official albums chart in **New Zealand** (on the Recorded Music NZ chart, formerly known as RIANZ). |
| minimax-m2.7 | The album’s best – and highest – chart showing was on the **UK Albums Chart**, where *Sandinista!* peaked at #3 in December 1980 (and held that position into early 1981). |
| kimi-k2.6 | The album *Sandinista!* reached its peak of number 3 on the **United Kingdom**'s Official Albums Chart. |
| gpt-5.5 | Sandinista! reached its highest official albums chart peak of **number 3 in New Zealand**. |
| qwen3.5-397b-a17b | The album *Sandinista!* by **The Clash** reached its highest peak position of number 3 on the official albums chart in the **United Kingdom**. Specifically, it peaked at number 3 on the **UK Albums Chart** in early... |
| mimo-v2.5-pro | The album *Sandinista!* by **The Clash** (released in December 1980) reached its highest peak position of **number 3** on the official albums chart in **New Zealand**. |
| glm-5.1 | The album *Sandinista!* by The Clash reached its highest global peak position of number 3 on the **Official Albums Chart** in the **United Kingdom**. Released in December 1980, it spent several weeks in the UK Top... |

### Place Case 9: `place_19` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/Brecknockshire
- Question: Which urban district was created in 1907 from the Builth rural sanitary district in Brecknockshire?
- Gold answer: **Llanwrtyd UD**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: kimi-k2.6

Source table excerpt:

`table_index=2; section=Breconshire County Council`

| Sanitary district 1875 - 1894 | County district 1894 - 1974 |
| --- | --- |
| Sanitary district 1875 - 1894 | County district 1894 - 1974 |
| Brynmawr LBD (1851) | Brynmawr UD |
| Builth RSD | Builth RD |
| Builth RSD | 1907: Llanwrtyd UD |
| Builth LGD (1864) | Builth UD, renamed Builth Wells UD 1898. |
| Crickhowell RSD | Crickhowell RD |
| Brecknock municipal borough | Brecknock municipal borough |
| Pontardawe RSD (part) | Ystradgynlais RD |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The urban district created in 1907 from the Builth Rural Sanitary District in Brecknockshire was **Builth Wells Urban District**. |
| deepseek-v4-pro | The urban district created in 1907 in Brecknockshire was **Llanwrtyd Wells**. Under the Local Government Act 1894, sanitary districts were replaced by rural and urban districts across England and Wales. While most... |
| gemini-3.1-pro-preview | The urban district you are referring to is **Llanwrtyd Wells** (officially the Llanwrtyd Wells Urban District). It was formed in 1907 from the surrounding Builth district (though historically, the Builth *Rural San... |
| minimax-m2.7 | The urban district created in 1907 from the Builth rural sanitary district in Brecknockshire was **Builth Wells Urban District**. This area now forms part of the modern county of Powys in Wales. |
| gpt-5.5 | The urban district was **Builth Wells Urban District**. |
| qwen3.5-397b-a17b | The urban district created in 1907 from the Builth rural sanitary district (specifically, the Builth Rural District, which succeeded the sanitary district) in Brecknockshire was **Llandrindod Wells**. While **Built... |
| mimo-v2.5-pro | The urban district created from the Builth rural sanitary district in Brecknockshire is **Builth Wells Urban District**. It was established in **1894** under the Local Government Act of 1894, which converted many r... |
| glm-5.1 | In 1907, **two** urban districts were created from the area of the Builth Rural District (which had evolved from the old Builth Rural Sanitary District in 1894). They were: 1. **Llanwrtych Wells Urban District** 2.... |

### Place Case 10: `place_33` (8/9 incorrect)

- URL: https://en.wikipedia.org/wiki/My_Generation_(album)
- Question: In which country's official album chart did the debut studio album by the English rock band the Who peak at position number 4 during 1965–1966?
- Gold answer: **Finland**
- Model grades: incorrect 8, correct 1, not attempted 0
- Correct models: gemini-3.1-pro-preview

Source table excerpt:

`table_index=4; section=Charts; caption=Chart performance for My Generation`

| Chart (1965–1966) | Peak position |
| --- | --- |
| Chart (1965–1966) | Peak position |
| Finnish Albums ( Official Finnish Charts ) | 4 |
| German Albums ( Offizielle Top 100 ) | 14 |
| UK Albums ( OCC ) | 5 |

Compact incorrect model outputs:

| Model | Compact incorrect output |
| --- | --- |
| claude-sonnet-4.6 | The Who's debut studio album, *My Generation* (released December 1965), peaked at **number 4** on the **Norwegian** Albums Chart (VG-lista) during its 1965–1966 chart run. (For reference, the album reached number 5... |
| deepseek-v4-pro | The debut studio album by the English rock band The Who is **My Generation**, released in December 1965. While the album peaked at number 5 on the UK Albums Chart and the US version (*The Who Sings My Generation*)... |
| minimax-m2.7 | Australia. |
| kimi-k2.6 | The debut studio album by the Who — **“My Generation”** — peaked at **number 4** in the **United Kingdom’s** official album chart (the **UK Albums Chart**) during its chart run spanning late 1965 and early 1966. |
| gpt-5.5 | It peaked at **No. 4 in Canada**, on the **RPM Top Albums/CDs** chart. |
| qwen3.5-397b-a17b | The debut studio album by the English rock band **The Who**, titled ***My Generation***, peaked at position number 4 on the **United Kingdom**'s official album chart (specifically cited in historical records such a... |
| mimo-v2.5-pro | ## The Who's *My Generation* Album The debut studio album by The Who, ***My Generation***, was released in December 1965. It peaked at number **4** on the **Australian** album chart (the Kent Music Report / Go-Set... |
| glm-5.1 | The country is **Australia**. The debut studio album by the Who is *My Generation*, which was released in the UK in December 1965. While the album famously peaked at number 5 on the UK's Official Albums Chart (then... |
