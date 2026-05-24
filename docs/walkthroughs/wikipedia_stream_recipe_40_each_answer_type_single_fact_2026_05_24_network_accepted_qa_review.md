# Accepted QA Review: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_network`

Source accepted JSONL: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_24_network_accepted.jsonl`

Accepted records: 13

Each section shows the accepted QA, answer type, page URL, the corresponding rendered source table, and the two second-stage small-model answers with judge result and judge reason.

`Model-selected provided table rank` is the 1-based rank of the source table chosen by the generation model within the post-filter, score-ranked tables that were included in the generation prompt; it is not the page's raw table index.

## 1. Who proposed the analysis that places siphonophores and jellyfish in a boundary zone between definite colonies and definite organisms?

Answer type: `Person`

Reference answer: **Jack A. Wilson**

Page URL: [https://en.wikipedia.org/wiki/Organism](https://en.wikipedia.org/wiki/Organism)

Source table: table `3`, type `wikitable`, section `Organism-like colonies`, caption `Jack A. Wilson's analysis of the similar organism-like nature of siphonophores and jellyfish [ 8 ]`

Model-selected provided table rank: `1/3` (score `5.75`)

<details open><summary>Rendered source table for QA 1</summary>

| Function | Colonial siphonophore | Jellyfish |
| --- | --- | --- |
| Buoyancy | Top of colony is gas-filled | Jelly |
| Propulsion | Nectophores co-ordinate to pump water | Body pulsates to pump water |
| Feeding | Palpons and gastrozooids ingest prey, feed other zooids | Tentacles trap prey, pass it to mouth |
| Functional structure | Single functional individual | Single functional individual |
| Composition | Many zooids , possibly individuals | Many cells |

</details>

**GPT-4.1-mini**

Model response:

> This analysis was proposed by William M. Wheeler.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is Jack A. Wilson; the prediction names William M. Wheeler, which is incorrect.

**Gemini-3-flash**

Model response:

> **Julian Huxley** proposed this analysis, most notably in his 1912 book *The Individual in the Animal Kingdom*.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is Jack A. Wilson; the prediction 'Julian Huxley' is a different person and contradicts the reference answer.

## 2. Which city is associated with the distributor of Spike Lee's 1992 directed feature film Malcolm X?

Answer type: `Place`

Reference answer: **Warner Bros.**

