# Accepted QA Review: `wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_23`

Source accepted JSONL: `D:\Study\AI\My-research\Wikidata_Framework\outputs\wikipedia_stream_recipe_40_each_answer_type_single_fact_2026_05_23_accepted.jsonl`

Accepted records: 14

Each section shows the accepted QA, answer type, page URL, the corresponding rendered source table, and the two second-stage small-model answers with judge result and judge reason.

`LLM selected provided table rank` is the 1-based rank within the post-filter, score-ranked tables that were included in the generation prompt, not the page's raw table index.

## 1. Who is the brightest star in the constellation that the Sun stays in for approximately 7 days according to the 1977 IAU boundaries?

Answer type: `Person`

Reference answer: **Antares**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=34411](https://en.wikipedia.org/w/index.php?pageid=34411)

Source table: table `3`, type `wikitable`, section `Constellations`

LLM selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 1</summary>

| Name | 1977 IAU boundaries (approximate) | Solar stay | Brightest star |
| --- | --- | --- | --- |
| Aries | 19 April – 13 May | 25 days | Hamal |
| Taurus | 14 May – 19 June | 37 days | Aldebaran |
| Gemini | 20 June – 20 July | 31 days | Pollux |
| Cancer | 21 July – 9 August | 20 days | Tarf |
| Leo | 10 August – 15 September | 37 days | Regulus |
| Virgo | 16 September – 30 October | 45 days | Spica |
| Libra | 31 October – 22 November | 23 days | Zubeneschamali |
| Scorpius | 23 November – 29 November | 7 days | Antares |
| Ophiuchus | 30 November – 17 December | 18 days | Rasalhague |
| Sagittarius | 18 December – 18 January | 32 days | Kaus Australis |
| Capricornus | 19 January – 15 February | 28 days | Deneb Algedi |
| Aquarius | 16 February – 11 March | 24 days | Sadalsuud |
| Pisces | 12 March – 18 April | 38 days | Alpherg |

</details>

**GPT-4.1-mini**

Model response:

> The Sun stays in the constellation **Libra** for approximately 7 days according to the 1977 IAU boundaries. The brightest star in Libra is **Zubeneschamali (Beta Librae)**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer identifies the constellation with approximately 7 days solar stay as Scorpius, whose brightest star is Antares. The prediction incorrectly states Libra and its brightest star Zubeneschamali, which has a solar stay of 23 days, not 7.

**Gemini-3-flash**

Model response:

> The constellation is **Ophiuchus**, and its brightest star is **Rasalhague** (Alpha Ophiuchi).

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Antares', the brightest star in Scorpius, which is the constellation where the Sun stays for approximately 7 days according to the 1977 IAU boundaries. The prediction incorrectly names Ophiuchus and its brightest star Rasalhague, which does not match the reference answer or the correct constellation for the 7-day solar stay.


## 2. Who proposed the view of organisms as cooperating entities at differing levels of biological organisation?

Answer type: `Person`

Reference answer: **Queller and Strassmann**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=19653842](https://en.wikipedia.org/w/index.php?pageid=19653842)

Source table: table `1`, type `wikitable`, section `Organisms at differing levels of biological organisation`, caption `Queller and Strassmann's view of organisms as cooperating entities at differing levels of biological organisation [ 18 ]`

LLM selected provided table rank: `3/3` (score `1.2`)

<details open><summary>Rendered source table for QA 2</summary>

| Level | Example | Composition | Co-operation |
| --- | --- | --- | --- |
| Virus | Tobacco mosaic virus | Nucleic acid , protein | No metabolism, so not living, not an organism, say many biologists; but they evolve, their genes collaborating to manipulate the host |
| Unicellular organism | Paramecium | One cell , with organelles e.g. cilia for specific functions | Inter-cellular (inter-organismal) signalling |
| Swarming protistan | Dictyostelium (cellular slime mould) | Unicellular amoebae | Free-living unicellular amoebae for most of lifetime; swarm and aggregate to a multicellular slug, cells specialising to form a dead stalk and a fruiting body |
| Multicellular organism | Mushroom -forming fungus | Cells, grouped into organs for specific functions (e.g. reproduction) | Cell specialisation, communication |
| Permanent sexual partnership | Anglerfish | Male and female permanently fastened together | Male provides male gametes ; female provides all other functions |
| Mutualism | Lichen | Organisms of different species | Fungus provides structure, absorbs water and minerals; alga photosynthesises |
| Joined colony | Siphonophore | Zooids joined together | Organism specialisation; inter-organism signalling |
| Superorganism | Ant colony | Individuals living together | Organism specialisation (many ants do not reproduce); inter-organism signalling |

</details>

**GPT-4.1-mini**

Model response:

> The view of organisms as cooperating entities at differing levels of biological organization was notably proposed by Ernst Mayr and further developed by biologists like Richard Dawkins and David Sloan Wilson, who emphasized multilevel selection theory. However, the concept is most closely associated with **David Sloan Wilson**, who extensively articulated the idea of cooperation and selection operating at multiple biological levels.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Queller and Strassmann'. The prediction names different biologists (Ernst Mayr, Richard Dawkins, David Sloan Wilson) and does not include Queller and Strassmann, so it does not match the reference answer or valid aliases.

**Gemini-3-flash**

Model response:

> **Leo Buss** proposed this view in his 1987 book, *The Evolution of Individuality*.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'Queller and Strassmann', but the prediction names 'Leo Buss', which is a different person and contradicts the reference.


## 3. In which film did Meat Loaf play the character named Roy Budnitz?

Answer type: `Place`

Reference answer: **Americathon**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=21026](https://en.wikipedia.org/w/index.php?pageid=21026)

Source table: table `2`, type `wikitable`, section `Film`

LLM selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 3</summary>

| Year | Title | Role | Notes | Ref. |
| --- | --- | --- | --- | --- |
| 1962 | State Fair | Boy In Stands | Uncredited |  |
| 1975 | The Rocky Horror Picture Show | Eddie | as Meatloaf |  |
| 1979 | Americathon | Roy Budnitz |  |  |
| 1979 | Scavenger Hunt | Scum |  |  |
| 1980 | Roadie | Travis W. Redfish |  |  |
| 1981 | Dead Ringer | Meat Loaf / Marvin |  |  |
| 1986 | Out of Bounds | Gil | as Meatloaf |  |
| 1987 | The Squeeze | Titus | as Meatloaf |  |
| 1991 | Motorama | Vern | as Meatloaf |  |
| 1992 | Wayne's World | "Tiny" | as Meatloaf |  |
| 1992 | The Gun in Betty Lou's Handbag | Lawrence | as Meatloaf |  |
| 1992 | Leap of Faith | Hoover | as Meatloaf |  |
| 1997 | Spice World | Dennis | as Meatloaf |  |
| 1998 | Gunshy | Lew Collins | as Meatloaf |  |
| 1998 | Black Dog | "Red" | as Meatloaf |  |
| 1998 | The Mighty | Iggy Lee | as Meatloaf |  |
| 1998 | Outside Ozona | Floyd Bibbs | as Meatloaf |  |
| 1999 | Crazy in Alabama | Sheriff John Doggett | as Meatloaf |  |
| 1999 | Fight Club | Robert "Bob" Paulsen | as Meat Loaf Aday |  |
| 1999 | The Diary of the Hurdy-Gurdy Man ( hu ) |  |  |  |
| 2001 | Face to Face | Driver |  |  |
| 2001 | Rustin | Coach Trellingsby |  |  |
| 2001 | Focus | Fred |  |  |
| 2001 | The 51st State | "The Lizard" |  |  |
| 2001 | Polish Spaghetti | Food Critic |  |  |
| 2002 | The Salton Sea | Bo |  |  |
| 2002 | Wishcraft | Detective "Sparky" Shaw |  |  |
| 2003 | Learning Curves | Timmons |  |  |
| 2004 | A Hole in One | Billy |  |  |
| 2005 | Extreme Dating | Marshall Jackson |  |  |
| 2005 | Chasing Ghosts | Richard Valbruno |  |  |
| 2005 | Crazylove | John |  |  |
| 2005 | BloodRayne | Leonid |  |  |
| 2006 | The Pleasure Drivers | Dale |  |  |
| 2006 | Tenacious D in The Pick of Destiny | Bud Black | Uncredited. Jack Black 's father, providing vocals on the film's opening song " Kickapoo " |  |
| 2007 | Urban Decay | Rick "Zero" |  |  |
| 2007 | History Rocks | Himself |  |  |
| 2008 | Meat Loaf: In Search of Paradise | Himself |  |  |
| 2010 | Burning Bright | Howie | Uncredited | [ citation needed ] |
| 2010 | Beautiful Boy | Motel Manager |  |  |
| 2010 | Polish Bar | Joe |  |  |
| 2011 | Absolute Killers | Dan |  |  |
| 2013 | The Moment | Sergeant Goodman |  |  |
| 2013 | All American Christmas Carol | Ross |  |  |
| 2014 | Stage Fright | Roger McCall |  |  |
| 2014 | Wishin' and Hopin' | Monsignor Muldoon |  |  |
| 2016 | Sausage Party | Meatloaf | Archive recording |  |

</details>

**GPT-4.1-mini**

Model response:

> Meat Loaf played the character named Roy Budnitz in the film **"Fight Club" (1999)**.

Judge result: `INCORRECT`

Judge reason:

> The correct film is 'Americathon' (1979), but the prediction incorrectly states 'Fight Club' (1999).

**Gemini-3-flash**

Model response:

> Meat Loaf played Roy Budnitz in the 1980 film **Roadie**.

Judge result: `INCORRECT`

Judge reason:

> The correct film is 'Americathon' (1979), but the prediction states 'Roadie' (1980), which is incorrect.


## 4. In which location was the TV movie featuring John Belushi as Ron Decline produced?

Answer type: `Place`

Reference answer: **The Rutles: All You Need Is Cash**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=16384](https://en.wikipedia.org/w/index.php?pageid=16384)

Source table: table `3`, type `wikitable`, section `Television`

LLM selected provided table rank: `1/3` (score `5.45`)

<details open><summary>Rendered source table for QA 4</summary>

| Year | Title | Role | Notes |
| --- | --- | --- | --- |
| 1975–1980 | Saturday Night Live | Various Roles | 79 episodes; also writer |
| 1976 | The Beach Boys: It's OK | Cop #2 | TV movie; also writer |
| 1978 | The Rutles: All You Need Is Cash | Ron Decline | TV movie |

</details>

**GPT-4.1-mini**

Model response:

> The TV movie featuring John Belushi as Ron Decline, titled **"The Last Detail" (1973)**, was primarily filmed in **New York City** and **Washington, D.C.**

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'The Rutles: All You Need Is Cash', but the prediction gives a different movie title and locations not supported by the source.

**Gemini-3-flash**

Model response:

> The TV movie, titled **The Rutles: All You Need Is Cash**, was primarily produced and filmed in **London, England**, with additional filming locations in **New York City**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 'The Rutles: All You Need Is Cash' (the title of the TV movie), but the prediction provides filming locations (London, England and New York City) which are not given or confirmed in the reference. The question asks for the location of production, but the reference answer is the title, not a place. Thus, the prediction contradicts the reference answer type and content.


## 5. At which awards ceremony did Tracy Chapman win the Best International Album award in 1989?

Answer type: `Place`

Reference answer: **Danish Music Awards**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=169833](https://en.wikipedia.org/w/index.php?pageid=169833)

Source table: table `3`, type `wikitable`, section `Other awards and nominations`

LLM selected provided table rank: `2/3` (score `4.8`)

<details open><summary>Rendered source table for QA 5</summary>

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

> The correct answer is 'Danish Music Awards', but the prediction states 'Brit Awards', which is incorrect.

**Gemini-3-flash**

Model response:

> Tracy Chapman won the Best International Album award at the **1989 BRIT Awards**.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is 'Danish Music Awards', but the prediction states '1989 BRIT Awards', which is incorrect according to the source table.


## 6. Which place is associated with the ICD-10 code L40.3 for a type of psoriasis?

Answer type: `Place`

Reference answer: **Pustulosis palmaris et plantaris**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=101965](https://en.wikipedia.org/w/index.php?pageid=101965)

Source table: table `2`, type `wikitable`, section `Morphological`

LLM selected provided table rank: `1/1` (score `4.2`)

<details open><summary>Rendered source table for QA 6</summary>

| Psoriasis Type | ICD-10 Code |
| --- | --- |
| Psoriasis Vulgaris | L40.0 |
| Generalized pustular psoriasis | L40.1 |
| Acrodermatitis continua | L40.2 |
| Pustulosis palmaris et plantaris | L40.3 |
| Guttate psoriasis | L40.4 |
| Psoriatic arthritis | L40.50 |
| Psoriatic spondylitis | L40.53 |
| Inverse psoriasis | L40.8 |

</details>

**GPT-4.1-mini**

Model response:

> The ICD-10 code L40.3 is associated with "Pustulosis palmaris et plantaris," which affects the palms of the hands and the soles of the feet.

Judge result: `INCORRECT`

Judge reason:

> The question asks for a place associated with the ICD-10 code L40.3, but the answer given is a medical condition (Pustulosis palmaris et plantaris), not a place. The answer does not match the required answer type 'Place'.

**Gemini-3-flash**

Model response:

> ICD-10 code L40.3 refers to **Pustulosis palmaris et plantaris**, which is associated with the **palms of the hands** and the **soles of the feet**.

Judge result: `INCORRECT`

Judge reason:

> The answer provides anatomical locations (palms of the hands and soles of the feet) rather than the required place name 'Pustulosis palmaris et plantaris' as per the reference answer.


## 7. Which association awarded The Blacklist for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014?

Answer type: `Other`

Reference answer: **Primetime Creative Arts Emmy Awards**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=38962787](https://en.wikipedia.org/w/index.php?pageid=38962787)

Source table: table `5`, type `wikitable`, section `Accolades`

LLM selected provided table rank: `1/1` (score `4.8`)

<details open><summary>Rendered source table for QA 7</summary>

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

> The Blacklist was awarded for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014 by the **Primetime Emmy Awards**.

Judge result: `INCORRECT`

Judge reason:

> The correct association is 'Primetime Creative Arts Emmy Awards', but the prediction states 'Primetime Emmy Awards', which is a broader and different category, thus not an exact match or valid alias.

**Gemini-3-flash**

Model response:

> The **Academy of Television Arts & Sciences** (the organization that presents the **Primetime Emmy Awards**) awarded *The Blacklist* for Outstanding Stunt Coordination for a Drama Series, Miniseries, or Movie in 2014.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer incorrectly names the 'Academy of Television Arts & Sciences' instead of the 'Primetime Creative Arts Emmy Awards' as the awarding association. The reference answer specifies 'Primetime Creative Arts Emmy Awards' which is the correct and specific association.


## 8. In which video game did Eddie Guerrero make his first appearance?

Answer type: `Other`

Reference answer: **WCW vs. the World**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=306724](https://en.wikipedia.org/w/index.php?pageid=306724)

Source table: table `3`, type `wikitable`, section `Video games`

LLM selected provided table rank: `1/3` (score `6.8`)

<details open><summary>Rendered source table for QA 8</summary>

| Year | Game | Notes |
| --- | --- | --- |
| 1997 | WCW vs. the World | First video game appearance |
| 1997 | WCW vs. nWo: World Tour |  |
| 1997 | Virtual Pro Wrestling 64 | Only released in Japan |
| 1998 | WCW Nitro |  |
| 1998 | Shin Nippon Pro Wrestling: Toukon Retsuden 3 | Only released in Japan |
| 1998 | WCW/nWo Revenge |  |
| 1999 | WCW/nWo Thunder | Unlockable character |
| 1999 | WCW Mayhem | Last WCW video game appearance |
| 2000 | WWF No Mercy | First WWF/E video game appearance |
| 2000 | WWF SmackDown! 2: Know Your Role |  |
| 2001 | WWF Betrayal |  |
| 2001 | WWF With Authority! | Online game |
| 2001 | WWF Road to WrestleMania |  |
| 2001 | WWF SmackDown! Just Bring It |  |
| 2002 | WWF Raw |  |
| 2002 | WWE Road to WrestleMania X8 |  |
| 2002 | WWE SmackDown! Shut Your Mouth |  |
| 2002 | Legends of Wrestling II |  |
| 2003 | WWE Crush Hour |  |
| 2003 | WWE WrestleMania XIX |  |
| 2003 | WWE Raw 2 |  |
| 2003 | WWE SmackDown! Here Comes the Pain |  |
| 2004 | Showdown: Legends of Wrestling |  |
| 2004 | WWE Day of Reckoning |  |
| 2004 | WWE Survivor Series | Cover athlete |
| 2004 | WWE SmackDown! vs. Raw |  |
| 2005 | WWE WrestleMania 21 |  |
| 2005 | WWE Aftershock | Cover athlete ( PAL version) |
| 2005 | WWE Day of Reckoning 2 |  |
| 2005 | WWE SmackDown! vs. Raw 2006 | Last video game to be released while Guerrero was alive Released posthumously in North America |
| 2006 | WWE SmackDown vs. Raw 2007 † | "Legend wrestler" |
| 2007 | WWE SmackDown vs. Raw 2008 † | PSP version only "Legend wrestler" |
| 2011 | WWE All-Stars † |  |
| 2011 | WWE '12 † | "Legend wrestler" |
| 2012 | WWE WrestleFest † |  |
| 2012 | WWE '13 † | Legend wrestler |
| 2013 | WWE 2K14 † | "Legend wrestler" |
| 2014 | WWE SuperCard † |  |
| 2016 | WWE 2K17 † | Unlockable wrestler through in-game currency |
| 2017 | WWE 2K18 † | Unlockable wrestler through in-game currency |
| 2018 | WWE 2K19 † | Unlockable wrestler through in-game currency |
| 2019 | WWE 2K20 † | Unlockable wrestler through in-game currency |
| 2020 | WWE 2K Battlegrounds † |  |
| 2022 | WWE 2K22 † |  |
| 2023 | WWE 2K23 † | Unlockable through in-game currency |
| 2024 | WWE 2K24 † | Unlockable through Showcase |
| 2025 | WWE 2K25 † | Unlockable through in-game currency |
| 2026 | WWE 2K26 † | Unlockable through in-game currency |

</details>

**GPT-4.1-mini**

Model response:

> Eddie Guerrero made his first video game appearance in **WCW/nWo Revenge** for the Nintendo 64.

Judge result: `INCORRECT`

Judge reason:

> The correct answer is 'WCW vs. the World' as the first video game appearance, but the prediction states 'WCW/nWo Revenge', which is incorrect.

**Gemini-3-flash**

Model response:

> Eddie Guerrero made his first video game appearance in **Virtual Pro Wrestling** (released in 1996 for the PlayStation in Japan), where he appeared under his **Black Tiger** persona.

Judge result: `INCORRECT`

Judge reason:

> The reference answer states 'WCW vs. the World' as the first video game appearance, but the prediction claims 'Virtual Pro Wrestling' in 1996, which contradicts the reference and is not listed as the first appearance in the source table.


## 9. Which authority is credited with naming both the large numbers googol and googolplex?

Answer type: `Other`

Reference answer: **Kasner and Newman, dictionaries**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=682403](https://en.wikipedia.org/w/index.php?pageid=682403)

Source table: table `3`, type `wikitable`, section `Googol family`

LLM selected provided table rank: `1/1` (score `2.0`)

<details open><summary>Rendered source table for QA 9</summary>

| Value | Name | Authority |
| --- | --- | --- |
| 10 100 | googol | Kasner and Newman, dictionaries (see above) |
| 10 googol = 10 10 100 | googolplex | Kasner and Newman, dictionaries (see above) |

</details>

**GPT-4.1-mini**

Model response:

> The authority credited with naming both the large numbers googol and googolplex is the American mathematician Edward Kasner.

Judge result: `INCORRECT`

Judge reason:

> The prediction only credits Edward Kasner, omitting Newman and dictionaries, thus it is incomplete and partially incorrect compared to the reference answer.

**Gemini-3-flash**

Model response:

> **Milton Sirotta**, the nine-year-old nephew of American mathematician Edward Kasner, is credited with naming both terms.

Judge result: `INCORRECT`

Judge reason:

> The reference answer credits 'Kasner and Newman, dictionaries' as the authority, while the prediction credits Milton Sirotta, the nephew of Kasner, which is a related but different entity and not the authority credited with naming the terms.


## 10. Which time zone abbreviation corresponds to the time zone used in the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic?

Answer type: `Other`

Reference answer: **MAGT**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=57905](https://en.wikipedia.org/w/index.php?pageid=57905)

Source table: table `2`, type `wikitable`, section `Time zones`

LLM selected provided table rank: `1/1` (score `5.45`)

<details open><summary>Rendered source table for QA 10</summary>

| Map | Time zone | Abbr. | UTC offset | Areas |
| --- | --- | --- | --- | --- |
|  | Yakutsk Time | YAKT | UTC+09:00 | Most of the republic's territory |
|  | Vladivostok Time | VLAT | UTC+10:00 | Districts of Oymyakonsky , Ust-Yansky and Verkhoyansky |
|  | Magadan Time | MAGT | UTC+11:00 | Districts of Abyysky , Allaikhovsky , Momsky , Nizhnekolymsky , Srednekolymsky and Verkhnekolymsky |

</details>

**GPT-4.1-mini**

Model response:

> The time zone abbreviation for the districts of Abyysky, Allaikhovsky, Momsky, Nizhnekolymsky, Srednekolymsky, and Verkhnekolymsky in the Sakha Republic is **VLAT** (Vladivostok Time), which is UTC+10.

Judge result: `INCORRECT`

Judge reason:

> The correct time zone abbreviation for the listed districts is MAGT (Magadan Time), not VLAT (Vladivostok Time).

**Gemini-3-flash**

Model response:

> The time zone abbreviation for those districts is **SRET** (Srednekolymsk Time).

Judge result: `INCORRECT`

Judge reason:

> The correct time zone abbreviation is MAGT (Magadan Time), not SRET. The prediction gives a wrong abbreviation and adds a non-existent alias 'Srednekolymsk Time'.


## 11. How many cycles of BEACOPP escalated regimen are tested in the German Hodgkin Study Group HD15 trial?

Answer type: `Number`

Reference answer: **8**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=23713759](https://en.wikipedia.org/w/index.php?pageid=23713759)

Source table: table `3`, type `wikitable`, section `Management`

LLM selected provided table rank: `1/1` (score `6.05`)

<details open><summary>Rendered source table for QA 11</summary>

| MOPP | ABVD | Stanford V | BEACOPP |
| --- | --- | --- | --- |
| The original treatment for Hodgkin lymphoma was MOPP . The abbreviation stands for the four drugs mustargen (also known as chlormethine), oncovin (also known as vincristine), prednisone and procarbazine (also known as Matulane). [ medical citation needed ] MOPP was the first combination chemotherapy that achieved a high success rate. [ medical citation needed ] It was developed at the US National Cancer Institute . [ medical citation needed ] Although no longer the most effective combination, MOPP is still used after relapse or where the person has certain allergies or lung or heart problems which prevents the use of another regimen. [ medical citation needed ] | The ABVD chemotherapy regimen is the standard treatment of Hodgkin lymphoma in the United States. [ medical citation needed ] The abbreviation stands for the four drugs adriamycin , bleomycin , vinblastine , and dacarbazine . [ medical citation needed ] Developed in Italy in the 1970s, the ABVD treatment typically takes between six and eight months, although longer treatments may be required. [ medical citation needed ] | The Stanford V regimen is typically only half as long as the ABVD but involves a more intensive chemotherapy schedule and incorporates radiation therapy. In a randomised controlled study in Italy, Stanford V was found to be inferior to ABVD; however, this study has been criticized due to its incorrect administration of radiotherapy, diverging from the original Stanford V protocol. | BEACOPP is a form of treatment for stages > II mainly used in Europe. The cure rate with the BEACOPP esc. regimen is approximately 10–15% higher than with standard ABVD in advanced stages. BEACOPP is more expensive because of the requirement for concurrent treatment with GCSF to increase production of white blood cells. The German Hodgkin Study Group tests 8 cycles (8x) BEACOPP esc vs. 6x BEACOPP esc vs. 8x BEACOPP-14 baseline (HD15-trial). |
| Chlormethine | Doxorubicin | Doxorubicin | Doxorubicin |
| Oncovin | Bleomycin | Bleomycin | Bleomycin |
| Prednisone | Vinblastine | Vinblastine , vincristine | Vincristine |
| Procarbazine | Dacarbazine | Chlormethine | Cyclophosphamide , procarbazine |
|  |  | Etoposide | Etoposide |
|  |  | Prednisone | Prednisone |

</details>

**GPT-4.1-mini**

Model response:

> The German Hodgkin Study Group HD15 trial tested 2 to 4 cycles of the BEACOPP escalated regimen.

Judge result: `INCORRECT`

Judge reason:

> The reference answer states 8 cycles (acceptable range 7-9), but the prediction states 2 to 4 cycles, which is outside the acceptable range and thus incorrect.

**Gemini-3-flash**

Model response:

> In the GHSG HD15 trial, patients were randomized to receive either **6 or 8 cycles** of escalated BEACOPP (compared against 8 cycles of BEACOPP-14). The trial concluded that **6 cycles** of escalated BEACOPP was the most effective and least toxic regimen.

Judge result: `INCORRECT`

Judge reason:

> The reference answer requires the number of cycles tested, which is 8 (acceptable range 7-9). The prediction mentions both 6 and 8 cycles were tested but emphasizes 6 cycles as most effective, which adds contradictory information and does not match the exact answer required. Partial list of cycles tested is given but not the full required answer as a single number.


## 12. How many football championships has Espérance Sportive de Tunis won?

Answer type: `Number`

Reference answer: **20**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=57659](https://en.wikipedia.org/w/index.php?pageid=57659)

Source table: table `5`, type `wikitable`, section `Sport`

LLM selected provided table rank: `1/1` (score `3.95`)

<details open><summary>Rendered source table for QA 12</summary>

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

> The predicted answer states 33 championships, which is outside the acceptable range of 19 to 21 given in the reference answer (20).


## 13. On what month, day, and year did Stanley B. Freeborn start his term as chancellor of the University of California, Davis?

Answer type: `Date`

Reference answer: **September 25, 1958**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=31924](https://en.wikipedia.org/w/index.php?pageid=31924)

Source table: table `9`, type `wikitable`, section `List of chancellors`

LLM selected provided table rank: `3/3` (score `4.35`)

<details open><summary>Rendered source table for QA 13</summary>

| No. | Portrait | Chancellor | Term start | Term end | Refs. |
| --- | --- | --- | --- | --- | --- |
| 1 |  | Stanley B. Freeborn | September 25, 1958 | June 30, 1959 |  |
| 2 |  | Emil M. Mrak | July 1, 1959 | June 30, 1969 |  |
| 3 |  | James Henry Meyer | July 1, 1969 | June 30, 1987 |  |
| 4 |  | Theodore L. Hullar | July 1, 1987 | February 29, 1994 |  |
| acting |  | Larry N. Vanderhoef [ c ] | March 1, 1994 | April 6, 1994 |  |
| 5 |  | Larry N. Vanderhoef [ c ] | April 6, 1994 | August 16, 2009 |  |
| 6 |  | Linda Katehi [ d ] | August 17, 2009 | August 9, 2016 |  |
| acting |  | Ralph Hexter [ e ] | April 27, 2016 | July 31, 2017 |  |
| 7 |  | Gary S. May | August 1, 2017 | present |  |

</details>

**GPT-4.1-mini**

Model response:

> Stanley B. Freeborn started his term as chancellor of the University of California, Davis on July 1, 1958.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer gives July 1, 1958, which contradicts the reference answer September 25, 1958.

**Gemini-3-flash**

Model response:

> Stanley B. Freeborn started his term as chancellor of the University of California, Davis, on **July 1, 1952**.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer 'July 1, 1952' contradicts the reference answer 'September 25, 1958' and is not a valid alias.


## 14. In what year did Sandra Oh perform the role of Paulina in the play Death and the Maiden at Victory Gardens Theater?

Answer type: `Date`

Reference answer: **2014**

Page URL: [https://en.wikipedia.org/w/index.php?pageid=363002](https://en.wikipedia.org/w/index.php?pageid=363002)

Source table: table `5`, type `wikitable`, section `Theatre`

LLM selected provided table rank: `1/2` (score `6.7`)

<details open><summary>Rendered source table for QA 14</summary>

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

> Sandra Oh performed the role of Paulina in the play Death and the Maiden at Victory Gardens Theater in 1994.

Judge result: `INCORRECT`

Judge reason:

> The predicted answer states the year as 1994, but the reference answer and table indicate the correct year is 2014.

**Gemini-3-flash**

Model response:

> Sandra Oh performed the role of Paulina in *Death and the Maiden* at Victory Gardens Theater in **2011**.

Judge result: `INCORRECT`

Judge reason:

> The reference answer is 2014, but the prediction states 2011, which is incorrect.
