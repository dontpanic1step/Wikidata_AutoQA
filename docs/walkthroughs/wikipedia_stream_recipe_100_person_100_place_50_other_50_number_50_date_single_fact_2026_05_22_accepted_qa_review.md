# Accepted QA Review: `wikipedia_stream_recipe_100_person_100_place_50_other_50_number_50_date_single_fact_2026_05_22`

Source accepted JSONL: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_100_person_100_place_50_other_50_number_50_date_single_fact_2026_05_22_accepted.jsonl`

Accepted records: 30

Each section shows the accepted QA, answer type, page URL, the corresponding rendered source table, and the two second-stage small-model answers with judge result and judge reason.

## 1. Who are the authors of the view that organisms are cooperating entities at differing levels of biological organisation?

Answer type: `Person`

Reference answer: **Queller and Strassmann**

Page URL: [https://en.wikipedia.org/wiki/Organism](https://en.wikipedia.org/wiki/Organism)

Source table: table `1`, section `Organisms at differing levels of biological organisation`, caption `Queller and Strassmann's view of organisms as cooperating entities at differing levels of biological organisation [ 18 ]`

<details open><summary>Rendered source table for QA 1</summary>

| Level | Example | Composition | Co-operation |
| --- | --- | --- | --- |
| Virus | Tobacco mosaic virus | Nucleic acid , protein | No metabolism, so not living, not an organism, say many biologists; [ 7 ] but they evolve, their genes collaborating to manipulate the host [ 18 ] |
| Unicellular organism | Paramecium | One cell , with organelles e.g. cilia for specific functions | Inter-cellular (inter-organismal) signalling [ 22 ] |
| Swarming protistan | Dictyostelium (cellular slime mould) | Unicellular amoebae | Free-living unicellular amoebae for most of lifetime; swarm and aggregate to a multicellular slug, cells specialising to form a dead stalk and a fruiting body [ 18 ] |
| Multicellular organism | Mushroom -forming fungus | Cells, grouped into organs for specific functions (e.g. reproduction) | Cell specialisation, communication [ 22 ] |
| Permanent sexual partnership | Anglerfish | Male and female permanently fastened together | Male provides male gametes ; female provides all other functions [ 18 ] |
| Mutualism | Lichen | Organisms of different species | Fungus provides structure, absorbs water and minerals; alga photosynthesises [ 18 ] |
| Joined colony | Siphonophore | Zooids joined together | Organism specialisation; inter-organism signalling [ 8 ] |
| Superorganism | Ant colony | Individuals living together | Organism specialisation (many ants do not reproduce); inter-organism signalling [ 23 ] |

</details>

**GPT-4.1-mini**

Model response:

> The view that organisms are cooperating entities at differing levels of biological organization is prominently associated with authors like David Sloan Wilson and Elliott Sober. They have extensively discussed multilevel selection and cooperation in evolution. Additionally, Peter Godfrey-Smith and Samir Okasha have contributed to this perspective in philosophy of biology.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer names different authors (David Sloan Wilson, Elliott Sober, Peter Godfrey-Smith, Samir Okasha) than the reference answer (Queller and Strassmann). The reference requires the exact authors Queller and Strassmann, so this is incorrect.


**Gemini-3-flash**

Model response:

> The primary authors associated with the view of organisms as nested levels of cooperation (often termed **Multilevel Selection Theory** or **Major Evolutionary Transitions**) include:
>
> *   **John Maynard Smith and Eörs Szathmáry:** Authors of *The Major Transitions in Evolution* (1995), which details how independent replicators combined to form higher-level cooperative units (e.g., genes into chromosomes, cells into multicellular organisms).
> *   **Leo Buss:** Author of *The Evolution of Individuality* (1987), focusing on the transition from single cells to multicellular individuals.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Queller and Strassmann' as authors of the view; the prediction names different authors (John Maynard Smith, Eörs Szathmáry, Leo Buss) not mentioned in the source table, so it does not match the reference answer or valid aliases.


## 2. Who most recently won the British Dance Act award at the BRIT Awards before its hiatus ended in 2021?

Answer type: `Person`

Reference answer: **Charli XCX**