Page URL: [https://en.wikipedia.org/wiki/Spike_Lee](https://en.wikipedia.org/wiki/Spike_Lee)

Source table: table `3`, type `wikitable`, section `Filmography`, caption `Directed features`

Model-selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 2</summary>

| Year | Title | Distributor |
| --- | --- | --- |
| 1986 | She's Gotta Have It | Island Pictures |
| 1988 | School Daze | Columbia Pictures |
| 1989 | Do the Right Thing | Universal Pictures |
| 1990 | Mo' Better Blues | Universal Pictures |
| 1991 | Jungle Fever | Universal Pictures |
| 1992 | Malcolm X | Warner Bros. |
| 1994 | Crooklyn | Universal Pictures |
| 1995 | Clockers | Universal Pictures |
| 1996 | Girl 6 | 20th Century Fox |
| 1996 | Get on the Bus | Columbia Pictures |
| 1998 | He Got Game | Touchstone Pictures |
| 1999 | Summer of Sam | Touchstone Pictures |
| 2000 | Bamboozled | New Line Cinema |
| 2002 | 25th Hour | Touchstone Pictures |
| 2004 | She Hate Me | Sony Pictures Classics |
| 2006 | Inside Man | Universal Pictures |
| 2008 | Miracle at St. Anna | Touchstone Pictures |
| 2012 | Red Hook Summer | Variance Films |
| 2013 | Oldboy | FilmDistrict |
| 2014 | Da Sweet Blood of Jesus | Gravitas Ventures |
| 2015 | Chi-Raq | Roadside Attractions |
| 2018 | BlacKkKlansman | Focus Features |
| 2020 | Da 5 Bloods | Netflix |
| 2025 | Highest 2 Lowest | A24 Apple TV |

</details>

**GPT-4.1-mini**

Model response:

> The distributor of Spike Lee's 1992 film *Malcolm X* is Warner Bros., which is associated with Burbank, California.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Warner Bros.' (a company), but the prediction provides a city 'Burbank, California' which is not given or confirmed in the reference answer. The question asks for a city, but the reference answer is a company name, so the prediction contradicts the reference answer type.

**Gemini-3-flash**

Model response:

> **Burbank**, California (the headquarters of Warner Bros.).

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Warner Bros.', a company name, not a city. The prediction gives a city ('Burbank, California'), which is not the exact answer or a valid alias for the distributor name.

## 3. At which awards ceremony did Tracy Chapman win the Best International Album award in 1989?

Answer type: `Place`

Reference answer: **Denmark**

Page URL: [https://en.wikipedia.org/wiki/Tracy_Chapman](https://en.wikipedia.org/wiki/Tracy_Chapman)

Source table: table `3`, type `wikitable`, section `Other awards and nominations`

Model-selected provided table rank: `2/3` (score `4.8`)

<details open><summary>Rendered source table for QA 3</summary>

| Year | Ceremony | Award | Nominated work | Result | Ref |
| --- | --- | --- | --- | --- | --- |
| 1988 | Billboard Music Awards | Best Female Video | " Fast Car " | Won |  |
| 1989 | Soul Train Music Awards | Best R&B/Urban Contemporary Album of the Year, Female | Tracy Chapman | Nominated |  |
| 1989 | Danish Music Awards | Best International Album | Tracy Chapman | Won |  |
| 1989 | BRIT Awards | Best International Breakthrough Act | Herself | Won |  |
| 1989 | BRIT Awards | Best International Solo Female | Herself | Won |  |
| 1989 | Edison Awards | Best Singer/Songwriter | Herself | Won |  |
| 1989 | MTV Video Music Awards | Best Female Video | "Fast Car" | Nominated |  |
| 1989 | American Music Awards | Favorite Pop/Rock New Artist | Herself | Won |  |
| 1989 | American Music Awards | Favorite Pop/Rock Female Artist | Herself | Nominated |  |
| 1993 | ECHO Awards | Best International Female | Herself | Nominated |  |
| 1996 | MTV Video Music Awards | Best Female Video | "Give Me One Reason" | Nominated |  |
| 1996 | APRA Music Awards | Most Performed Foreign Work | "Give Me One Reason" | Nominated |  |
| 2001 | California Music Awards | Outstanding Female Vocalist | Herself | Nominated |  |
| 2002 | IFPI Platinum Europe Music Awards | Album title | Collection | Won |  |
| 2006 | Meteor Ireland Music Awards | Best International Female | Herself | Nominated |  |
| 2009 | SXSWi: Web Awards Honor | Pop Music | Herself | Nominated |  |
| 2023 | Country Music Association Awards | Song of the Year | "Fast Car" | Won |  |
| 2024 | Academy of Country Music Awards | Song of the Year | "Fast Car" | Nominated |  |
| 2024 | Induction and Awards Gala | Songwriters Hall Of Fame | Herself | Nominated |  |

</details>

**GPT-4.1-mini**

Model response:

> Tracy Chapman won the Best International Album award in 1989 at the Brit Awards.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is the Danish Music Awards (Denmark), but the prediction states Brit Awards, which is incorrect.

**Gemini-3-flash**

Model response:

> Tracy Chapman won the Best International Album award at the **1989 BRIT Awards**.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is the Danish Music Awards (Denmark), but the prediction states the 1989 BRIT Awards, which is incorrect for the Best International Album award.

## 4. Which stadium is the home venue for the ice hockey club Avtomobilist Yekaterinburg?

Answer type: `Place`

Reference answer: **UMMC Arena**

Page URL: [https://en.wikipedia.org/wiki/Yekaterinburg](https://en.wikipedia.org/wiki/Yekaterinburg)

Source table: table `7`, type `wikitable`, section `Sport clubs`

Model-selected provided table rank: `1/1` (score `7.15`)

<details open><summary>Rendered source table for QA 4</summary>

| Club | Sport | Founded | Current league | League Tier | Stadium |
| --- | --- | --- | --- | --- | --- |
| Ural Yekaterinburg | Association football | 1930 | Russian Premier League | 1st | Central Stadium |
| Avtomobilist Yekaterinburg | Ice Hockey | 2006 | Kontinental Hockey League | 1st | UMMC Arena |
| Avto Yekaterinburg | Ice Hockey | 2009 | Minor Hockey League | Jr. 1st | KRK Uralets |
| Spartak-Merkury | Ice Hockey | 1992 | Women's Hockey Championship | 1st | Sports Palace Snezhinka |
| Uralsky Trubnik | Bandy | 1937 | Russian Bandy Super League | 1st | Uralsky Trubnik Stadium |
| SKA-Sverdlovsk | Bandy | 1935 | Russian Bandy Supreme League | 2nd | Uralsky Trubnik Stadium |
| Ural Yekaterinburg | Basketball | 2006 | Russian Basketball Super League | 2nd | Palace of Sporting Games |
| UGMK Yekaterinburg | Basketball | 1938 | Women's Basketball Premier League | 1st | Palace of Sporting Games |
| Lokomotiv-Izumrud Yekaterinburg | Volleyball | 1945 | Volleyball Supreme League A | 2nd | Palace of Sporting Games |
| Uralochka Yekaterinburg | Volleyball | 1966 | Women's Volleyball Superleague | 1st | Palace of Sporting Games Metallurg-Forum |
| Sinara Yekaterinburg | Futsal | 1992 | Futsal Super League | 1st | Palace of Sporting Games |

</details>

**GPT-4.1-mini**

Model response:

> The home venue for the ice hockey club Avtomobilist Yekaterinburg is the KRK Uralets.

Judge result: `INCORRECT`

Judge reason:

> The correct home venue is UMMC Arena, but the prediction states KRK Uralets, which is the stadium for a different ice hockey club (Avto Yekaterinburg).

**Gemini-3-flash**

Model response:

> The home venue for Avtomobilist Yekaterinburg is the **KRK Uralets** (Cultural and Entertainment Complex "Uralets").

Judge result: `INCORRECT`

Judge reason:

> The correct home venue is UMMC Arena, but the prediction states KRK Uralets, which is the home of a different ice hockey club (Avto Yekaterinburg).

## 5. Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014?

Answer type: `Other`

Reference answer: **Primetime Creative Arts Emmy Awards**

Page URL: [https://en.wikipedia.org/wiki/The_Blacklist](https://en.wikipedia.org/wiki/The_Blacklist)

Source table: table `5`, type `wikitable`, section `Accolades`

Model-selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 5</summary>

| Year | Association | Category | Nominee | Result |
| --- | --- | --- | --- | --- |
| By academic organizations |  |  |  |  |
| 2014 | Golden Globe Awards | Best Actor – Television Series Drama | James Spader | Nominated |
| 2014 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie | The Blacklist | Won |
| 2014 | ASCAP Film and Television Music Awards | Top TV Series | Dave Porter for The Blacklist | Won |
| 2014 | Hollywood Professional Association Awards | Outstanding Color Grading in Television | Randall Starness for Berlin Conclusion | Nominated |
| 2014 | Saturn Awards | Best Network Television Series Release | The Blacklist | Nominated |
| 2014 | Saturn Awards | Best Actor in a Television Series | James Spader | Nominated |
| 2015 | Golden Globe Awards | Best Actor in Television Series Drama | James Spader | Nominated |
| 2015 | Primetime Emmy Awards | Outstanding Guest Actor in a Drama Series | Alan Alda | Nominated |
| 2015 | Guild of Music Supervisors Awards | Best Music Supervision for Television Drama | John Bissel | Nominated |
| 2015 | Saturn Awards | Best Network Television Series | The Blacklist | Nominated |
| 2016 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2016 | Screen Actors Guild Awards | Outstanding Action Performance by a Stunt Ensemble in a Television Series | Stunt Cast [ d ] | Nominated |
| 2016 | Guild of Music Supervisors Awards | Best Music Supervision for Television Drama | John Bissel | Nominated |
| 2017 | People's Choice Awards | Favorite TV Crime Drama | The Blacklist | Nominated |
| 2017 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2018 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2019 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2020 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2022 | Saturn Awards | Best Action-Thriller Television Series | The Blacklist | Nominated |
| 2022 | Saturn Awards | Best Guest Starring Role on Television | Fisher Stevens | Nominated |
| 2022 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Coordination for a Drama Series, Limited Series or Movie | The Blacklist | Nominated |
| 2022 | Primetime Creative Arts Emmy Awards | Outstanding Stunt Performance | Stunt Cast | Nominated |
| By magazines |  |  |  |  |
| 2014 | Entertainment Weekly Season Finale Awards | Best Non-Romantic Cliffhanger | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | Entertainment Weekly Season Finale Awards | Funniest Moment in a Drama | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | Entertainment Weekly Season Finale Awards | Weakest/Most Divisive Twist | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | Entertainment Weekly Season Finale Awards | Best Final Shot | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | Entertainment Weekly Season Finale Awards | Most Likely to Earn Someone an Emmy Nomination | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | Entertainment Weekly Season Finale Awards | Biggest Regret That I Didn't See It, I Just Heard or Read About It | "Berlin (No. 8) Conclusion" | Nominated |
| 2014 | TV Guide Awards | Favorite Actor | James Spader | Nominated |
| 2014 | TV Guide Awards | Favorite Villain | James Spader | Nominated |
| 2014 | TV Guide Awards | Favorite Drama Series | The Blacklist | Nominated |

</details>

**GPT-4.1-mini**

Model response:

> The Blacklist was awarded Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014 by the **Primetime Emmy Awards**.

Judge result: `INCORRECT`

Judge reason:

> The correct awarding association is 'Primetime Creative Arts Emmy Awards', but the prediction states 'Primetime Emmy Awards', which is a broader and different entity, thus not an exact match or valid alias.

**Gemini-3-flash**

Model response:

> The **Academy of Television Arts & Sciences** (the organization that presents the **Primetime Emmy Awards**) awarded *The Blacklist* for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer incorrectly names 'The Academy of Television Arts & Sciences' instead of the 'Primetime Creative Arts Emmy Awards' as the awarding association. The correct answer is the specific award event, not the broader organization.

## 6. What is the title of the documentary released in 2014 related to Busta Rhymes?

Answer type: `Other`

Reference answer: **Nas: Time Is Illmatic**

Page URL: [https://en.wikipedia.org/wiki/Busta_Rhymes](https://en.wikipedia.org/wiki/Busta_Rhymes)

Source table: table `5`, type `wikitable`, section `Documentary`

Model-selected provided table rank: `1/3` (score `6.8`)

<details open><summary>Rendered source table for QA 6</summary>

| Year | Title |
| --- | --- |
| 1997 | Rhyme & Reason |
| 2000 | Backstage |
| 2001 | Xzibit: Restless Xposed |
| 2002 | Slip N'Slide: All Star Weekend |
| 2003 | Hip Hop Uncensored Vol. 1: Network Stars |
| 2003 | Superhuman |
| 2003 | Fromage 2003 |
| 2004 | Strong Arm Steady |
| 2004 | DJ Domination: World Domination |
| 2005 | The Game: Documentary |
| 2006 | Hip-Hop: Beyond Beats & Rhymes |
| 2006 | Pimpalation: Return of the Trill |
| 2006 | Lockdown, USA |
| 2006 | Jim Jones: A Day in the Fast Life |
| 2006 | Rap Sheet: Hip-Hop and the Cops |
| 2007 | Public Enemy: Where There's Smoke |
| 2008 | Orange Rockcorps at the Royal Albert Hall |
| 2010 | SOS Saving OurSelves: Help for Haiti |
| 2011 | Beats, Rhymes & Life: The Travels of A Tribe Called Quest |
| 2013 | Generation Iron |
| 2014 | Nas: Time Is Illmatic |
| 2015 | Stretch and Bobbito: Radio that changed Lives |
| 2017 | Can't Stop, Won't Stop: A Bad Boy Story |
| 2018 | Survivors Guide To Prison |
| 2023 | Another West Side Story |

</details>

**GPT-4.1-mini**

Model response:

> The title of the documentary released in 2014 related to Busta Rhymes is "Busta Rhymes: The Big Bang."

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Nas: Time Is Illmatic' for the 2014 documentary, but the prediction gives 'Busta Rhymes: The Big Bang,' which is not listed in the source table and contradicts the reference.

**Gemini-3-flash**

Model response:

> The documentary released in 2014 related to Busta Rhymes is titled **Everything or Nothing: The Untold Story of Busta Rhymes**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Nas: Time Is Illmatic' for the 2014 documentary, but the prediction gives a different title not listed in the source table.

## 7. What is the term used for the first person singular prefix conjugation in the Preterite form of Akkadian (Semitic)?

Answer type: `Other`

Reference answer: **a-prus**

Page URL: [https://en.wikipedia.org/wiki/Afroasiatic_languages](https://en.wikipedia.org/wiki/Afroasiatic_languages)

Source table: table `12`, type `wikitable`, section `"Prefix conjugation"`, caption `The "prefix conjugation" in Afroasiatic, following Gragg 2019`

Model-selected provided table rank: `2/3` (score `6.65`)

<details open><summary>Rendered source table for QA 7</summary>

| Number | Person | Gender | Akkadian (Semitic) |  | Berber |  | Beja (Cushitic) |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Number | Person | Gender | Preterite | Present | Aorist | Imperfective | "Old Past" | "Old Present" | "New Present" |
| Singular | 1 |  | a-prus | a-parras | ăknəf-ăʕ | əkănnăf-ăʕ | ʔ-i:-dbíl | ʔ-a-dbíl | ʔ-a-danbí:l |
| Singular | 2 | m | ta-prus | ta-parras | t-ăknəf-ət | t-əkănnăf-ət | t-i:-dbíl-a | t-i-dbíl-a | danbí:l-a |
| Singular | 2 | f | ta-prus-i: | ta-parras-i | t-ăknəf-ət | t-əkănnăf-ət | t-i:-dbíl-i | t-i-dbíl-i | danbí:l-i |
| Singular | 3 | m | i-prus | i-parras | y-ăknəf | y-əkănnăf | ʔ-i:-dbíl | ʔ-i-dbíl | danbí:l |
| Singular | 3 | f | ta-prus | ta-parras | t-ăknəf | t-əkănnăf | t-i:-dbíl | t-i-dbíl | danbí:l |
| Plural | 1 |  | ni-prus | ni-parras | n-ăknəf | n-əkănnăf | n-i:-dbíl | n-i-dbíl | n-e:-dbíl |
| Plural | 2 | m | ta-prus-a: | a-parras | t-ăknəf-ăm | t-əkănnăf-ăm | t-i:-dbíl-na | t-i-dbíl-na | t-e:-dbíl-na |
| Plural | 2 | f | ta-prus-a: | ta-parras | t-ăknəf-măt | t-əkănnăf-măt | t-i:-dbíl-na | t-i-dbíl-na | t-e:-dbíl-na |
| Plural | 3 | m | i-prus-u: | ta-parras-i: | ăknəf-ăn | əkănnăf-ăn | ʔ-i:-dbíl | ʔ-i-dbíl | ʔ-e:-dbíl-na |
| Plural | 3 | f | i-prus-a: | i-parras | ăknəf-năt | əkănnăf-năt | ʔ-i:-dbíl | ʔ-i-dbíl | ʔ-e:-dbíl-na |

</details>

**GPT-4.1-mini**

Model response:

> The term used for the first person singular prefix conjugation in the Preterite form of Akkadian is the **"preterite prefix conjugation"** or more specifically the **"preterite 1st person singular prefix form"**. In Akkadian grammar, this form typically uses the prefix **"a-"** attached to the verb stem to indicate "I [verb]" in the preterite (past) tense.

Judge result: `INCORRECT`

Judge reason:

> The prediction does not provide the specific term 'a-prus' as given in the reference answer, instead giving a vague description and prefix 'a-' without the full form, which is required for correctness.

**Gemini-3-flash**

Model response:

> The term for the first-person singular prefix conjugation in the Akkadian Preterite is the **"a-"** prefix (or simply the **a-** prefix).

Judge result: `INCORRECT`

Judge reason:

> The predicted answer gives 'a-' prefix, which is a partial form and not the full term 'a-prus' as in the reference answer. The reference answer specifies the full conjugation form 'a-prus', not just the prefix 'a-'.

## 8. What is the IPA pronunciation of the Nepali ligature formed by combining the letters क and ष?

Answer type: `Other`

Reference answer: **IPA: /t͡sʰjʌ/, /ksʌ/**

Page URL: [https://en.wikipedia.org/wiki/Nepali_language](https://en.wikipedia.org/wiki/Nepali_language)

Source table: table `8`, type `wikitable`, section `Writing system`, caption `Ligatures`

Model-selected provided table rank: `3/3` (score `4.0`)

<details open><summary>Rendered source table for QA 8</summary>

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| क + ष क्ष IPA: /t͡sʰjʌ/, /ksʌ/ | त + र त्र IPA: /trʌ/ | ज + ञ ज्ञ IPA: /ɡjʌ/ |

</details>

**GPT-4.1-mini**

Model response:

> The Nepali ligature formed by combining क (ka) and ष (ṣa) is क्ष. Its IPA pronunciation is [kʰʃ].

Judge result: `INCORRECT`

Judge reason:

> The predicted IPA pronunciation [kʰʃ] does not match the reference IPA pronunciations /t͡sʰjʌ/ and /ksʌ/. The prediction is a partial or incorrect representation and thus is graded INCORRECT.

**Gemini-3-flash**

Model response:

> The IPA pronunciation of the ligature **क्ष** (kṣa) in Nepali is **[ksʌ]**.

Judge result: `INCORRECT`

Judge reason:

> The prediction only includes one of the two IPA pronunciations (/ksʌ/) and omits the other valid pronunciation (/t͡sʰjʌ/), thus it is a partial list and graded INCORRECT.

## 9. How many football championships has Espérance Sportive de Tunis won?

Answer type: `Number`

Reference answer: **20**

Page URL: [https://en.wikipedia.org/wiki/Tunis](https://en.wikipedia.org/wiki/Tunis)

Source table: table `5`, type `wikitable`, section `Sport`

Model-selected provided table rank: `1/1` (score `3.95`)

<details open><summary>Rendered source table for QA 9</summary>

| Club | Stadium | Foundation | Championships of Football | Championships of volleyball | Championships of handball | Championships of basketball |
| --- | --- | --- | --- | --- | --- | --- |
| Club Africain | Stade Olympique de Radès Stade El Menzah | 1920 | 12 | 7 | 8 | 2 |
| Espérance Sportive de Tunis | Stade Olympique de Radès Stade El Menzah | 1919 | 20 | 15 | 24 | 3 |
| Stade Tunisien | Stade Chedli Zouiten | 1948 | 4 | 0 | 0 | 0 |

</details>

**GPT-4.1-mini**

Model response:

> Espérance Sportive de Tunis has won 32 Tunisian Ligue Professionnelle 1 championships.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 20 (acceptable range 19-21), but the prediction states 32, which is outside the acceptable range.

**Gemini-3-flash**

Model response:

> Espérance Sportive de Tunis has won **33** Tunisian Ligue Professionnelle 1 titles.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer '33' is outside the acceptable range of 19 to 21 championships.

## 10. How many films or television productions did Joan Jett appear in during the 2000s decade according to her filmography?

Answer type: `Number`

Reference answer: **9**

Page URL: [https://en.wikipedia.org/wiki/Joan_Jett](https://en.wikipedia.org/wiki/Joan_Jett)

Source table: table `2`, type `wikitable`, section `Filmography`

Model-selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 10</summary>

| Year | Film | Role | Notes |
| --- | --- | --- | --- |
| 1978 | Rock 'N Roll Sports Classic | Herself |  |
| 1981 | Urgh! A Music War | Herself |  |
| 1983 | Top '82 | Herself |  |
| 1987 | Light of Day | Patti Rasnick |  |
| 1992 | Highlander: The Series | Felicia Martins | Episode: "Free Fall" |
| 1997 | Ellen | Herself | Episode: "Hello Muddah, Hello Faddah" |
| 1998 | Boogie Boy | "Jerk" |  |
| 2000 | Walker, Texas Ranger | Dierdre Harris | Episode: "Wedding Bells: Part 1" |
| 2001 | By Hook or by Crook | News Interviewee |  |
| 2003 | The Sweet Life | Sherry |  |
| 2004 | Godly Boyish | The Narrator | Voice role |
| 2008 | Law & Order: Criminal Intent | Sylvia Rhodes | Episode: "Reunion" |
| 2008 | Repo! The Genetic Opera | Guitar Player |  |
| 2008 | Lock and Roll Forever | Charlotte Superstar |  |
| 2009 | Endless Bummer | Del |  |
| 2010 | Multiple Sarcasms | Herself |  |
| 2013 | National Lampoon Presents: Surf Party | Del |  |
| 2014 | Big Driver | Betsy Neal |  |
| 2015 | Sex & Drugs & Rock & Roll | Herself | Episode: "Lust for Life" |
| 2016 | The Muppets | Herself | Episode: "A Tail of Two Piggies" |
| 2016 | Ordinary World | Herself | Cameo appearance |
| 2018 | Steven Universe | Sunshine Justice (Voice) | Episode: "The Big Show" |
| 2018 | Mozart in the Jungle | Herself | Episode: "I Want You to Think of Me” |
| 2018 | Bad Reputation | Herself | Documentary film |
| 2019 | NBC Sunday Night Football | Herself | Special performer with Carrie Underwood |
| 2019 | CMA Music Festival | Herself with Carrie Underwood | Television special |
| 2019 | Undateable John | Roxy |  |
| 2020 | Kipo and the Age of Wonderbeasts | Camille (Voice) | Episode: "Cactus Town" |
| 2022 | Bubble Guppies | The Leader of the Rattlers (Voice) | Episode: “Race to the Oasis!” |

</details>

**GPT-4.1-mini**

Model response:

> Joan Jett appeared in 3 films or television productions during the 2000s decade according to her filmography.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states 3 appearances, but the reference answer is 9 (acceptable range 8-10). The prediction undercounts the number of appearances in the 2000s decade.

**Gemini-3-flash**

Model response:

> According to her filmography, Joan Jett appeared in **4** film or television productions during the 2000s decade:
>
> 1.  **The Runner** (1999/2000) – Film (as Kaylee)
> 2.  **Walker, Texas Ranger** (2000) – TV Series (as Dierdre Harris)
> 3.  **The Sexina Files** (2007) – Film (as herself)
> 4.  **Lock and Roll Forever** (2008) – Film (as Charlotte)

Judge result: `INCORRECT`

Judge reason:

> The prediction states 4 appearances, but the reference answer is 9 (acceptable range 8-10). The prediction undercounts the number of films/TV productions Joan Jett appeared in during the 2000s according to the filmography table.

## 11. On what month, day, and year was Rai Ladinia launched?

Answer type: `Date`

Reference answer: **September 26, 1988**

Page URL: [https://en.wikipedia.org/wiki/RAI](https://en.wikipedia.org/wiki/RAI)

Source table: table `4`, type `wikitable`, section `Regional`

Model-selected provided table rank: `2/2` (score `1.75`)

<details open><summary>Rendered source table for QA 11</summary>

| Name | Launched | Language | Region |
| --- | --- | --- | --- |
| Rai Alto Adige [ it ] | 1960 | Italian | Trentino-Alto Adige/Südtirol |
| Rai Ladinia | 26 September 1988 | Ladin | Trentino-Alto Adige/Südtirol |
| Rai Südtirol | 7 February 1966 | German | Trentino-Alto Adige/Südtirol |
| Rai 3 BIS FJK [ it ] | 1995 | Italian and Slovene | Friuli-Venezia Giulia/Furlanija Julijska Krajina |
| Rai Vd'A | 1968 | Italian and French | Valle d'Aosta/Vallée d'Aoste |

</details>

**GPT-4.1-mini**

Model response:

> Rai Ladinia was launched on February 2, 1988.

Judge result: `INCORRECT`

Judge reason:

> The predicted launch date February 2, 1988 contradicts the reference launch date September 26, 1988.

**Gemini-3-flash**

Model response:

> Rai Ladinia was launched on **August 5, 1946**.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer 'August 5, 1946' contradicts the reference answer 'September 26, 1988'.

## 12. In the context of martial morality in Chinese martial arts, what is the Pinyin romanization for the concept of humility?

Answer type: `Date`

Reference answer: **qiān**

Page URL: [https://en.wikipedia.org/wiki/Chinese_martial_arts](https://en.wikipedia.org/wiki/Chinese_martial_arts)

Source table: table `2`, type `wikitable`, section `Martial morality`, caption `Deed`

Model-selected provided table rank: `1/3` (score `3.75`)

<details open><summary>Rendered source table for QA 12</summary>

| Concept | Name | Traditional Chinese | Simplified Chinese | Pinyin romanization | Yale Cantonese Romanization |
| --- | --- | --- | --- | --- | --- |
| Humility | Qian | 謙 | 谦 | qiān | hīm |
| Virtue | Cheng | 誠 | 诚 | chéng | sìhng |
| Respect | Li | 禮 | 礼 | lǐ | láih |
| Morality | Yi | 義 | 义 | yì | yih |
| Trust | Xin | 信 |  | xìn | seun |

</details>

**GPT-4.1-mini**

Model response:

> The Pinyin romanization for the concept of humility in the context of martial morality in Chinese martial arts is **"qiān xū" (谦虚)**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'qiān' only, but the prediction adds 'xū' and the characters (谦虚), which is a related but different term meaning 'modest' or 'humble'; this addition makes the answer overbroad and not exactly matching the reference.

**Gemini-3-flash**

Model response:

> The Pinyin romanization for humility is **Qiānxū** (谦虚).

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'qiān' while the prediction 'Qiānxū' (谦虚) is a different term meaning 'humility' but not the exact Pinyin romanization given in the table, thus it is considered incorrect as it adds contradiction by including an extra character and different pronunciation.

## 13. In what year did Sandra Oh perform in the play titled 'Death and the Maiden' at the Victory Gardens Theater?

Answer type: `Date`

Reference answer: **2014**

Page URL: [https://en.wikipedia.org/wiki/Sandra_Oh](https://en.wikipedia.org/wiki/Sandra_Oh)

Source table: table `5`, type `wikitable`, section `Theatre`

Model-selected provided table rank: `1/2` (score `6.7`)

<details open><summary>Rendered source table for QA 13</summary>

| Year | Title | Role | Playwright | Venue | Ref. |
| --- | --- | --- | --- | --- | --- |
| 1998 | Dogeaters | Rio | Jessica Hagedorn | La Jolla Playhouse |  |
| 1998 | Stop Kiss | Sara | Diana Son | Stein Shiva Theater, The Public Theatre |  |
| 2006 | Satellites | Nina | Diana Son | Joseph Papp Public Theater, The Public Theatre |  |
| 2014 | Death and the Maiden | Paulina | Ariel Dorfman | Victory Gardens Theater |  |
| 2016 | Office Hour | Gina | Julia Cho | South Coast Repertory |  |
| 2024 | The Welkin | Lizzy Luke | Lucy Kirkwood | Linda Gross Theatre , Off-Broadway |  |
| 2025 | Twelfth Night | Olivia | William Shakespeare | Delacorte Theater , The Public Theatre |  |
| 2025 | La Fille du Régiment | Duchess of Krakenthorp | Gaetano Donizetti | Metropolitan Opera , Lincoln Center |  |

</details>

**GPT-4.1-mini**

Model response:

> Sandra Oh performed in the play "Death and the Maiden" at the Victory Gardens Theater in 1994.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states the year as 1994, but the reference answer and table indicate the correct year is 2014.

**Gemini-3-flash**

Model response:

> Sandra Oh performed in *Death and the Maiden* at the Victory Gardens Theater in **2004**.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states 2004, but the reference answer and table show the correct year is 2014.