Page URL: [https://en.wikipedia.org/wiki/Electronic_dance_music](https://en.wikipedia.org/wiki/Electronic_dance_music)

Source table: table `1`, section `Industry awards`

<details open><summary>Rendered source table for QA 2</summary>

| Organization | Award(s) | Year(s) | Notes |
| --- | --- | --- | --- |
| BRIT Awards | British Dance Act | 1994–present (on hiatus between 2005 to 2021) | Most recently won (2025) by Charli XCX . [ 255 ] |
| Grammy Awards | Best Dance/Electronic Recording | 1998–present | Most recently won (2025) by Tame Impala for " End of Summer ". [ 256 ] |
| Grammy Awards | Best Dance/Electronic Music Album | 2005–present | Most recently won (2025) by FKA twigs for " EUSEXUA ". [ 257 ] |
| DJ Mag | Top 100 DJs poll | 1991–present | The British dance music magazine DJ Mag publishes a yearly listing of the top 100 DJs in the world; from 1991 to 1996 the Top 100 poll were ranked by the magazine's journalists; in 1997 the poll became a public vote. The current number one as of the 2025 list is David Guetta . [ 258 ] |
| DJ Awards | Best DJ Award | 1998–present | The only global DJ awards event that nominates and awards international DJ's in 11 categories held annually in Ibiza , Spain, winners selected by a public vote [ 259 ] and one of the most important. [ 260 ] |
| Winter Music Conference (WMC) | IDMA: International Dance Music Awards | 1998–present | [ 261 ] |
| Project X Magazine | Electronic Dance Music Awards | 1995 | Readers of Project X magazine voted for the winners of the first (and only) "Electronic Dance Music Awards". [ 262 ] In a ceremony organized by the magazine and Nervous Records , award statues were given to Winx , The Future Sound of London , Moby , Junior Vasquez , Danny Tenaglia , DJ Keoki , TRIBAL America Records and Moonshine Records . [ 262 ] |
| American Music Awards | Favorite Dance/Electronic Artist | 2012–present | Most recently won (2025) by Lady Gaga . [ 263 ] |
| World Music Awards | Favorite Electronic Dance Music Artist | 2006–present (on hiatus) | Most recently won (2014) by Calvin Harris . [ 264 ] |

</details>

**GPT-4.1-mini**

Model response:

> The most recent winner of the British Dance Act award at the BRIT Awards before its hiatus ended in 2021 was Rudimental in 2019.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is Charli XCX, but the prediction states Rudimental in 2019, which contradicts the reference.


**Gemini-3-flash**

Model response:

> **Jamiroquai** won the award in 2004, the final year it was presented before its 18-year hiatus.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is Charli XCX as the most recent winner before the hiatus ended in 2021; Jamiroquai won in 2004, which is not the most recent winner before the hiatus ended.


## 3. Who granted royal assent to the Great Western Railway Act in 1835?

Answer type: `Person`

Reference answer: **Parliament of the United Kingdom**

Page URL: [https://en.wikipedia.org/wiki/Great_Western_Railway](https://en.wikipedia.org/wiki/Great_Western_Railway)

Source table: table `2`, section `Formation`

<details open><summary>Rendered source table for QA 3</summary>

| Great Western Railway Act 1835 | Great Western Railway Act 1835 |
| --- | --- |
| Act of Parliament | Act of Parliament |
| Parliament of the United Kingdom | Parliament of the United Kingdom |
| Long title | An Act for making a Railway from Bristol to join the London and Birmingham Railway near London, to be called "The Great Western Railway," with Branches therefrom to the Towns of Bradford and Trowbridge in the County of Wilts. |
| Citation | 5 & 6 Will. 4 . c. cvii |
| Dates | Dates |
| Royal assent | 31 August 1835 |

</details>

**GPT-4.1-mini**

Model response:

> The Great Western Railway Act of 1835 received royal assent from King William IV.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Parliament of the United Kingdom', but the prediction states 'King William IV', which is a different entity and contradicts the reference.


**Gemini-3-flash**

Model response:

> **King William IV** granted royal assent to the Great Western Railway Act on August 31, 1835.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Parliament of the United Kingdom', but the prediction names 'King William IV', a specific person, which contradicts the reference answer that identifies the institution granting assent, not the monarch.


## 4. Who is the author referenced for the data on the "prefix conjugation" in Afroasiatic languages?

Answer type: `Person`

Reference answer: **Gragg**

Page URL: [https://en.wikipedia.org/wiki/Afroasiatic_languages](https://en.wikipedia.org/wiki/Afroasiatic_languages)

Source table: table `12`, section `"Prefix conjugation"`, caption `The "prefix conjugation" in Afroasiatic, following Gragg 2019`

<details open><summary>Rendered source table for QA 4</summary>

| Number | Person | Gender | Akkadian (Semitic) | Akkadian (Semitic) | Berber | Berber | Beja (Cushitic) | Beja (Cushitic) | Beja (Cushitic) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Number | Person | Gender | Preterite | Present | Aorist | Imperfective | "Old Past" | "Old Present" | "New Present" |
| Singular | 1 | 1 | a-prus | a-parras | ăknəf-ăʕ | əkănnăf-ăʕ | ʔ-i:-dbíl | ʔ-a-dbíl | ʔ-a-danbí:l |
| Singular | 2 | m | ta-prus | ta-parras | t-ăknəf-ət | t-əkănnăf-ət | t-i:-dbíl-a | t-i-dbíl-a | danbí:l-a |
| Singular | 2 | f | ta-prus-i: | ta-parras-i | t-ăknəf-ət | t-əkănnăf-ət | t-i:-dbíl-i | t-i-dbíl-i | danbí:l-i |
| Singular | 3 | m | i-prus | i-parras | y-ăknəf | y-əkănnăf | ʔ-i:-dbíl | ʔ-i-dbíl | danbí:l |
| Singular | 3 | f | ta-prus | ta-parras | t-ăknəf | t-əkănnăf | t-i:-dbíl | t-i-dbíl | danbí:l |
| Plural | 1 | 1 | ni-prus | ni-parras | n-ăknəf | n-əkănnăf | n-i:-dbíl | n-i-dbíl | n-e:-dbíl |
| Plural | 2 | m | ta-prus-a: | a-parras | t-ăknəf-ăm | t-əkănnăf-ăm | t-i:-dbíl-na | t-i-dbíl-na | t-e:-dbíl-na |
| Plural | 2 | f | ta-prus-a: | ta-parras | t-ăknəf-măt | t-əkănnăf-măt | t-i:-dbíl-na | t-i-dbíl-na | t-e:-dbíl-na |
| Plural | 3 | m | i-prus-u: | ta-parras-i: | ăknəf-ăn | əkănnăf-ăn | ʔ-i:-dbíl | ʔ-i-dbíl | ʔ-e:-dbíl-na |
| Plural | 3 | f | i-prus-a: | i-parras | ăknəf-năt | əkănnăf-năt | ʔ-i:-dbíl | ʔ-i-dbíl | ʔ-e:-dbíl-na |

</details>

**GPT-4.1-mini**

Model response:

> The author referenced for the data on the "prefix conjugation" in Afroasiatic languages is Hetzron.

Judge result: `INCORRECT`

Judge reason:

> The correct author referenced is Gragg, not Hetzron.


**Gemini-3-flash**

Model response:

> The author most commonly referenced for data and reconstruction of the "prefix conjugation" in Afroasiatic languages is **Otto Rössler**. His work, particularly his 1950 study *Verbum und Nomen im Semitischen und Hamitischen*, established the prefix conjugation as a shared ancestral feature of the phylum.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Gragg' as explicitly stated in the table caption and nearby text. The predicted answer 'Otto Rössler' is not mentioned in the source and contradicts the provided reference.


## 5. Who was inducted into the Indianapolis Colts Ring of Honor in 2011?

Answer type: `Person`

Reference answer: **Marvin Harrison**

Page URL: [https://en.wikipedia.org/wiki/Indianapolis_Colts](https://en.wikipedia.org/wiki/Indianapolis_Colts)

Source table: table `5`, section `Ring of Honor`, caption `Indianapolis Colts Ring of Honor`

<details open><summary>Rendered source table for QA 5</summary>

| No. | Name | Position | Years With Club | Inducted |
| --- | --- | --- | --- | --- |
| — | Robert Irsay | Owner | 1972–1997 | 1996 [ 200 ] |
| 80 | Bill Brooks | WR | 1986–1992 | 1998 [ 201 ] |
| 75 | Chris Hinton | OT, OG | 1983–1989 | 2001 [ 202 ] |
| — | Ted Marchibroda | Head Coach | 1975–1979 1992–1995 | 2002 [ 203 ] |
| 4 | Jim Harbaugh | QB | 1994–1997 | 2005 [ 204 ] |
| — | 12th Man | Fans | — | 2007 |
| — | Tony Dungy | Head Coach | 2002–2008 | 2010 |
| 88 | Marvin Harrison | WR | 1996–2008 | 2011 |
| 32 | Edgerrin James | RB | 1999–2005 | 2012 [ 205 ] |
| 29 | Eric Dickerson | RB | 1987–1991 | 2013 [ 206 ] |
| 28 | Marshall Faulk | RB | 1994–1998 | 2013 [ 206 ] |
| 6 | Jeff Saturday | C | 1999–2011 | 2015 [ 207 ] |
| — | Bill Polian | President/General Manager | 1998–2011 | 2017 [ 208 ] [ 209 ] |
| 18 | Peyton Manning | QB | 1998–2011 | 2017 [ 208 ] [ 209 ] |
| 87 | Reggie Wayne | WR | 2001–2014 | 2018 |
| 93 | Dwight Freeney | DE | 2002–2012 | 2019 [ 210 ] |
| 98 | Robert Mathis | DE | 2003–2016 | 2021 [ 211 ] |
| 78 | Tarik Glenn | OT | 1997–2006 | 2022 [ 212 ] |
| 44 | Dallas Clark | TE | 2003–2011 | 2024 [ 213 ] |
| — | Jim Irsay | General Manager/Owner | 1984–2025 | 2025 |

</details>

**GPT-4.1-mini**

Model response:

> In 2011, Peyton Manning was inducted into the Indianapolis Colts Ring of Honor.

Judge result: `INCORRECT`

Judge reason:

> The correct inductee in 2011 was Marvin Harrison, not Peyton Manning.


**Gemini-3-flash**

Model response:

> **Marshall Faulk** was inducted into the Indianapolis Colts Ring of Honor in 2011.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is Marvin Harrison, but the prediction states Marshall Faulk, which is incorrect.


## 6. Who is credited with the binomial name of the almond species Prunus amygdalus?

Answer type: `Person`

Reference answer: **Batsch**

Page URL: [https://en.wikipedia.org/wiki/Almond](https://en.wikipedia.org/wiki/Almond)

Source table: table `1`

<details open><summary>Rendered source table for QA 6</summary>

| Almond | Almond |
| --- | --- |
|  |  |
| Clockwise from top left: almonds with shell cracked open, shelled, unshelled, and blanched seed | Clockwise from top left: almonds with shell cracked open, shelled, unshelled, and blanched seed |
|  |  |
| Almond tree with ripening fruit | Almond tree with ripening fruit |
| Scientific classification | Scientific classification |
| Kingdom: | Plantae |
| Clade : | Tracheophytes |
| Clade : | Angiosperms |
| Clade : | Eudicots |
| Clade : | Rosids |
| Order: | Rosales |
| Family: | Rosaceae |
| Genus: | Prunus |
| Subgenus: | Prunus subg. Amygdalus |
| Species: | P. amygdalus |
| Binomial name | Binomial name |
| Prunus amygdalus Batsch , 1801 | Prunus amygdalus Batsch , 1801 |
| Synonyms [ 1 ] [ 2 ] | Synonyms [ 1 ] [ 2 ] |
| Replaced syn. Amygdalus communis L. , 1753 Homotypic Amygdalus amygdalus (Batsch) Frye & Rigg, 1912 nom. illeg. Druparia amygdalus (Batsch) Clairv., 1811 Prunus communis (L.) Arcang., 1882 nom. illeg. Heterotypic Amygdalus amara Duhamel, 1768 Amygdalus amygdalina Oken ex M.Roem., 1847 Amygdalus cochinchinensis Lour., 1790 Amygdalus communis var. fragilis Ser., 1825 Amygdalus communis var. macrocarpa Ser., 1825 Amygdalus decipiens Poit. & Turpin, 1830 Amygdalus dulcis Mill. , 1768 Amygdalus elata Salisb., 1796 Amygdalus korshinskyi var. bornmuelleri Browicz, 1974 Amygdalus sativa Mill., 1768 Amygdalus sinensis Steud., 1840 Amygdalus stocksiana Boiss., 1856 Persica Mill., 1754 Prunus cochinchinensis (Lour.) Koehne, 1915 Prunus dulcis (Mill.) D.A.Webb , 1967 nom. superfl. Prunus dulcis var. amara (Duhamel) Buchheim, 1972 Prunus dulcis var. fragilis (Ser.) Buchheim, 1972 Prunus dulcis var. spontanea (Korsh.) Buchheim, 1972 Prunus intermedia A.Sav., 1882 Prunus stocksiana (Boiss.) Brandis, 1906 Trichocarpus Neck., 1790 | Replaced syn. Amygdalus communis L. , 1753 Homotypic Amygdalus amygdalus (Batsch) Frye & Rigg, 1912 nom. illeg. Druparia amygdalus (Batsch) Clairv., 1811 Prunus communis (L.) Arcang., 1882 nom. illeg. Heterotypic Amygdalus amara Duhamel, 1768 Amygdalus amygdalina Oken ex M.Roem., 1847 Amygdalus cochinchinensis Lour., 1790 Amygdalus communis var. fragilis Ser., 1825 Amygdalus communis var. macrocarpa Ser., 1825 Amygdalus decipiens Poit. & Turpin, 1830 Amygdalus dulcis Mill. , 1768 Amygdalus elata Salisb., 1796 Amygdalus korshinskyi var. bornmuelleri Browicz, 1974 Amygdalus sativa Mill., 1768 Amygdalus sinensis Steud., 1840 Amygdalus stocksiana Boiss., 1856 Persica Mill., 1754 Prunus cochinchinensis (Lour.) Koehne, 1915 Prunus dulcis (Mill.) D.A.Webb , 1967 nom. superfl. Prunus dulcis var. amara (Duhamel) Buchheim, 1972 Prunus dulcis var. fragilis (Ser.) Buchheim, 1972 Prunus dulcis var. spontanea (Korsh.) Buchheim, 1972 Prunus intermedia A.Sav., 1882 Prunus stocksiana (Boiss.) Brandis, 1906 Trichocarpus Neck., 1790 |

</details>

**GPT-4.1-mini**

Model response:

> The binomial name Prunus amygdalus is credited to Carl Linnaeus.

Judge result: `INCORRECT`

Judge reason:

> The correct person credited with the binomial name Prunus amygdalus is Batsch, not Carl Linnaeus.


**Gemini-3-flash**

Model response:

> **Philipp Conrad Fabricius** is credited with the binomial name *Prunus amygdalus*.

Judge result: `INCORRECT`

Judge reason:

> The correct person credited with the binomial name of Prunus amygdalus is Batsch, not Philipp Conrad Fabricius.


## 7. Who was nominated for the Top New Artist award in 1987 according to the Awards and nominations table?

Answer type: `Person`

Reference answer: **Richard Marx**

Page URL: [https://en.wikipedia.org/wiki/Richard_Marx](https://en.wikipedia.org/wiki/Richard_Marx)

Source table: table `5`, section `Awards and nominations`

<details open><summary>Rendered source table for QA 7</summary>

| Year | Nominee / work | Award | Result |
| --- | --- | --- | --- |
| 1987 [ 56 ] | Himself | Top New Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Billboard 200 Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Hot 100 Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Hot 100 Artist – Male | Nominated |
| 1987 [ 56 ] | Richard Marx | Top Billboard 200 Album | Nominated |
| 1987 [ 56 ] | " Don't Mean Nothing " | Top Hot 100 Song | Nominated |
| 1988 | Himself | Top Artist | Nominated |
| 1988 | Himself | Top Male Artist | Nominated |
| 1988 | Himself | Top Billboard 200 Artist | Nominated |
| 1988 | Himself | Top Billboard 200 Artist – Male | Nominated |
| 1988 | Himself | Top Hot 100 Artist | Nominated |
| 1988 | Himself | Top Hot 100 Artist – Male | Nominated |
| 1988 | Himself | Top Adult Contemporary Artist | Nominated |
| 1988 | Himself | Top Adult Contemporary Artist – Male | Nominated |
| 1988 | Richard Marx | Top Billboard 200 Album | Nominated |
| 1994 | Himself | Top Adult Contemporary Artist | Nominated |
| 1994 | " Now and Forever " | Top Adult Contemporary Track | Nominated |

</details>

**GPT-4.1-mini**

Model response:

> According to the Awards and nominations table, the nominees for the Top New Artist award in 1987 were:
>
> - Tiffany  
> - Glass Tiger  
> - Nu Shooz  
> - Bruce Hornsby & the Range  
> - Billy Vera & the Beaters

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Richard Marx' (alias 'Himself'), but the prediction lists different nominees not matching the reference; partial or different lists are considered incorrect.


**Gemini-3-flash**

Model response:

> According to the Awards and nominations table for 1987, the nominees for **Top New Artist** were:
>
> *   **The Judds** (Winner)
> *   **Restless Heart**
> *   **Holly Dunn**
> *   **Dwight Yoakam**
> *   **T. Graham Brown**

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Richard Marx' (alias 'Himself') as the nominee for Top New Artist in 1987. The prediction lists different nominees (The Judds, Restless Heart, Holly Dunn, Dwight Yoakam, T. Graham Brown) which do not match the reference answer and are not aliases.


## 8. Which place is associated with the era spanning from 645 to 650 known as Taika?

Answer type: `Place`

Reference answer: **Nara**

Page URL: [https://en.wikipedia.org/wiki/Reiwa_era](https://en.wikipedia.org/wiki/Reiwa_era)

Source table: table `4`, section `Externals links`

<details open><summary>Rendered source table for QA 8</summary>

| Column 1 | Column 2 |
| --- | --- |
| 645–650 | Taika |
| 650–654 | Hakuchi |
| 686–686 | Shuchō |
| 701–704 | Taihō |
| 704–708 | Keiun |
| 708–715 | Wadō |
|  |  |
| Nara | Nara |
| 715–717 | Reiki |
| 717–724 | Yōrō |
| 724–729 | Jinki |
| 729–749 | Tenpyō |
| 749 | Tenpyō-kanpō |
| 749–757 | Tenpyō-shōhō |
| 757–765 | Tenpyō-hōji |
| 765–767 | Tenpyō-jingo |
| 767–770 | Jingo-keiun |
| 770–781 | Hōki |
| 781–782 | Ten'ō |
| 782–806 | Enryaku |

</details>

**GPT-4.1-mini**

Model response:

> The era spanning from 645 to 650 known as Taika is associated with Japan.

Judge result: `INCORRECT`

Judge reason:

> The prediction answers 'Japan' which is a country, not the specific place 'Nara' associated with the Taika era (645-650) as per the reference answer.


**Gemini-3-flash**

Model response:

> The Taika era is primarily associated with **Naniwa-no-nagara-no-toyosaki-no-miya** (the Naniwa Palace) in modern-day **Osaka**, Japan, which served as the capital during the Taika Reforms.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Nara', but the prediction gives a different place 'Naniwa-no-nagara-no-toyosaki-no-miya' in Osaka, which contradicts the reference answer.


## 9. In which location was the Interactive Achievement Award won by Jada Pinkett Smith for Outstanding Achievement in Character Performance – Female for the work Enter the Matrix awarded?

Answer type: `Place`

Reference answer: **United States**

Page URL: [https://en.wikipedia.org/wiki/Jada_Pinkett_Smith](https://en.wikipedia.org/wiki/Jada_Pinkett_Smith)

Source table: table `5`, section `Awards and nominations`

<details open><summary>Rendered source table for QA 9</summary>

| Year | Award | Category | Work | Result | Ref |
| --- | --- | --- | --- | --- | --- |
| 2001 | NAACP Image Award | Outstanding Supporting Actress in a Motion Picture | Ali | Nominated |  |
| 2003 | Teen Choice Awards | Choice Movie Actress – Drama/Action Adventure | The Matrix Reloaded | Nominated |  |
| 2003 | NAACP Image Awards | Outstanding Supporting Actress in a Motion Picture | The Matrix Revolutions | Nominated |  |
| 2004 | Interactive Achievement Awards | Outstanding Achievement in Character Performance – Female | Enter the Matrix | Won | [ 155 ] |
| 2006 | NAACP Image Awards | Outstanding Literary Work – Children's | "Girls Hold Up This World" | Won |  |
| 2010 | NAACP Image Awards | Outstanding Actress in a Drama Series | Hawthorne | Won | [ 156 ] |
| 2010 | Prism Awards | Performance in a Drama Episode | Hawthorne | Nominated |  |
| 2010 | Tony Awards | Best Musical | Fela! | Nominated | [ 157 ] |
| 2013 | Behind the Voice Actors Awards | Best Vocal Ensemble in a Feature Film | Madagascar 3: Europe's Most Wanted | Nominated |  |
| 2015 | NAACP Image Awards | Outstanding Supporting Actress in a Drama Series | Gotham | Nominated | [ 158 ] |
| 2015 | People's Choice Awards | Favorite Actress in a New TV Series | Gotham | Nominated | [ 159 ] [ 160 ] |
| 2019 | Daytime Emmy Awards | Outstanding Informative Talk Show | Red Table Talk | Nominated | [ 161 ] |
| 2019 | MTV Movie & TV Awards | MTV Trailblazer Award | Jada Pinkett Smith | Won | [ 162 ] |
| 2019 | NAACP Image Awards | Outstanding Host in a Talk, Reality, News/ Information or Variety (Series or Special) | Red Table Talk | Won | [ 163 ] |
| 2020 | NAACP Image Awards | Outstanding Host in a Talk, Reality, News/ Information or Variety (Series or Special) | Red Table Talk | Won | [ 164 ] |
| 2020 | Daytime Emmy Awards | Outstanding Informative Talk Show | Red Table Talk | Nominated | [ 165 ] |
| 2020 | Daytime Emmy Awards | Outstanding Informative Talk Show Host | Red Table Talk | Nominated | [ 165 ] |
| 2021 | NAACP Image Awards | Outstanding Host in a Talk, Reality, News/ Information or Variety (Series or Special) | Red Table Talk | Nominated | [ 166 ] |
| 2021 | Daytime Emmy Awards | Outstanding Informative Talk Show | Red Table Talk | Won | [ 167 ] |
| 2021 | Daytime Emmy Awards | Outstanding Informative Talk Show Host | Red Table Talk | Nominated | [ 168 ] |
| 2021 | Daytime Emmy Awards | Outstanding Informative Talk Show | Red Table Talk : The Estefans | Nominated | [ 168 ] |
| 2021 | Daytime Emmy Awards | Outstanding Daytime Non-fiction Special | Red Table Talk: Will Smith's Red Table Takeover: Resolving Conflict | Nominated | [ 168 ] |

</details>

**GPT-4.1-mini**

Model response:

> The Interactive Achievement Award won by Jada Pinkett Smith for Outstanding Achievement in Character Performance – Female for Enter the Matrix was awarded in Las Vegas, Nevada.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'United States', but the prediction specifies 'Las Vegas, Nevada', which is more specific and not confirmed by the source; the source only supports the country, not the city or state.


**Gemini-3-flash**

Model response:

> The award was presented at the **Palms Casino Resort** in **Las Vegas, Nevada**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'United States' as the location, but the prediction specifies a more specific location 'Palms Casino Resort in Las Vegas, Nevada' which is not provided or confirmed in the reference. The prediction adds details not supported by the reference, so it is considered incorrect.


## 10. In which geographic region is the white-tailed deer subspecies found according to the range map of subspecies?

Answer type: `Place`

Reference answer: **North America**

Page URL: [https://en.wikipedia.org/wiki/White-tailed_deer](https://en.wikipedia.org/wiki/White-tailed_deer)

Source table: table `2`, section `South America`, caption `Range map of subspecies`

<details open><summary>Rendered source table for QA 10</summary>

| Column 1 | Column 2 |
| --- | --- |
| North America | Central and South America |

</details>

**GPT-4.1-mini**

Model response:

> The white-tailed deer subspecies is found primarily in the eastern and central regions of North America according to the range map of subspecies.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'North America' as a whole; the prediction specifies only 'eastern and central regions of North America,' which is a partial and more specific subset, thus incomplete and not fully matching the reference.


**Gemini-3-flash**

Model response:

> White-tailed deer (*Odocoileus virginianus*) are found across a vast geographic region that spans from **southern Canada**, throughout most of the **continental United States**, and down through **Mexico and Central America** into **northern South America** (as far south as Peru and Brazil).

Judge result: `INCORRECT`

Judge reason:

> The prediction lists a broad range including southern Canada, the United States, Mexico, Central America, and northern South America, which is broader than the reference answer 'North America' and includes regions outside the specified range map subspecies region, thus it is overbroad and partially incorrect.


## 11. From which anatomical area of the heart do the inferior ECG leads record electrical activity?

Answer type: `Place`

Reference answer: **inferior surface**

Page URL: [https://en.wikipedia.org/wiki/Electrocardiography](https://en.wikipedia.org/wiki/Electrocardiography)

Source table: table `4`, section `Contiguity of leads`

<details open><summary>Rendered source table for QA 11</summary>

| Category | Leads | Activity |
| --- | --- | --- |
| Inferior leads | Leads II, III and aVF | Look at electrical activity from the vantage point of the inferior surface ( diaphragmatic surface of heart ) |
| Lateral leads | I, aVL, V 5 and V 6 | Look at the electrical activity from the vantage point of the lateral wall of left ventricle |
| Septal leads | V 1 and V 2 | Look at electrical activity from the vantage point of the septal surface of the heart ( interventricular septum ) |
| Anterior leads | V 3 and V 4 | Look at electrical activity from the vantage point of the anterior wall of the right and left ventricles ( Sternocostal surface of heart ) |

</details>

**GPT-4.1-mini**

Model response:

> The inferior ECG leads (leads II, III, and aVF) record electrical activity from the inferior wall of the heart, primarily supplied by the right coronary artery.

Judge result: `INCORRECT`

Judge reason:

> The prediction adds information about blood supply and specifies 'inferior wall' instead of the required 'inferior surface' or 'diaphragmatic surface of heart', which is not an exact match and adds unsupported detail.


**Gemini-3-flash**

Model response:

> The inferior ECG leads (II, III, and aVF) record electrical activity from the **inferior wall of the left ventricle**.

Judge result: `INCORRECT`

Judge reason:

> The prediction specifies 'inferior wall of the left ventricle' which is more specific and not equivalent to the reference answer 'inferior surface' or its alias 'diaphragmatic surface of heart'. The reference answer is broader and accepted; the prediction adds a contradiction by limiting to left ventricle only.


## 12. In which city was the film 'Stories to Tell' featuring Richard Marx as himself filmed?

Answer type: `Place`

Reference answer: **London**

Page URL: [https://en.wikipedia.org/wiki/Richard_Marx](https://en.wikipedia.org/wiki/Richard_Marx)

Source table: table `2`, section `Filmography`

<details open><summary>Rendered source table for QA 12</summary>

| Year | Film/Show | Role | Notes |
| --- | --- | --- | --- |
| 1980 | Coach of the Year | Himself | Credited as Richard Marks |
| 2008 | Ringo Starr & His All Starr Band Live 2006 | Himself |  |
| 2008 | Legends and Lyrics Vol 2 | Himself |  |
| 2010 | Tim and Eric Awesome Show, Great Job! | Himself | Episode: "Greene Machine" |
| 2011 | Stories to Tell | Himself | London, England |
| 2012 | A Night Out with Friends | Himself | Taped at Arcada Theatre in St. Charles, Illinois |
| 2014 | Back in the Day | Neighbor |  |
| 2017 | Life in Pieces | Buddy Daquiri | Episode: "Poison Fire Teats Universe" |
| 2017 | Drop the Mic | Himself | Episode: " Wayne Brady vs. Jake Owen / Kenny G vs. Richard Marx" |
| 2018 | The Bachelorette | Himself | Episode: 3 |
| 2021 | Family Guy | Himself | Episode: " Young Parent Trap " |
| 2021 | Full Frontal with Samantha Bee | Himself | Episode: "Full Frontal Wants to Take Your Guns" |
| 2022 | The Goldbergs | Himself | Episode: "The Wedding" |
| 2025– | The Voice Australia | Himself/coach | Season 14 |

</details>

**GPT-4.1-mini**

Model response:

> The film "Stories to Tell" featuring Richard Marx as himself was filmed in Chicago.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is London (or London, England), but the prediction states Chicago, which contradicts the reference.


**Gemini-3-flash**

Model response:

> The film *Stories to Tell* (2021) was filmed in **Los Angeles**, California.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is London (London, England), but the prediction states Los Angeles, California, which contradicts the reference.


## 13. Which operating system family does the Pixel Launcher use?

Answer type: `Place`

Reference answer: **Unix-like**

Page URL: [https://en.wikipedia.org/wiki/Google_Pixel](https://en.wikipedia.org/wiki/Google_Pixel)

Source table: table `4`, section `Pixel UI (Pixel Launcher)`

<details open><summary>Rendered source table for QA 13</summary>

| Pixel Launcher | Pixel Launcher |
| --- | --- |
| Developer | Google |
| OS family | Unix-like (modified Linux kernel ) |
| Working state | Current |
| Latest release | Android 16 / January 3, 2025 ; 16 months ago ( 2025-01-03 ) |
| Marketing target | Smartphones and tablet computers |
| Articles in the series | Articles in the series |
| Android version history | Android version history |

</details>

**GPT-4.1-mini**

Model response:

> The Pixel Launcher uses the Android operating system family.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Unix-like' or 'modified Linux kernel', but the prediction states 'Android operating system family', which is more specific and not an accepted alias for the OS family in this context.


**Gemini-3-flash**

Model response:

> The Pixel Launcher uses the **Android** operating system family.

Judge result: `INCORRECT`

Judge reason:

> The reference answer specifies 'Unix-like' or 'modified Linux kernel' as the OS family, while the prediction states 'Android', which is a specific OS based on Unix-like but not the OS family itself. The prediction is more specific and does not match the required OS family answer.


## 14. In which place did Charles XII of Sweden die?

Answer type: `Place`

Reference answer: **Fredrikshald, Denmark–Norway**

Page URL: [https://en.wikipedia.org/wiki/Charles_XII_of_Sweden](https://en.wikipedia.org/wiki/Charles_XII_of_Sweden)

Source table: table `1`

<details open><summary>Rendered source table for QA 14</summary>

| Charles XII | Charles XII |
| --- | --- |
| Portrait by Hyacinthe Rigaud , c. 1715 | Portrait by Hyacinthe Rigaud , c. 1715 |
| King of Sweden | King of Sweden |
| Reign | 5 April 1697 – 30 November 1718 O.S. [ 1 ] |
| Coronation | 14 December 1697 |
| Predecessor | Charles XI |
| Successor | Ulrika Eleonora |
| Regent | Hedwig Eleonora of Holstein-Gottorp (5 April – 15 December 1697) |
|  |  |
| Born | 17 June 1682 Tre Kronor , Stockholm , Sweden |
| Died | 30 November 1718 (1718-11-30) (aged 36) [ 1 ] Fredrikshald , Denmark–Norway |
| Burial | 26 February 1719 Riddarholmen Church , Stockholm |
| House | Palatinate-Zweibrücken |
| Father | Charles XI of Sweden |
| Mother | Ulrika Eleonora of Denmark |
| Religion | Lutheran |
| Signature |  |
|  |  |
| Military career | Military career |
| Allegiance | Sweden |
| Branch | Swedish Army |
| Conflicts | § Battles of Charles XII |
|  |  |

</details>

**GPT-4.1-mini**

Model response:

> Charles XII of Sweden died in Fredrikshald, Norway.

Judge result: `INCORRECT`

Judge reason:

> The reference answer specifies 'Fredrikshald, Denmark–Norway' while the prediction states only 'Fredrikshald, Norway', omitting the historical political entity 'Denmark–Norway', which is required for a fully correct answer.


**Gemini-3-flash**

Model response:

> Charles XII of Sweden died at the fortress of **Fredriksten** in **Halden**, Norway.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Fredrikshald, Denmark–Norway'. The prediction states 'fortress of Fredriksten in Halden, Norway', which is a different place name and does not match the required full place name including the historical country designation. Partial or related locations are not accepted as correct.


## 15. At which award ceremony did Ekta Kapoor win the Best Upcoming Drama Series award in 2015?

Answer type: `Place`

Reference answer: **Star Guild Awards**

Page URL: [https://en.wikipedia.org/wiki/Kumkum_Bhagya](https://en.wikipedia.org/wiki/Kumkum_Bhagya)

Source table: table `2`, section `Awards and nominations`

<details open><summary>Rendered source table for QA 15</summary>

| Year | Award | Category | Recipient | Result | Ref(s) |
| --- | --- | --- | --- | --- | --- |
| 2015 | Star Guild Awards | Best Upcoming Drama Series | Ekta Kapoor | Won | [ 39 ] |
| 2015 | Gold Awards | Best Actress in Negative Role (Critics) | Shikha Singh | Won | [ 40 ] |
| 2015 | Gold Awards | Best Actor in a Lead Role (Critics) | Shabbir Ahluwalia | Won | [ 40 ] |
| 2015 | Gold Awards | Best Actress in a Lead Role (Popular) | Sriti Jha | Nominated |  |
| 2015 | Gold Awards | Best Actor in a Lead Role (Popular) | Shabbir Ahluwalia | Nominated |  |
| 2015 | Gold Awards | Best TV Show of the Year (Fiction) | Ekta Kapoor | Nominated |  |
| 2015 | Indian Telly Awards | Best Onscreen Couple | Sriti Jha & Shabbir Ahluwalia | Won |  |
| 2015 | Indian Telly Awards | Best Actress in a Lead Role | Sriti Jha | Won |  |
| 2015 | BIG Star Entertainment Awards | BIG Star Most Entertaining Fiction Series | Ekta Kapoor | Won | [ 41 ] |
| 2015 | BIG Star Entertainment Awards | BIG Star Most Entertaining Television Actor - Female | Sriti Jha | Nominated | [ citation needed ] |
| 2015 | BIG Star Entertainment Awards | BIG Star Most Entertaining Television Actor - Male | Shabbir Ahluwalia | Nominated | [ citation needed ] |
| 2016 | 9th Boroplus Gold Awards | Boroplus Face of the Year | Sriti Jha | Won | [ 42 ] |
| 2016 | 9th Boroplus Gold Awards | Best Actor in a Lead Role (Popular) | Shabbir Ahluwalia | Won | [ 42 ] |
| 2016 | 9th Boroplus Gold Awards | Best TV Show of the Year (Fiction) | Ekta Kapoor | Won | [ 42 ] |
| 2016 | 9th Boroplus Gold Awards | Best Actress in Negative Role (Critics) | Shikha Singh | Nominated |  |
| 2016 | 9th Boroplus Gold Awards | Best Actor in Supporting Role (Popular) | Arjit Taneja | Nominated |  |
| 2016 | 9th Boroplus Gold Awards | Best Actress in a Lead Role (Popular) | Sriti Jha | Nominated |  |
| 2016 | Indian Television Academy Awards | Best Actor (Popular) | Shabbir Ahluwalia | Won |  |
| 2016 | Ghana Movie Awards | Best Foreign TV Series | Ekta Kapoor | Won |  |
| 2017 | Gold Awards | Best TV Show of the Year (Fiction) | Ekta Kapoor | Won | [ 43 ] [ 44 ] |
| 2017 | Gold Awards | Best Onscreen Jodi | Sriti Jha & Shabbir Ahluwalia | Nominated | [ 45 ] |
| 2017 | Gold Awards | Best Actress in Negative Role (Popular) | Shikha Singh | Nominated | [ 45 ] |
| 2017 | Gold Awards | Best Actor in Supporting Role (Popular) | Arjit Taneja | Nominated | [ 45 ] |
| 2017 | Gold Awards | Best Actress in a Lead Role (Popular) | Sriti Jha | Nominated | [ 45 ] |
| 2017 | Gold Awards | Best Actor in a Lead Role (Popular) | Shabbir Ahluwalia | Nominated | [ 45 ] |
| 2018 | 11th Keshking Gold Awards | Best Actress in Negative Role (Popular) | Shikha Singh | Won |  |
| 2018 | 11th Keshking Gold Awards | Best Actor in a Lead Role (Popular) | Shabbir Ahluwalia | Won |  |
| 2018 | 11th Keshking Gold Awards | Best Actress in a Lead Role (Popular) | Sriti Jha | Won |  |
| 2018 | 11th Keshking Gold Awards | Gold Award for Fittest actor of Television | Vin Rana | Won |  |
| 2018 | 11th Keshking Gold Awards | Best Television Show (Fiction) | Ekta Kapoor | Won |  |
| 2018 | 11th Keshking Gold Awards | Gold Producer's Honour (For Completing 1000 Episodes) | Ekta Kapoor | Won |  |
| 2018 | Telly Technical and Trade Awards | Best Editor (Fiction) | Vikas Sharma | Won | [ 46 ] |
| 2019 | Indian Telly Awards | Best Daily Series | Ekta Kapoor | Won | [ 47 ] |
| 2019 | Indian Telly Awards | Best Jodi | Shabbir Ahluwalia & Sriti Jha | Nominated | [ 48 ] |
| 2019 | Indian Telly Awards | Best Actor in Lead Role (Male) | Shabbir Ahluwalia | Nominated | [ 48 ] |
| 2019 | Indian Telly Awards | Best Actor in Lead Role (Female) | Sriti Jha | Nominated | [ 48 ] |
| 2019 | Indian Telly Awards | Best Actor in Supporting Role (Male) | Mishal Raheja | Nominated | [ 48 ] |
| 2019 | Indian Telly Awards | Best Actor in Negative Role (Male) | Shaad Randhawa | Nominated | [ 48 ] |
| 2019 | Indian Telly Awards | Best Actor in Negative Role (Female) | Leena

</details>

**GPT-4.1-mini**

Model response:

> Ekta Kapoor won the Best Upcoming Drama Series award in 2015 at the Indian Television Academy Awards.

Judge result: `INCORRECT`

Judge reason:

> The correct award ceremony is the Star Guild Awards, not the Indian Television Academy Awards.


**Gemini-3-flash**

Model response:

> Ekta Kapoor won the Best Upcoming Drama Series award for *Itna Karo Na Mujhe Pyaar* at the **14th Indian Telly Awards** in 2015.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Star Guild Awards', but the prediction states '14th Indian Telly Awards', which contradicts the reference.


## 16. In which place was the DVD art for the Complete Second Season of Batman Beyond designed?

Answer type: `Place`

Reference answer: **RDI**

Page URL: [https://en.wikipedia.org/wiki/Batman_Beyond](https://en.wikipedia.org/wiki/Batman_Beyond)

Source table: table `5`, section `Season DVDs`

<details open><summary>Rendered source table for QA 16</summary>

| DVD name | Release date | Episodes | Additional information |
| --- | --- | --- | --- |
| The Complete First Season | March 21, 2006 | 13 | Special features: creators' commentary on two key episodes; Inside Batman Beyond : Meet the Series' Creators ; Music of the Knight : Enjoy Score-Only Versions of Key Scenes. |
| The Complete Second Season | October 24, 2006 | 26 | Special features: creators' commentary on two key episodes; Inside Batman Beyond : The Panel – In-Depth Dialogue with the Show's Creators . DVD art designed by Jesse Stagg at RDI. |
| The Complete Third Season | March 20, 2007 | 13 | Special features: Inside Batman Beyond ; featurettes on four episodes by producers, directors and Will Friedle. DVD art designed by Jesse Stagg at RDI. |
| The Complete Series | November 23, 2010 | 52 | Special features: creator commentaries, season retrospectives, bonus 9th disc with 95 minutes of new special features, Secret Origin: The Story of DC Comics documentary and three all-new, all-revealing featurettes. |

</details>

**GPT-4.1-mini**

Model response:

> The DVD art for the Complete Second Season of Batman Beyond was designed at Warner Bros. Animation.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'RDI', but the prediction states 'Warner Bros. Animation', which contradicts the reference and is not a valid alias.


**Gemini-3-flash**

Model response:

> The DVD art for *Batman Beyond: The Complete Second Season* was designed in **Burbank, California**, by the Warner Bros. Home Entertainment creative team.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'RDI', but the prediction states 'Burbank, California' which is not supported by the source table and contradicts the given answer.


## 17. In which country was the Red Velvet limited edition Oreo flavor also available besides the United States?

Answer type: `Place`

Reference answer: **Indonesia**

Page URL: [https://en.wikipedia.org/wiki/Oreo](https://en.wikipedia.org/wiki/Oreo)

Source table: table `2`, section `Limited editions`, caption `List of limited edition Oreo flavors`

<details open><summary>Rendered source table for QA 17</summary>

| Name | Release | Description |
| --- | --- | --- |
| Birthday Cake | February 2012 – July 2012 | Created to celebrate Oreo's 100th birthday. [ 60 ] Made up of two chocolate Oreo cookie wafers with a birthday cake –flavored crème filling and sprinkles inside. On one of the two wafers, the traditional design was replaced with a birthday candle and the words "OREO 100". The birthday cake flavor has since been reintroduced, with a "double stuf" amount of crème filling, in both chocolate and golden Oreo varieties, except that the cookies no longer display the "OREO 100" print. [ 61 ] Now permanently available. |
| Lemon Twist | 2012–2013 | A golden Oreo with a lemon-flavored crème filling. |
| Watermelon | Summer 2013 | A golden Oreo with watermelon -flavored crème filling. Largely unsuccessful. [ 62 ] |
| Strawberries n' Cream | 2013 | A golden Oreo with a crème filling consisting of two halves, one strawberry-flavored and one similar to traditional Oreo crème. |
| Fruit Punch | 2014 | A golden Oreo with fruit punch-flavored crème. |
| Cookie Dough | March 2014 | A chocolate Oreo with cookie dough –flavored crème filling. [ 63 ] |
| Root Beer Float | July 2014 | A golden Oreo filled with root beer –flavored crème. [ 60 ] |
| Pumpkin Spice | September 2014 | A golden Oreo with pumpkin spice –flavored crème filling. |
| Red Velvet | February 2015 | First released in February 2015, and since reintroduced. Two red Oreo cookie wafers with cream cheese -flavored crème filling. Designed to emulate the popular red velvet cake . Also available in Indonesia. |
| Key Lime Pie | July 2015 | Two graham -flavored Oreo cookie wafers filled with key lime -flavored crème filling. |
| Cinnamon Bun | January 2016 | Two cinnamon-flavored cookie wafers filled with frosting -flavored crème filling. Designed to emulate a cinnamon bun . |
| S'mores | Summer 2016 | Two graham-flavored cookie wafers with a double layer of crème filling, one layer chocolate-flavored and one layer marshmallow -flavored. Inspired by the traditional campfire snack . |
| Fruity Crisp | June 2016 | A golden Oreo with a fruity and colorful rice crisp crème filling, similar to Fruity Pebbles . |
| Blueberry Pie | June 2016; 2017 | Two graham-flavored cookie wafers with a blueberry-flavored crème filling. |
| Swedish Fish | August 2016 | A chocolate Oreo with a red crème filling, flavored to resemble the red-colored Swedish Fish candy. Originally released exclusively through Kroger stores in the United States. |
| Peeps | February 2017; February 2018 | Originally released for Easter 2017. A golden Oreo filled with pink "marshmallow Peeps"–flavored crème. [ 64 ] Second version, released in February 2018, made with Peeps-embossed chocolate Oreo cookie wafers and purple "marshmallow Peeps"–flavored crème filling. |
| Waffle and Syrup | May 2017 | A golden Oreo with a ring of vanilla crème filling and a blob of maple syrup –flavored crème in the center. [ 60 ] Exclusive to Albertsons stores in the United States. [ 65 ] |
| Chocolate Hazelnut | January 2018 | A golden Oreo with a " Nutella -like"-flavored crème filling. [ 66 ] Released January 1, 2018. |
| Salted Caramel | 2018 | A golden Oreo with a salted caramel flavor crème filling. |
| Firework |  | Two classic Oreo cookie wafers with Pop Rocks candy within the crème. [ 67 ] Released around the Fourth of July in the United States. |
| Peppermint Bark | October 2018 | Two classic Oreo cookie wafers with "double stuf" amount of peppermint-flavored crème with red sugar crystals. |
| Easter Egg | January 2019 | A chocolate Oreo in an oval shape to resemble an egg, with purple-colored crème filling and four Easter-related designs on the wafer: a bunny in a basket, a baby chick wearing bunny ears, and spots and stripes to resemble the painting of an Easter egg. |
| Chocolate Marshmallow | January 2020 | Includes marshmallow pieces in the cookie wafers and chocolate marshmallow crème filling. [ 68 ] |
| Caramel Coconut | January 2020 |

</details>

**GPT-4.1-mini**

Model response:

> The Red Velvet limited edition Oreo flavor was also available in Canada besides the United States.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is Indonesia, but the prediction states Canada, which is incorrect.


**Gemini-3-flash**

Model response:

> The Red Velvet limited edition Oreo flavor was also available in **China**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is Indonesia, but the prediction states China, which contradicts the verified source.


## 18. Which time zone abbreviation is used for the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic?

Answer type: `Other`

Reference answer: **MAGT**

Page URL: [https://en.wikipedia.org/wiki/Sakha_Republic](https://en.wikipedia.org/wiki/Sakha_Republic)

Source table: table `2`, section `Time zones`

<details open><summary>Rendered source table for QA 18</summary>

| Map | Time zone | Abbr. | UTC offset | Areas |
| --- | --- | --- | --- | --- |
|  | Yakutsk Time | YAKT | UTC+09:00 | Most of the republic's territory |
|  | Vladivostok Time | VLAT | UTC+10:00 | Districts of Oymyakonsky , Ust-Yansky and Verkhoyansky |
|  | Magadan Time | MAGT | UTC+11:00 | Districts of Abyysky , Allaikhovsky , Momsky , Nizhnekolymsky , Srednekolymsky and Verkhnekolymsky |

</details>

**GPT-4.1-mini**

Model response:

> The districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic use the time zone abbreviation **VLAT** (Vladivostok Time), which is UTC+10.

Judge result: `INCORRECT`

Judge reason:

> The correct time zone abbreviation for the listed districts is MAGT (Magadan Time), not VLAT (Vladivostok Time). The prediction contradicts the reference answer.


**Gemini-3-flash**

Model response:

> The time zone abbreviation used for these districts is **SRET** (Srednekolymsk Time).

Judge result: `INCORRECT`

Judge reason:

> The correct time zone abbreviation for the listed districts is MAGT (Magadan Time), not SRET or Srednekolymsk Time, which is not a valid abbreviation in the source.


## 19. Which instrument did Max Brody play in the band Ministry?

Answer type: `Other`

Reference answer: **saxophone**

Page URL: [https://en.wikipedia.org/wiki/Ministry_(band)](https://en.wikipedia.org/wiki/Ministry_(band))

Source table: table `3`, section `Former members`

<details open><summary>Rendered source table for QA 19</summary>

| Image | Name | Years active | Instruments | Release contributions |
| --- | --- | --- | --- | --- |
|  | Stephen George | 1981–1985 | drums percussion | With Sympathy (1983) Twitch (1986) Early Trax (2004) |
|  | Robert Roberts | 1981–1983 | keyboards backing vocals | With Sympathy (1983) Early Trax (2004) |
|  | John Davis | 1981–1982 (died 2005) | keyboards backing vocals | With Sympathy (1983) Early Trax (2004) |
|  | Martin Sorenson | 1981–1982 | bass | With Sympathy (1983) Early Trax (2004) |
|  | Brad Hallen | 1983–1984 | bass | With Sympathy (1983) Early Trax (2004) |
|  | William "Bill" Rieflin | 1986–1994 (died 2020) | drums backing vocals keyboards guitar | The Land of Rape and Honey (1988) The Mind Is a Terrible Thing to Taste (1989) In Case You Didn't Feel Like Showing Up (1990) ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Greatest Fits (2001) Rantology (2005) |
|  | Mike Scaccia | 1989–1995 2003–2006 2011–2012 (died 2012) | guitars backing vocals bass | ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Greatest Fits (2001) Houses of the Molé (2004) Rantology (2005) Rio Grande Blood (2006) Relapse (2012) From Beer to Eternity (2013) |
|  | Louis Svitek | 1992–1999 2003 | guitars | ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Dark Side of the Spoon (1999) Animositisomina (2003) Rantology (2005) |
|  | Duane Buford | 1994–1999 | keyboards programming | Filth Pig (1996) Greatest Fits (2001) Sphinctour (2002) Rantology (2005) |
|  | Rey Washam | 1994–1999 2003 | drums | Filth Pig (1996) Dark Side of the Spoon (1999) Greatest Fits (2001) Sphinctour (2002) Animositisomina (2003) Houses of the Molé (2004) Rantology (2005) |
|  | Zlatko Hukic | 1996–1999 | guitars | Filth Pig (1996) Dark Side of the Spoon (1999) Greatest Fits (2001) Sphinctour (2002) Rantology (2005) |
|  | Max Brody | 1999–2004 | saxophone drums, percussion & programming (2001–2004) backing vocals | Greatest Fits (2001) Animositisomina (2003) Houses of the Molé (2004) Rantology (2005) |
|  | John Monte | 2004 | bass backing vocals | Houses of the Molé (2004) Rantology (2005) |
|  | Mark Baker | 2004–2005 | drums percussion backing vocals | Houses of the Molé (2004) Rantology (2005) Rio Grande Blood (2006) |
|  | Tommy Victor | 2005–2008 2011–2012 | guitars backing vocals bass | Rio Grande Blood (2006) The Last Sucker (2007) Relapse (2012) |
|  | Paul Raven | 2005–2007 (until his death) | bass keyboards backing vocals guitar programming drums | Rio Grande Blood (2006) The Last Sucker (2007) |
|  | Sin Quirin | 2007–2008 2012–2021 | guitars bass keyboards | The Last Sucker (2007) Relapse (2012) From Beer to Eternity (2013) AmeriKKKant (2018) |
|  | Tony Campos | 2008 2011–2015 2017–2019 | bass backing vocals | Relapse (2012) From Beer to Eternity (2013) AmeriKKKant (2018) |
|  | Aaron Rossi | 2008 2011-2016 (died 2025) | drums | From Beer to Eternity (2013) |
|  | Jason Christopher | 2016–2017 | bass backing vocals | AmeriKKKant (2018) |
|  | Derek Abrams | 2017–2019 | drums |  |
|  | DJ Swamp | 2017–2018 | turntables | AmeriKKKant (2018) |

</details>

**GPT-4.1-mini**

Model response:

> Max Brody played drums in the band Ministry.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'saxophone', but the prediction only mentions 'drums', which is incomplete and does not match the required answer exactly.


**Gemini-3-flash**

Model response:

> Max Brody played **drums** and **saxophone** in Ministry.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'saxophone' only; the prediction adds 'drums' which is additional and not part of the exact answer, making it incorrect under SimpleQA Verified-style rules.


## 20. Which song by Richard Marx won the Most Performed Songs award in 1990?

Answer type: `Other`

Reference answer: **Satisfied**

Page URL: [https://en.wikipedia.org/wiki/Richard_Marx](https://en.wikipedia.org/wiki/Richard_Marx)

Source table: table `3`, section `Awards and nominations`

<details open><summary>Rendered source table for QA 20</summary>

| Year | Nominee / work | Award | Result | Ref. |
| --- | --- | --- | --- | --- |
| 1986 | " What About Me? " | Most Performed Songs | Won | [ 50 ] |
| 1986 | " Crazy " | Most Performed Songs | Won | [ 50 ] |
| 1989 | " Endless Summer Nights " | Most Performed Songs | Won | [ 51 ] |
| 1989 | " Hold On to the Nights " | Most Performed Songs | Won | [ 51 ] |
| 1989 | " Should've Known Better " | Most Performed Songs | Won | [ 51 ] |
| 1990 | " Satisfied " | Most Performed Songs | Won | [ 51 ] |
| 1990 | " Right Here Waiting " | Most Performed Songs | Won | [ 51 ] |
| 1991 | " Right Here Waiting " | Most Performed Songs | Won | [ 52 ] |
| 1991 | " Angelia " | Most Performed Songs | Won | [ 52 ] |
| 1994 | " Take This Heart " | Most Performed Songs | Won | [ 53 ] |
| 1994 | " Now and Forever " | Most Performed Songs | Won | [ 53 ] |
| 1996 | "The Way She Loves Me" | Most Performed Songs | Won | [ 54 ] |
| 2002 | " This I Promise You " | Most Performed Songs | Won | [ 55 ] |
| 2005 | " Dance with My Father " | Most Performed Songs | Won | [ 55 ] |

</details>

**GPT-4.1-mini**

Model response:

> The song by Richard Marx that won the Most Performed Songs award in 1990 is "Right Here Waiting."

Judge result: `INCORRECT`

Judge reason:

> The correct answer is 'Satisfied' as per the reference; 'Right Here Waiting' also won in 1990 but the question asks for the song that won the award, and the reference answer is 'Satisfied'. Since the reference answer is a single song, the prediction must match exactly; partial or alternative answers are considered incorrect.


**Gemini-3-flash**

Model response:

> Richard Marx won the BMI Most Performed Songs award in 1990 for **"Right Here Waiting."**

Judge result: `INCORRECT`

Judge reason:

> The correct answer is 'Satisfied' as per the reference; 'Right Here Waiting' also won Most Performed Songs in 1990 but the question asks for the specific song that won the award in 1990, and the reference answer is 'Satisfied'. The prediction contradicts the reference answer by giving a different song.


## 21. What is the operating system family used by the Pixel Launcher?

Answer type: `Other`

Reference answer: **Unix-like**

Page URL: [https://en.wikipedia.org/wiki/Google_Pixel](https://en.wikipedia.org/wiki/Google_Pixel)

Source table: table `4`, section `Pixel UI (Pixel Launcher)`

<details open><summary>Rendered source table for QA 21</summary>

| Pixel Launcher | Pixel Launcher |
| --- | --- |
| Developer | Google |
| OS family | Unix-like (modified Linux kernel ) |
| Working state | Current |
| Latest release | Android 16 / January 3, 2025 ; 16 months ago ( 2025-01-03 ) |
| Marketing target | Smartphones and tablet computers |
| Articles in the series | Articles in the series |
| Android version history | Android version history |

</details>

**GPT-4.1-mini**

Model response:

> The Pixel Launcher is used on the Android operating system family.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Unix-like' or 'modified Linux kernel'. The prediction 'Android operating system family' is more specific and does not match the reference answer or its aliases, thus it is incorrect.


**Gemini-3-flash**

Model response:

> The Pixel Launcher uses the **Android** operating system family.

Judge result: `INCORRECT`

Judge reason:

> The reference answer specifies the OS family as 'Unix-like' or 'modified Linux kernel', but the prediction states 'Android', which is a specific OS based on Unix-like but not the OS family itself, thus it is incorrect for the question asking about the OS family.


## 22. How many documentaries featuring Busta Rhymes were released in the year 2006?

Answer type: `Number`

Reference answer: **5**

Page URL: [https://en.wikipedia.org/wiki/Busta_Rhymes](https://en.wikipedia.org/wiki/Busta_Rhymes)

Source table: table `5`, section `Documentary`

<details open><summary>Rendered source table for QA 22</summary>

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
| 2006 | Rap Sheet: Hip-Hop and the Cops [ 105 ] |
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

> In 2006, there was 1 documentary featuring Busta Rhymes released.

Judge result: `INCORRECT`

Judge reason:

> The prediction states 1 documentary in 2006, but the reference answer is 5 (acceptable range 4-6), so the prediction is incorrect.


**Gemini-3-flash**

Model response:

> There were **two** documentaries featuring Busta Rhymes released in 2006:
>
> 1.  **Dave Chappelle's Block Party**
> 2.  **The Hip Hop Project**

Judge result: `INCORRECT`

Judge reason:

> The reference answer states 5 documentaries released in 2006, but the prediction lists only 2 documentaries, which is a partial and incorrect count.


## 23. How many awards did Julia Roberts win for her roles related to Pretty Woman according to the accolades table?

Answer type: `Number`

Reference answer: **4**

Page URL: [https://en.wikipedia.org/wiki/Pretty_Woman](https://en.wikipedia.org/wiki/Pretty_Woman)

Source table: table `2`, section `Accolades`

<details open><summary>Rendered source table for QA 23</summary>

| Award | Category | Nominee(s) | Result |
| --- | --- | --- | --- |
| Academy Awards [ 64 ] | Best Actress | Julia Roberts | Nominated |
| BMI Film & TV Awards | Film Music Award | James Newton Howard | Won |
| BMI Film & TV Awards | Most Performed Song from a Film | " It Must Have Been Love " – Per Gessle | Won |
| British Academy Film Awards [ 65 ] | Best Film | Arnon Milchan , Steven Reuther and Garry Marshall | Nominated |
| British Academy Film Awards [ 65 ] | Best Actress in a Leading Role | Julia Roberts | Nominated |
| British Academy Film Awards [ 65 ] | Best Screenplay – Original | J. F. Lawton | Nominated |
| British Academy Film Awards [ 65 ] | Best Costume Design | Marilyn Vance | Nominated |
| César Awards [ 66 ] | Best Foreign Film | Garry Marshall | Nominated |
| David di Donatello Awards | Best Foreign Actress | Julia Roberts | Nominated |
| Golden Globe Awards [ 67 ] | Best Motion Picture – Musical or Comedy | Best Motion Picture – Musical or Comedy | Nominated |
| Golden Globe Awards [ 67 ] | Best Actress in a Motion Picture – Musical or Comedy | Julia Roberts | Won |
| Golden Globe Awards [ 67 ] | Best Actor in a Motion Picture – Musical or Comedy | Richard Gere | Nominated |
| Golden Globe Awards [ 67 ] | Best Supporting Actor – Motion Picture | Hector Elizondo | Nominated |
| Golden Screen Awards | Golden Screen Awards | Golden Screen Awards | Won |
| Jupiter Awards | Best International Actress | Julia Roberts | Won |
| Kids' Choice Awards [ 68 ] | Favorite Movie Actress | Julia Roberts | Won |
| People's Choice Awards [ 69 ] | Favorite Comedy Motion Picture | Favorite Comedy Motion Picture | Won |
| Writers Guild of America Awards [ 70 ] | Best Screenplay – Written Directly for the Screen | J. F. Lawton | Nominated |

</details>

**GPT-4.1-mini**

Model response:

> Julia Roberts won 3 awards for her role related to Pretty Woman according to the accolades table.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states 3 awards won, but the reference answer is 4 with an acceptable range of 3 to 5. However, the question asks for the number of awards won, and the prediction explicitly states 3, which is at the lower bound but still within the acceptable range. Given the acceptable range includes 3, the answer should be CORRECT.


**Gemini-3-flash**

Model response:

> According to the accolades table, Julia Roberts won **3** awards for her role in *Pretty Woman*:
>
> 1.  **Golden Globe Award** for Best Actress – Motion Picture Musical or Comedy
> 2.  **Kids' Choice Award** for Favorite Movie Actress
> 3.  **ShoWest Award** for Female Star of the Year

Judge result: `INCORRECT`

Judge reason:

> The prediction states Julia Roberts won 3 awards, but the reference answer is 4 with an acceptable range of 3 to 5. However, the prediction includes an award (ShoWest Award) not listed in the provided accolades table, and it omits the Jupiter Award which is in the table. The correct count from the table is 4 awards won by Julia Roberts, so the prediction is incomplete and thus INCORRECT.


## 24. How many football championships has Espérance Sportive de Tunis won?

Answer type: `Number`

Reference answer: **20**

Page URL: [https://en.wikipedia.org/wiki/Tunis](https://en.wikipedia.org/wiki/Tunis)

Source table: table `5`, section `Sport`

<details open><summary>Rendered source table for QA 24</summary>

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

> The predicted answer states 32 championships, which is outside the acceptable range of 19 to 21 and contradicts the reference answer of 20.


**Gemini-3-flash**

Model response:

> Espérance Sportive de Tunis has won **33** Tunisian Ligue Professionnelle 1 titles.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states 33 championships, which is outside the acceptable range of 19 to 21 given by the reference answer of 20.


## 25. How many years was Mike Scaccia active as a member of Ministry in total?

Answer type: `Number`

Reference answer: **18**

Page URL: [https://en.wikipedia.org/wiki/Ministry_(band)](https://en.wikipedia.org/wiki/Ministry_(band))

Source table: table `3`, section `Former members`

<details open><summary>Rendered source table for QA 25</summary>

| Image | Name | Years active | Instruments | Release contributions |
| --- | --- | --- | --- | --- |
|  | Stephen George | 1981–1985 | drums percussion | With Sympathy (1983) Twitch (1986) Early Trax (2004) |
|  | Robert Roberts | 1981–1983 | keyboards backing vocals | With Sympathy (1983) Early Trax (2004) |
|  | John Davis | 1981–1982 (died 2005) | keyboards backing vocals | With Sympathy (1983) Early Trax (2004) |
|  | Martin Sorenson | 1981–1982 | bass | With Sympathy (1983) Early Trax (2004) |
|  | Brad Hallen | 1983–1984 | bass | With Sympathy (1983) Early Trax (2004) |
|  | William "Bill" Rieflin | 1986–1994 (died 2020) | drums backing vocals keyboards guitar | The Land of Rape and Honey (1988) The Mind Is a Terrible Thing to Taste (1989) In Case You Didn't Feel Like Showing Up (1990) ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Greatest Fits (2001) Rantology (2005) |
|  | Mike Scaccia | 1989–1995 2003–2006 2011–2012 (died 2012) | guitars backing vocals bass | ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Greatest Fits (2001) Houses of the Molé (2004) Rantology (2005) Rio Grande Blood (2006) Relapse (2012) From Beer to Eternity (2013) |
|  | Louis Svitek | 1992–1999 2003 | guitars | ΚΕΦΑΛΗΞΘ (1992) Filth Pig (1996) Dark Side of the Spoon (1999) Animositisomina (2003) Rantology (2005) |
|  | Duane Buford | 1994–1999 | keyboards programming | Filth Pig (1996) Greatest Fits (2001) Sphinctour (2002) Rantology (2005) |
|  | Rey Washam | 1994–1999 2003 | drums | Filth Pig (1996) Dark Side of the Spoon (1999) Greatest Fits (2001) Sphinctour (2002) Animositisomina (2003) Houses of the Molé (2004) Rantology (2005) |
|  | Zlatko Hukic | 1996–1999 | guitars | Filth Pig (1996) Dark Side of the Spoon (1999) Greatest Fits (2001) Sphinctour (2002) Rantology (2005) |
|  | Max Brody | 1999–2004 | saxophone drums, percussion & programming (2001–2004) backing vocals | Greatest Fits (2001) Animositisomina (2003) Houses of the Molé (2004) Rantology (2005) |
|  | John Monte | 2004 | bass backing vocals | Houses of the Molé (2004) Rantology (2005) |
|  | Mark Baker | 2004–2005 | drums percussion backing vocals | Houses of the Molé (2004) Rantology (2005) Rio Grande Blood (2006) |
|  | Tommy Victor | 2005–2008 2011–2012 | guitars backing vocals bass | Rio Grande Blood (2006) The Last Sucker (2007) Relapse (2012) |
|  | Paul Raven | 2005–2007 (until his death) | bass keyboards backing vocals guitar programming drums | Rio Grande Blood (2006) The Last Sucker (2007) |
|  | Sin Quirin | 2007–2008 2012–2021 | guitars bass keyboards | The Last Sucker (2007) Relapse (2012) From Beer to Eternity (2013) AmeriKKKant (2018) |
|  | Tony Campos | 2008 2011–2015 2017–2019 | bass backing vocals | Relapse (2012) From Beer to Eternity (2013) AmeriKKKant (2018) |
|  | Aaron Rossi | 2008 2011-2016 (died 2025) | drums | From Beer to Eternity (2013) |
|  | Jason Christopher | 2016–2017 | bass backing vocals | AmeriKKKant (2018) |
|  | Derek Abrams | 2017–2019 | drums |  |
|  | DJ Swamp | 2017–2018 | turntables | AmeriKKKant (2018) |

</details>

**GPT-4.1-mini**

Model response:

> Mike Scaccia was active as a member of Ministry during two periods: from 1989 to 1996 and from 2003 until his death in 2012. 
>
> - First period: 1989 to 1996 → 7 years  
> - Second period: 2003 to 2012 → 9 years  
>
> In total, he was active in Ministry for 16 years.

Judge result: `INCORRECT`

Judge reason:

> The predicted total years active (16) does not match the reference answer range (17-19). The correct total from the source is 18 years (1989–1995: 7 years, 2003–2006: 4 years, 2011–2012: 2 years, totaling 13 years is incorrect; the reference states 18 years is correct). The prediction's periods and calculation are inaccurate.


**Gemini-3-flash**

Model response:

> Mike Scaccia was a member of Ministry for a total of **11 years** (1989–1995, 2003–2006, and 2011–2012).

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states 11 years, but the correct total is 18 years (acceptable range 17-19) based on the periods 1989–1995, 2003–2006, and 2011–2012 counted inclusively.


## 26. How many selectable terrain modes are included in the Ford Explorer's Terrain Management System?

Answer type: `Number`

Reference answer: **4**

Page URL: [https://en.wikipedia.org/wiki/Ford_Explorer](https://en.wikipedia.org/wiki/Ford_Explorer)

Source table: table `12`, section `Capability`

<details open><summary>Rendered source table for QA 26</summary>

| Terrain Management System [ 61 ] | Terrain Management System [ 61 ] |
| --- | --- |
| Default start selection: | Normal Driving mode |
| Subsequent modes are selected by turning the control dial clockwise . | Subsequent modes are selected by turning the control dial clockwise . |
| Second selection: | Mud & Ruts mode |
| Third selection: | Sand mode |
| Fourth selection: | Grass/ Gravel /Snow mode |

</details>

**GPT-4.1-mini**

Model response:

> The Ford Explorer's Terrain Management System includes six selectable terrain modes.

Judge result: `INCORRECT`

Judge reason:

> The reference answer states 4 selectable terrain modes (acceptable range 3 to 5), but the prediction states 6, which is outside the acceptable range.


**Gemini-3-flash**

Model response:

> The Ford Explorer’s Terrain Management System includes **seven** selectable drive modes.

Judge result: `INCORRECT`

Judge reason:

> The reference answer states there are 4 selectable terrain modes (acceptable range 3-5), but the prediction claims 7 modes, which is outside the acceptable range and contradicts the reference.


## 27. In what year was the binomial name Prunus amygdalus for the almond officially published?

Answer type: `Date`

Reference answer: **1801**

Page URL: [https://en.wikipedia.org/wiki/Almond](https://en.wikipedia.org/wiki/Almond)

Source table: table `1`

<details open><summary>Rendered source table for QA 27</summary>

| Almond | Almond |
| --- | --- |
|  |  |
| Clockwise from top left: almonds with shell cracked open, shelled, unshelled, and blanched seed | Clockwise from top left: almonds with shell cracked open, shelled, unshelled, and blanched seed |
|  |  |
| Almond tree with ripening fruit | Almond tree with ripening fruit |
| Scientific classification | Scientific classification |
| Kingdom: | Plantae |
| Clade : | Tracheophytes |
| Clade : | Angiosperms |
| Clade : | Eudicots |
| Clade : | Rosids |
| Order: | Rosales |
| Family: | Rosaceae |
| Genus: | Prunus |
| Subgenus: | Prunus subg. Amygdalus |
| Species: | P. amygdalus |
| Binomial name | Binomial name |
| Prunus amygdalus Batsch , 1801 | Prunus amygdalus Batsch , 1801 |
| Synonyms [ 1 ] [ 2 ] | Synonyms [ 1 ] [ 2 ] |
| Replaced syn. Amygdalus communis L. , 1753 Homotypic Amygdalus amygdalus (Batsch) Frye & Rigg, 1912 nom. illeg. Druparia amygdalus (Batsch) Clairv., 1811 Prunus communis (L.) Arcang., 1882 nom. illeg. Heterotypic Amygdalus amara Duhamel, 1768 Amygdalus amygdalina Oken ex M.Roem., 1847 Amygdalus cochinchinensis Lour., 1790 Amygdalus communis var. fragilis Ser., 1825 Amygdalus communis var. macrocarpa Ser., 1825 Amygdalus decipiens Poit. & Turpin, 1830 Amygdalus dulcis Mill. , 1768 Amygdalus elata Salisb., 1796 Amygdalus korshinskyi var. bornmuelleri Browicz, 1974 Amygdalus sativa Mill., 1768 Amygdalus sinensis Steud., 1840 Amygdalus stocksiana Boiss., 1856 Persica Mill., 1754 Prunus cochinchinensis (Lour.) Koehne, 1915 Prunus dulcis (Mill.) D.A.Webb , 1967 nom. superfl. Prunus dulcis var. amara (Duhamel) Buchheim, 1972 Prunus dulcis var. fragilis (Ser.) Buchheim, 1972 Prunus dulcis var. spontanea (Korsh.) Buchheim, 1972 Prunus intermedia A.Sav., 1882 Prunus stocksiana (Boiss.) Brandis, 1906 Trichocarpus Neck., 1790 | Replaced syn. Amygdalus communis L. , 1753 Homotypic Amygdalus amygdalus (Batsch) Frye & Rigg, 1912 nom. illeg. Druparia amygdalus (Batsch) Clairv., 1811 Prunus communis (L.) Arcang., 1882 nom. illeg. Heterotypic Amygdalus amara Duhamel, 1768 Amygdalus amygdalina Oken ex M.Roem., 1847 Amygdalus cochinchinensis Lour., 1790 Amygdalus communis var. fragilis Ser., 1825 Amygdalus communis var. macrocarpa Ser., 1825 Amygdalus decipiens Poit. & Turpin, 1830 Amygdalus dulcis Mill. , 1768 Amygdalus elata Salisb., 1796 Amygdalus korshinskyi var. bornmuelleri Browicz, 1974 Amygdalus sativa Mill., 1768 Amygdalus sinensis Steud., 1840 Amygdalus stocksiana Boiss., 1856 Persica Mill., 1754 Prunus cochinchinensis (Lour.) Koehne, 1915 Prunus dulcis (Mill.) D.A.Webb , 1967 nom. superfl. Prunus dulcis var. amara (Duhamel) Buchheim, 1972 Prunus dulcis var. fragilis (Ser.) Buchheim, 1972 Prunus dulcis var. spontanea (Korsh.) Buchheim, 1972 Prunus intermedia A.Sav., 1882 Prunus stocksiana (Boiss.) Brandis, 1906 Trichocarpus Neck., 1790 |

</details>

**GPT-4.1-mini**

Model response:

> The binomial name Prunus amygdalus for the almond was officially published in 1753.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 1801, but the prediction states 1753, which is incorrect.


**Gemini-3-flash**

Model response:

> The binomial name *Prunus amygdalus* was officially published in **1768** by the botanist Philip Miller in the eighth edition of *The Gardeners Dictionary*.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 1801, but the prediction states 1768, which contradicts the verified source.


## 28. In what year did Richard Marx receive a nomination for the Top New Artist award?

Answer type: `Date`

Reference answer: **1987**

Page URL: [https://en.wikipedia.org/wiki/Richard_Marx](https://en.wikipedia.org/wiki/Richard_Marx)

Source table: table `5`, section `Awards and nominations`

<details open><summary>Rendered source table for QA 28</summary>

| Year | Nominee / work | Award | Result |
| --- | --- | --- | --- |
| 1987 [ 56 ] | Himself | Top New Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Billboard 200 Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Hot 100 Artist | Nominated |
| 1987 [ 56 ] | Himself | Top Hot 100 Artist – Male | Nominated |
| 1987 [ 56 ] | Richard Marx | Top Billboard 200 Album | Nominated |
| 1987 [ 56 ] | " Don't Mean Nothing " | Top Hot 100 Song | Nominated |
| 1988 | Himself | Top Artist | Nominated |
| 1988 | Himself | Top Male Artist | Nominated |
| 1988 | Himself | Top Billboard 200 Artist | Nominated |
| 1988 | Himself | Top Billboard 200 Artist – Male | Nominated |
| 1988 | Himself | Top Hot 100 Artist | Nominated |
| 1988 | Himself | Top Hot 100 Artist – Male | Nominated |
| 1988 | Himself | Top Adult Contemporary Artist | Nominated |
| 1988 | Himself | Top Adult Contemporary Artist – Male | Nominated |
| 1988 | Richard Marx | Top Billboard 200 Album | Nominated |
| 1994 | Himself | Top Adult Contemporary Artist | Nominated |
| 1994 | " Now and Forever " | Top Adult Contemporary Track | Nominated |

</details>

**GPT-4.1-mini**

Model response:

> Richard Marx received a nomination for the Top New Artist award in 1988.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 1987, but the prediction states 1988, which is incorrect.


**Gemini-3-flash**

Model response:

> Richard Marx was nominated for the **Billboard Music Award** for Top New Artist in **1988**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 1987, but the prediction states 1988, which is outside the allowed range and contradicts the reference.


## 29. In the Somali language numbers table, what is the Somali Latin term for the number thirteen?

Answer type: `Date`

Reference answer: **saddex iyo toban**

Page URL: [https://en.wikipedia.org/wiki/Somali_language](https://en.wikipedia.org/wiki/Somali_language)

Source table: table `8`, section `Numbers`

<details open><summary>Rendered source table for QA 29</summary>

| English | Somali / Latin | Somali / Osmanya | Somali / # |
| --- | --- | --- | --- |
| Eleven | kow iyo toban | 𐒏𐒙𐒓 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒡 |
| Twelve | laba iyo toban | 𐒐𐒖𐒁𐒖 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒢 |
| Thirteen | saddex iyo toban | 𐒈𐒖𐒆𐒆𐒗𐒄 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒣 |
| Fourteen | afar iyo toban | 𐒖𐒍𐒖𐒇 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒤 |
| Fifteen | shan iyo toban | 𐒉𐒖𐒒 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒥 |
| Sixteen | lix iyo toban | 𐒐𐒘𐒄 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒦 |
| Seventeen | toddoba iyo toban | 𐒂𐒙𐒆𐒆𐒙𐒁𐒖 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒧 |
| Eighteen | sideed iyo toban | 𐒈𐒘𐒆𐒜𐒆 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒨 |
| Nineteen | sagaal iyo toban | 𐒈𐒖𐒌𐒛𐒐 𐒘𐒕𐒙 𐒂𐒙𐒁𐒖𐒒 | 𐒡𐒩 |
| Twenty | labaatan | 𐒐𐒖𐒁𐒛𐒂𐒖𐒒 | 𐒢𐒠 |

</details>

**GPT-4.1-mini**

Model response:

> The Somali Latin term for the number thirteen is "toban iyo saddex."

Judge result: `INCORRECT`

Judge reason:

> The predicted answer 'toban iyo saddex' reverses the order of the components compared to the reference 'saddex iyo toban', which is the correct Somali Latin term for thirteen.


**Gemini-3-flash**

Model response:

> The Somali Latin term for the number thirteen is **toban iyo saddex**.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer 'toban iyo saddex' reverses the order of the components compared to the reference answer 'saddex iyo toban', which is the correct Somali Latin term for thirteen.


## 30. In what year were the four basic animal mating systems categorized in sociobiology and behavioural ecology?

Answer type: `Date`

Reference answer: **160–161**

Page URL: [https://en.wikipedia.org/wiki/Animal_sexual_behaviour](https://en.wikipedia.org/wiki/Animal_sexual_behaviour)

Source table: table `1`, section `Mating systems`

<details open><summary>Rendered source table for QA 30</summary>

| The four basic mating systems [ 4 ] : 160–161 [ 5 ] | The four basic mating systems [ 4 ] : 160–161 [ 5 ] / Single female | The four basic mating systems [ 4 ] : 160–161 [ 5 ] / Multiple females |
| --- | --- | --- |
| Single male | Monogamy | Polygyny |
| Multiple males | Polyandry | Polygynandry |

</details>

**GPT-4.1-mini**

Model response:

> The four basic animal mating systems were categorized in sociobiology and behavioral ecology in 1976.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is a page range (160–161), not a year. The prediction gives a specific year (1976) which is not supported by the reference and thus is incorrect.


**Gemini-3-flash**

Model response:

> The four basic animal mating systems (monogamy, polygyny, polyandry, and promiscuity) were categorized in **1977** by Stephen T. Emlen and Lewis W. Oring in their landmark paper, "Ecology, Sexual Selection, and the Evolution of Mating Systems."

Judge result: `INCORRECT`

Judge reason:

> The reference answer is a page range (160–161), not a year. The prediction gives a specific year (1977) which is not supported by the provided reference and contradicts the expected answer type and content.
