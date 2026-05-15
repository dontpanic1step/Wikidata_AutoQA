# Naomi C Futhey Walkthrough

## Example

- Question: From which university did Naomi C Futhey receive a first degree?
- Answer: University of British Columbia
- Subject QID: `Q96429409`
- Answer QID: `Q391028`
- Domain: `person_first_degree_university`

## Route Validation

- Route validation status: `resolved_by_non_temporal_descriptor`
- Descriptor: `Naomi C Futhey`
- Required signature: `first degree`
- Canonical question: From which university did Naomi C Futhey receive a first degree?

## Rewrite

- Rewrite used: `True`
- Rewritten question: From which university did Naomi C Futhey earn her Doctor of Medicine degree?
- Surface validation result: `passed`
- Answer-blind search queries:
  - Naomi C Futhey Doctor of Medicine university
  - Naomi C Futhey medical degree institution
  - where did Naomi C Futhey receive her medical degree
  - Naomi C Futhey education background medical degree

## Search Filter

- Search-based verifier passed: `False`
- DuckDuckGo request URLs:
  - https://html.duckduckgo.com/html/?q=From+which+university+did+Naomi+C+Futhey+earn+her+Doctor+of+Medicine+degree%3F
  - https://html.duckduckgo.com/html/?q=Naomi+C+Futhey+Doctor+of+Medicine+university
  - https://html.duckduckgo.com/html/?q=Naomi+C+Futhey+medical+degree+institution
  - https://html.duckduckgo.com/html/?q=where+did+Naomi+C+Futhey+receive+her+medical+degree
  - https://html.duckduckgo.com/html/?q=Naomi+C+Futhey+education+background+medical+degree
- Query results:
  - Query `full_question`: From which university did Naomi C Futhey earn her Doctor of Medicine degree?
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250
      - Title: Naomi C Futhey - Wikidata
      - Snippet: instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471
      - Title: Catie Futhey - CWHHA
      - Snippet: Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9
      - Title: 2025 - Abstract 6 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5
      - Title: Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...
      - Snippet: Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.researchgate.net%2Fprofile%2FCatie%2DFuthey&rut=9d9a6af7c0343faaa2f1c67ffe491fa16cddb9aa307f4c4321b1d9202d6b3bbd
      - Title: Catie FUTHEY | University of British Columbia - ResearchGate
      - Snippet: Catie FUTHEY | Cited by 38 | of University of British Columbia - Vancouver, Vancouver (UBC) | Read 6 publications | Contact Catie FUTHEY
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=ea477d090b1b1634960a189779fac16b26ed695e01369e4db820d1e5ed1a0516
      - Title: Catie Futhey - The University of British Columbia | LinkedIn
      - Snippet: Catie Futhey Greater Vancouver Metropolitan Area 541 followers 500+ connections Catie can introduce you to 10+ people at The University of British Columbia
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: 17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.centreforbrainhealth.ca%2Fnews%2Ftrainee%2Dprofile%2Dcatie%2Dfuthey%2F&rut=f6bb3a40051b70a951a274aa22ef15fa945d5543040ffe2b9897e760f6c3c42d
      - Title: Trainee Profile: Catie Futhey - Centre for Brain Health
      - Snippet: Catie Futhey is an MD/PhD student in the Graduate Program in Neuroscience under the supervision of Drs. Veronica Hirsch-Reinshagen and Mark Cembrowski.
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmdprogram.med.ubc.ca%2Fmdphd%2Fstudents%2F&rut=f39e915028783c66c520ddfc19928bd3905b15ced93a331f366808ea4b0d0977
      - Title: Students - MD Undergrad Education, UBC Faculty of Medicine
      - Snippet: The UBC MD/PhD Program currently has an enrollment of 33 students. Our current student liaison is Erica Qureshi, and our current alternate student liaison is Catie Futhey. Curtis Leclerc is our student liaison in the Northern Medical Program. Prospective applicants are welcome to contact any of the students via email to obtain more information on the program.
      - Answer hit: `False`
  - Query `keyword_query_1`: Naomi C Futhey Doctor of Medicine university
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471
      - Title: Catie Futhey - CWHHA
      - Snippet: Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250
      - Title: Naomi C Futhey - Wikidata
      - Snippet: instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9
      - Title: 2025 - Abstract 6 | CANP-ACNP
      - Snippet: Presenter Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline in chronic brain disorders such as ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fca.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=a60a43bfe04088daefb467ba1718cce5871d5b5d9a6aefac548b9bf581469d88
      - Title: Catie Futhey - The University of British Columbia | LinkedIn
      - Snippet: MD/PhD candidate at UBC studying the molecular signatures of neurological diseases, with a particular interest in how cardiovascular and endocrine factors shape brain health. · Experience: The University of British Columbia · Education: The University of British Columbia · Location: Greater Vancouver Metropolitan Area · 500+ connections on LinkedIn. View Catie Futhey's profile on ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5
      - Title: Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...
      - Snippet: Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: 17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmuckrack.com%2Fnaomi%2Dc%2Dfuthey&rut=4ecd6c22332dbb59204cae87faf437f66dcdf7cf3b576540f019d7a8254751a6
      - Title: Naomi C. Futhey's Profile | The Journal of Immunology Journalist | Muck ...
      - Snippet: Find Naomi C. Futhey's articles, email address, contact information, Twitter and more
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fonc.akashi.hyogo.jp%2Fmedical%2Fdoctors%2Ffujii_m.html&rut=fb7f55cf5d87e9c152039b8ab40dff727e3d2173cf13901e3a89ff3bb50a09cf
      - Title: 冨士井 睦｜大西脳神経外科病院 - onc.akashi.hyogo.jp
      - Snippet: 脳神経外科医 冨士井 睦 ふじい むつみ Fujii Mutsumi 所属診療科 脳神経外科
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmaps.google.com%2Fmaps%2F%3Fentry%3Dwc&rut=4f8125778977431fa287c8dfc94644c72e8532c22b7b86b04344fef468cf2ddb
      - Title: Google Maps
      - Snippet: Find local businesses, view maps and get driving directions in Google Maps.
      - Answer hit: `False`
  - Query `keyword_query_2`: Naomi C Futhey medical degree institution
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304
      - Title: PDF NAOMI (Catie) Futhey
      - Snippet: Naomi (Catie) Futhey MD/PhD Candidate, University of British Columbia
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471
      - Title: Catie Futhey - CWHHA
      - Snippet: Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250
      - Title: Naomi C Futhey - Wikidata
      - Snippet: instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9
      - Title: 2025 - Abstract 6 | CANP-ACNP
      - Snippet: Presenter Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline in chronic brain disorders such as ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: 17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5
      - Title: Naomi C. Futhey (Canada)
      - Snippet: Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fnpiregistry.cms.hhs.gov%2Fregistry%2F&rut=622da1382f37819fd522219e0c09888ca7745de19845e06fbd91c03744723b45
      - Title: NPPES NPI Registry
      - Snippet: Search the National Provider Identifier (NPI) Registry to find information about healthcare providers and organizations.
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Fprofile%2Fcatie%2Dfuthey%2F&rut=803fb7ea2240b160b6c3994fda7ecaa8a8f5c11ddd7078e7d48a4bee4f306472
      - Title: Catie Futhey - Women's Health Research Cluster
      - Snippet: Catie is a medical student at the University of British Columbia. She also holds a Bachelor of Science degree in Neuroscience from the University of McGill.
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1
      - Title: 2024-Abstract 4 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.
      - Answer hit: `True`
  - Query `keyword_query_3`: where did Naomi C Futhey receive her medical degree
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304
      - Title: PDF NAOMI (Catie) Futhey
      - Snippet: Naomi (Catie) Futhey MD/PhD Candidate, University of British Columbia
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471
      - Title: Catie Futhey - CWHHA
      - Snippet: Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250
      - Title: Naomi C Futhey - Wikidata
      - Snippet: instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9
      - Title: 2025 - Abstract 6 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1
      - Title: 2024-Abstract 4 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Fprofile%2Fcatie%2Dfuthey%2F&rut=803fb7ea2240b160b6c3994fda7ecaa8a8f5c11ddd7078e7d48a4bee4f306472
      - Title: Catie Futhey - Women's Health Research Cluster
      - Snippet: Catie is a medical student at the University of British Columbia. She also holds a Bachelor of Science degree in Neuroscience from the University of McGill.
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: 17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.instagram.com%2Fp%2FCPXCmAdjvfl%2F&rut=45bc4629509ffaaac2db7b3ee0d5d04688820f2c628151950dbb6f64bea0587e
      - Title: WashU Figure Skating on Instagram: " Senior Spotlight Our third senior ...
      - Snippet: WashU Figure Skating on Instagram: "🎓Senior Spotlight🎓 Our third senior is Naomi (@naomigmichael), who received degrees in Microbiology and Psychology. She will be moving back to her hometown of Raleigh, North Carolina to work as a medical scribe during her gap year before applying to medical schools. Naomi has also been on the Club Figure Skating team since her freshman year, serving as ...
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5
      - Title: Naomi C. Futhey (Canada)
      - Snippet: Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fca.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=a60a43bfe04088daefb467ba1718cce5871d5b5d9a6aefac548b9bf581469d88
      - Title: Catie Futhey - The University of British Columbia | LinkedIn
      - Snippet: MD/PhD candidate at UBC studying the molecular signatures of neurological diseases, with a particular interest in how cardiovascular and endocrine factors shape brain health. · Experience: The University of British Columbia · Education: The University of British Columbia · Location: Greater Vancouver Metropolitan Area · 500+ connections on LinkedIn. View Catie Futhey's profile on ...
      - Answer hit: `True`
  - Query `keyword_query_4`: Naomi C Futhey education background medical degree
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304
      - Title: PDF NAOMI (Catie) Futhey
      - Snippet: Founded and lead an officially ratified Medical Undergraduate Society organization striving to bridge biomedical research and clinical education to address the women's health gap.
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471
      - Title: Catie Futhey - CWHHA
      - Snippet: Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features.
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250
      - Title: Naomi C Futhey - Wikidata
      - Snippet: instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1
      - Title: 2024-Abstract 4 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9
      - Title: 2025 - Abstract 6 | CANP-ACNP
      - Snippet: Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.centreforbrainhealth.ca%2Fnews%2F2023%2Dtrainee%2Dendowment%2Daward%2Dwinners%2Dannounced%2F&rut=81874afa6ef93193cfdd850b14be129fceefb1fd19a9a952fa59b115e0626562
      - Title: 2023 Trainee Endowment Award Winners Announced
      - Snippet: Naomi (Catie) Futhey, PhD student Under the supervision of Drs. Veronica Hirsch-Reinshagen and Mark Cembrowski, Naomi is investigating the neuropathology of cognitive impairment in chronic Schizophrenia and Alzheimer's Disease by studying the expression of neuronal and synaptic protein markers.
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257
      - Title: 17 Years Too Long: Advancing Women's Health Through Medical School ...
      - Snippet: 17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5
      - Title: Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...
      - Snippet: Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health
      - Answer hit: `True`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FNaomi_(wrestler)&rut=08104e4d7c007493bb02a48b5d4a30b53e95ed878567ff16b12962e2474fa962
      - Title: Naomi (wrestler) - Wikipedia
      - Snippet: Trinity LaShawn Fatu[6] (née McCray; born November 30, 1987) [7] is an American professional wrestler, dancer and actress. As of January 2024, she is signed to WWE, where she performs on the Raw brand under the ring name Naomi. In August 2009, McCray signed with WWE. She was assigned to its former developmental territory, Florida Championship Wrestling (FCW), where she was the inaugural FCW ...
      - Answer hit: `False`
    - Result URL: //duckduckgo.com/l/?uddg=https%3A%2F%2Fescholarship.mcgill.ca%2Fcatalog%3Ff%255Bfaculty_sim%255D%255B%255D%3DMedicine%2Band%2BHealth%2BSciences%26locale%3Den%26q%3DFuthey%252C%2BNaomi%2BC.%26search_field%3Dnested_ordered_creator_label_ssim&rut=5612f8b2fb65fdcdfb67054c32696f7de2b331ca94a4cf6968dc57320d5fe69b
      - Title: Index Catalog // eScholarship@McGill
      - Snippet: Filtering by:CreatorFuthey, Naomi C.Remove constraint Creator: Futhey, Naomi C.FacultyMedicine and Health SciencesRemove constraint Faculty: Medicine and Health Sciences
      - Answer hit: `False`

## Cheap Model Filter

- Cheap-model verifier passed: `True`
- Model answer: Naomi C. Futhey earned her Doctor of Medicine degree from **Howard University**.
- Triggered rule: `none`

## Panel Grading

- Threshold used: `1.0`
- Panel accuracy: `0.0`
- Candidate passed threshold gate: `True`
- Model replies:
  - `openai/gpt-5.4-mini`
    - Reply: Naomi C. Futhey earned her Doctor of Medicine degree from **the University of Minnesota**.
    - Grade: `INCORRECT`
    - Used LLM grader: `True`
  - `google/gemini-3-flash-preview`
    - Reply: Naomi C. Futhey earned her Doctor of Medicine (MD) degree from the **University of Oklahoma College of Medicine**.
    - Grade: `INCORRECT`
    - Used LLM grader: `True`
- Panel metrics:
  - `n`: `2`
  - `correct`: `0`
  - `incorrect`: `2`
  - `not_attempted`: `0`
  - `attempted`: `2`
  - `accuracy`: `0.0`
  - `incorrect_rate`: `1.0`
  - `not_attempted_rate`: `0.0`
  - `attempt_rate`: `1.0`
  - `accuracy_given_attempted`: `0.0`
  - `f1`: `0.0`
- Per-model metrics:
  - `google/gemini-3-flash-preview`
    - `n`: `1`
    - `correct`: `0`
    - `incorrect`: `1`
    - `not_attempted`: `0`
    - `attempted`: `1`
    - `accuracy`: `0.0`
    - `incorrect_rate`: `1.0`
    - `not_attempted_rate`: `0.0`
    - `attempt_rate`: `1.0`
    - `accuracy_given_attempted`: `0.0`
    - `f1`: `0.0`
  - `openai/gpt-5.4-mini`
    - `n`: `1`
    - `correct`: `0`
    - `incorrect`: `1`
    - `not_attempted`: `0`
    - `attempted`: `1`
    - `accuracy`: `0.0`
    - `incorrect_rate`: `1.0`
    - `not_attempted_rate`: `0.0`
    - `attempt_rate`: `1.0`
    - `accuracy_given_attempted`: `0.0`
    - `f1`: `0.0`

## Shared Validation

- Shared validation passed: `True`
- `stable_answer`: `True`
- `answer_in_evidence`: `True`
- `question_unambiguous`: `True`
- `rewrite_guard_passed`: `True`

## Snapshot

```json
{
  "rewrite_summary": {
    "rewrite_used": true,
    "rewritten_question": "From which university did Naomi C Futhey earn her Doctor of Medicine degree?",
    "search_queries": [
      "Naomi C Futhey Doctor of Medicine university",
      "Naomi C Futhey medical degree institution",
      "where did Naomi C Futhey receive her medical degree",
      "Naomi C Futhey education background medical degree"
    ],
    "llm_discard_reason": ""
  },
  "search_verification_features": {
    "top_k": 10,
    "queries": [
      {
        "query_name": "full_question",
        "query_category": "full_question",
        "query": "From which university did Naomi C Futhey earn her Doctor of Medicine degree?",
        "result_count": 10,
        "title_hits": 2,
        "snippet_hits": 8,
        "answer_hit_results": 8,
        "exact_question_hit": false,
        "results": [
          {
            "title": "Naomi C Futhey - Wikidata",
            "snippet": "instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - CWHHA",
            "snippet": "Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471",
            "answer_hit": true
          },
          {
            "title": "2025 - Abstract 6 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9",
            "answer_hit": true
          },
          {
            "title": "Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...",
            "snippet": "Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5",
            "answer_hit": true
          },
          {
            "title": "Catie FUTHEY | University of British Columbia - ResearchGate",
            "snippet": "Catie FUTHEY | Cited by 38 | of University of British Columbia - Vancouver, Vancouver (UBC) | Read 6 publications | Contact Catie FUTHEY",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.researchgate.net%2Fprofile%2FCatie%2DFuthey&rut=9d9a6af7c0343faaa2f1c67ffe491fa16cddb9aa307f4c4321b1d9202d6b3bbd",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - The University of British Columbia | LinkedIn",
            "snippet": "Catie Futhey Greater Vancouver Metropolitan Area 541 followers 500+ connections Catie can introduce you to 10+ people at The University of British Columbia",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=ea477d090b1b1634960a189779fac16b26ed695e01369e4db820d1e5ed1a0516",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257",
            "answer_hit": true
          },
          {
            "title": "Trainee Profile: Catie Futhey - Centre for Brain Health",
            "snippet": "Catie Futhey is an MD/PhD student in the Graduate Program in Neuroscience under the supervision of Drs. Veronica Hirsch-Reinshagen and Mark Cembrowski.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.centreforbrainhealth.ca%2Fnews%2Ftrainee%2Dprofile%2Dcatie%2Dfuthey%2F&rut=f6bb3a40051b70a951a274aa22ef15fa945d5543040ffe2b9897e760f6c3c42d",
            "answer_hit": false
          },
          {
            "title": "Students - MD Undergrad Education, UBC Faculty of Medicine",
            "snippet": "The UBC MD/PhD Program currently has an enrollment of 33 students. Our current student liaison is Erica Qureshi, and our current alternate student liaison is Catie Futhey. Curtis Leclerc is our student liaison in the Northern Medical Program. Prospective applicants are welcome to contact any of the students via email to obtain more information on the program.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmdprogram.med.ubc.ca%2Fmdphd%2Fstudents%2F&rut=f39e915028783c66c520ddfc19928bd3905b15ced93a331f366808ea4b0d0977",
            "answer_hit": false
          }
        ]
      },
      {
        "query_name": "keyword_query_1",
        "query_category": "keyword_queries",
        "query": "Naomi C Futhey Doctor of Medicine university",
        "result_count": 10,
        "title_hits": 1,
        "snippet_hits": 7,
        "answer_hit_results": 7,
        "exact_question_hit": false,
        "results": [
          {
            "title": "Catie Futhey - CWHHA",
            "snippet": "Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471",
            "answer_hit": true
          },
          {
            "title": "Naomi C Futhey - Wikidata",
            "snippet": "instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250",
            "answer_hit": true
          },
          {
            "title": "2025 - Abstract 6 | CANP-ACNP",
            "snippet": "Presenter Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline in chronic brain disorders such as ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - The University of British Columbia | LinkedIn",
            "snippet": "MD/PhD candidate at UBC studying the molecular signatures of neurological diseases, with a particular interest in how cardiovascular and endocrine factors shape brain health. · Experience: The University of British Columbia · Education: The University of British Columbia · Location: Greater Vancouver Metropolitan Area · 500+ connections on LinkedIn. View Catie Futhey's profile on ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fca.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=a60a43bfe04088daefb467ba1718cce5871d5b5d9a6aefac548b9bf581469d88",
            "answer_hit": true
          },
          {
            "title": "Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...",
            "snippet": "Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257",
            "answer_hit": true
          },
          {
            "title": "Naomi C. Futhey's Profile | The Journal of Immunology Journalist | Muck ...",
            "snippet": "Find Naomi C. Futhey's articles, email address, contact information, Twitter and more",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmuckrack.com%2Fnaomi%2Dc%2Dfuthey&rut=4ecd6c22332dbb59204cae87faf437f66dcdf7cf3b576540f019d7a8254751a6",
            "answer_hit": false
          },
          {
            "title": "冨士井 睦｜大西脳神経外科病院 - onc.akashi.hyogo.jp",
            "snippet": "脳神経外科医 冨士井 睦 ふじい むつみ Fujii Mutsumi 所属診療科 脳神経外科",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fonc.akashi.hyogo.jp%2Fmedical%2Fdoctors%2Ffujii_m.html&rut=fb7f55cf5d87e9c152039b8ab40dff727e3d2173cf13901e3a89ff3bb50a09cf",
            "answer_hit": false
          },
          {
            "title": "Google Maps",
            "snippet": "Find local businesses, view maps and get driving directions in Google Maps.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmaps.google.com%2Fmaps%2F%3Fentry%3Dwc&rut=4f8125778977431fa287c8dfc94644c72e8532c22b7b86b04344fef468cf2ddb",
            "answer_hit": false
          }
        ]
      },
      {
        "query_name": "keyword_query_2",
        "query_category": "keyword_queries",
        "query": "Naomi C Futhey medical degree institution",
        "result_count": 10,
        "title_hits": 0,
        "snippet_hits": 9,
        "answer_hit_results": 9,
        "exact_question_hit": false,
        "results": [
          {
            "title": "PDF NAOMI (Catie) Futhey",
            "snippet": "Naomi (Catie) Futhey MD/PhD Candidate, University of British Columbia",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - CWHHA",
            "snippet": "Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471",
            "answer_hit": true
          },
          {
            "title": "Naomi C Futhey - Wikidata",
            "snippet": "instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250",
            "answer_hit": true
          },
          {
            "title": "2025 - Abstract 6 | CANP-ACNP",
            "snippet": "Presenter Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline in chronic brain disorders such as ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in Neuroscience | Editors: Romina Garcia de leon, Janielle Richards (Blog Coordinators) | Expert Reviewer: Dr. Liisa Galea Published: September 20, 2024 Women face disproportionate barriers to healthcare, including longer time to diagnosis and differences in disease presentation ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Flearn%2Fwomens%2Dhealth%2Dblog%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2F&rut=38a43d728faee437f8099e2318859271d295dfbbf3f23a22f5873beae154ad75",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257",
            "answer_hit": true
          },
          {
            "title": "Naomi C. Futhey (Canada)",
            "snippet": "Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5",
            "answer_hit": true
          },
          {
            "title": "NPPES NPI Registry",
            "snippet": "Search the National Provider Identifier (NPI) Registry to find information about healthcare providers and organizations.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fnpiregistry.cms.hhs.gov%2Fregistry%2F&rut=622da1382f37819fd522219e0c09888ca7745de19845e06fbd91c03744723b45",
            "answer_hit": false
          },
          {
            "title": "Catie Futhey - Women's Health Research Cluster",
            "snippet": "Catie is a medical student at the University of British Columbia. She also holds a Bachelor of Science degree in Neuroscience from the University of McGill.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Fprofile%2Fcatie%2Dfuthey%2F&rut=803fb7ea2240b160b6c3994fda7ecaa8a8f5c11ddd7078e7d48a4bee4f306472",
            "answer_hit": true
          },
          {
            "title": "2024-Abstract 4 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1",
            "answer_hit": true
          }
        ]
      },
      {
        "query_name": "keyword_query_3",
        "query_category": "keyword_queries",
        "query": "where did Naomi C Futhey receive her medical degree",
        "result_count": 10,
        "title_hits": 1,
        "snippet_hits": 9,
        "answer_hit_results": 9,
        "exact_question_hit": false,
        "results": [
          {
            "title": "PDF NAOMI (Catie) Futhey",
            "snippet": "Naomi (Catie) Futhey MD/PhD Candidate, University of British Columbia",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - CWHHA",
            "snippet": "Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features. Her passion for understanding sex differences in health and disease was sparked during her undergraduate research at McGill University, where she investigated the roles of ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471",
            "answer_hit": true
          },
          {
            "title": "Naomi C Futhey - Wikidata",
            "snippet": "instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250",
            "answer_hit": true
          },
          {
            "title": "2025 - Abstract 6 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9",
            "answer_hit": true
          },
          {
            "title": "2024-Abstract 4 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - Women's Health Research Cluster",
            "snippet": "Catie is a medical student at the University of British Columbia. She also holds a Bachelor of Science degree in Neuroscience from the University of McGill.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealthresearchcluster.com%2Fprofile%2Fcatie%2Dfuthey%2F&rut=803fb7ea2240b160b6c3994fda7ecaa8a8f5c11ddd7078e7d48a4bee4f306472",
            "answer_hit": true
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257",
            "answer_hit": true
          },
          {
            "title": "WashU Figure Skating on Instagram: \" Senior Spotlight Our third senior ...",
            "snippet": "WashU Figure Skating on Instagram: \"🎓Senior Spotlight🎓 Our third senior is Naomi (@naomigmichael), who received degrees in Microbiology and Psychology. She will be moving back to her hometown of Raleigh, North Carolina to work as a medical scribe during her gap year before applying to medical schools. Naomi has also been on the Club Figure Skating team since her freshman year, serving as ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.instagram.com%2Fp%2FCPXCmAdjvfl%2F&rut=45bc4629509ffaaac2db7b3ee0d5d04688820f2c628151950dbb6f64bea0587e",
            "answer_hit": false
          },
          {
            "title": "Naomi C. Futhey (Canada)",
            "snippet": "Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5",
            "answer_hit": true
          },
          {
            "title": "Catie Futhey - The University of British Columbia | LinkedIn",
            "snippet": "MD/PhD candidate at UBC studying the molecular signatures of neurological diseases, with a particular interest in how cardiovascular and endocrine factors shape brain health. · Experience: The University of British Columbia · Education: The University of British Columbia · Location: Greater Vancouver Metropolitan Area · 500+ connections on LinkedIn. View Catie Futhey's profile on ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fca.linkedin.com%2Fin%2Fcatie%2Dfuthey%2D914103169&rut=a60a43bfe04088daefb467ba1718cce5871d5b5d9a6aefac548b9bf581469d88",
            "answer_hit": true
          }
        ]
      },
      {
        "query_name": "keyword_query_4",
        "query_category": "keyword_queries",
        "query": "Naomi C Futhey education background medical degree",
        "result_count": 10,
        "title_hits": 0,
        "snippet_hits": 6,
        "answer_hit_results": 6,
        "exact_question_hit": false,
        "results": [
          {
            "title": "PDF NAOMI (Catie) Futhey",
            "snippet": "Founded and lead an officially ratified Medical Undergraduate Society organization striving to bridge biomedical research and clinical education to address the women's health gap.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fmark%2Dcembrowski.squarespace.com%2Fs%2Fncf_cv_sep2025.pdf&rut=4c9ba8578f977e0568dfc7decaecfb0a3c2eedea2fce1327c3faa18747652304",
            "answer_hit": false
          },
          {
            "title": "Catie Futhey - CWHHA",
            "snippet": "Catie (Naomi) Futhey is an MD/PhD student at the University of British Columbia studying the molecular signatures of Alzheimer's disease and schizophrenia, with a particular interest in identifying sex-specific features.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcwhha.ca%2Four%2Dmembers%2Fcatie%2Dfuthey%2F&rut=c1b17d6163c15f357499e252293f2ca68d1ac357db495c005a586a9c3dcf0471",
            "answer_hit": true
          },
          {
            "title": "Naomi C Futhey - Wikidata",
            "snippet": "instance of human 0 references given name Naomi 0 references occupation researcher 0 references educated at University of British Columbia academic degree Doctor of Medicine start time 22 August 2022 end time 1 April 2026 1 reference stated in ORCID Public Data File 2023 filename in archive 0000-0002-0680-3141.xml last update 19 February 2023 ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wikidata.org%2Fwiki%2FQ96429409&rut=c2ac9d53e844159de6ed92fdc336c65f83f255914f5e2c2f140240b6a2832250",
            "answer_hit": true
          },
          {
            "title": "2024-Abstract 4 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is a third-year MD/PhD student at The University of British Columbia in the Graduate Program in Neuroscience. She is co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski and her project aims to understand the cellular underpinnings of schizophrenia and Alzheimer's Disease.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2024%2F09%2F10%2F2024%2Dabstract%2D4%2F&rut=de827ccb95f520f19737170c54d4c8509709db7acd02c794ab33377be9ffc6c1",
            "answer_hit": true
          },
          {
            "title": "2025 - Abstract 6 | CANP-ACNP",
            "snippet": "Naomi (Catie) Futhey is an MD/PhD candidate at the University of British Columbia, co-supervised by Dr. Veronica Hirsch-Reinshagen and Dr. Mark Cembrowski. Her doctoral research investigates spatial proteomic disease signatures in the human brain, with a focus on how vascular, inflammatory, and hormonal factors contribute to cognitive decline ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcanp.ca%2F2025%2F09%2F24%2F2025%2Dabstract%2D6%2F&rut=502cb1ca5f1ae2571c074e0ee467ffe019591b764d6ba8bcc1a6d01c1c79efd9",
            "answer_hit": true
          },
          {
            "title": "2023 Trainee Endowment Award Winners Announced",
            "snippet": "Naomi (Catie) Futhey, PhD student Under the supervision of Drs. Veronica Hirsch-Reinshagen and Mark Cembrowski, Naomi is investigating the neuropathology of cognitive impairment in chronic Schizophrenia and Alzheimer's Disease by studying the expression of neuronal and synaptic protein markers.",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.centreforbrainhealth.ca%2Fnews%2F2023%2Dtrainee%2Dendowment%2Daward%2Dwinners%2Dannounced%2F&rut=81874afa6ef93193cfdd850b14be129fceefb1fd19a9a952fa59b115e0626562",
            "answer_hit": false
          },
          {
            "title": "17 Years Too Long: Advancing Women's Health Through Medical School ...",
            "snippet": "17 Years Too Long: Advancing Women's Health Through Medical School Curricula Authors: Naomi (Catie) Futhey, MD/PhD Student, University of British Columbia Faculty of Medicine & Graduate Program in …",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwomenshealth%2Dblog.medium.com%2F17%2Dyears%2Dtoo%2Dlong%2Dadvancing%2Dwomens%2Dhealth%2Dthrough%2Dmedical%2Dschool%2Dcurricula%2Da5101ee6ec11&rut=c264561ae71258667dd44713f2d96970a1bc41c4f20503e5b0a79ee832340257",
            "answer_hit": true
          },
          {
            "title": "Naomi C. Futhey (Canada) - 20th International Conference on Alzheimer's ...",
            "snippet": "Naomi C. Futhey (Canada) University of British Columbia Djavad Mowafaghian Centre for Brain Health",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fcslide.ctimeetingtech.com%2Fadpd26%2Fattendee%2Fperson%2F3658&rut=478b50ba08e14e2f19fd79bf8250814418aa260cf144ebaa9f52838670e835e5",
            "answer_hit": true
          },
          {
            "title": "Naomi (wrestler) - Wikipedia",
            "snippet": "Trinity LaShawn Fatu[6] (née McCray; born November 30, 1987) [7] is an American professional wrestler, dancer and actress. As of January 2024, she is signed to WWE, where she performs on the Raw brand under the ring name Naomi. In August 2009, McCray signed with WWE. She was assigned to its former developmental territory, Florida Championship Wrestling (FCW), where she was the inaugural FCW ...",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FNaomi_(wrestler)&rut=08104e4d7c007493bb02a48b5d4a30b53e95ed878567ff16b12962e2474fa962",
            "answer_hit": false
          },
          {
            "title": "Index Catalog // eScholarship@McGill",
            "snippet": "Filtering by:CreatorFuthey, Naomi C.Remove constraint Creator: Futhey, Naomi C.FacultyMedicine and Health SciencesRemove constraint Faculty: Medicine and Health Sciences",
            "url": "//duckduckgo.com/l/?uddg=https%3A%2F%2Fescholarship.mcgill.ca%2Fcatalog%3Ff%255Bfaculty_sim%255D%255B%255D%3DMedicine%2Band%2BHealth%2BSciences%26locale%3Den%26q%3DFuthey%252C%2BNaomi%2BC.%26search_field%3Dnested_ordered_creator_label_ssim&rut=5612f8b2fb65fdcdfb67054c32696f7de2b331ca94a4cf6968dc57320d5fe69b",
            "answer_hit": false
          }
        ]
      }
    ],
    "category_hit_rates": {
      "full_question": {
        "query_count": 1,
        "total_results": 10,
        "answer_hit_results": 8,
        "title_hit_results": 2,
        "snippet_hit_results": 8,
        "answer_hit_rate": 0.8
      },
      "keyword_queries": {
        "query_count": 4,
        "total_results": 40,
        "answer_hit_results": 31,
        "title_hit_results": 2,
        "snippet_hit_results": 31,
        "answer_hit_rate": 0.775
      },
      "answer_probe": {
        "query_count": 0,
        "total_results": 0,
        "answer_hit_results": 0,
        "title_hit_results": 0,
        "snippet_hit_results": 0,
        "answer_hit_rate": 0.0
      },
      "overall": {
        "query_count": 5,
        "total_results": 50,
        "answer_hit_results": 39,
        "title_hit_results": 4,
        "snippet_hit_results": 39,
        "answer_hit_rate": 0.78
      }
    },
    "thresholds": {
      "full_question": 0.0,
      "keyword_queries": 0.1,
      "overall": 0.1
    },
    "passed": false,
    "triggered_rule": "keyword_query_3:answer_in_title"
  },
  "cheap_model_verification_features": {
    "question": "From which university did Naomi C Futhey earn her Doctor of Medicine degree?",
    "predicted_answer": "Naomi C. Futhey earned her Doctor of Medicine degree from **Howard University**.",
    "accepted_answers": [
      "university of british columbia"
    ],
    "answered_correctly": false,
    "passed": true,
    "triggered_rule": ""
  },
  "panel_grading_features": {
    "enabled": true,
    "model_count": 2,
    "models": [
      {
        "model_name": "openai/gpt-5.4-mini",
        "predicted_answer": "Naomi C. Futhey earned her Doctor of Medicine degree from **the University of Minnesota**.",
        "grade": "INCORRECT",
        "used_llm_grader": true
      },
      {
        "model_name": "google/gemini-3-flash-preview",
        "predicted_answer": "Naomi C. Futhey earned her Doctor of Medicine (MD) degree from the **University of Oklahoma College of Medicine**.",
        "grade": "INCORRECT",
        "used_llm_grader": true
      }
    ],
    "metrics": {
      "n": 2,
      "correct": 0,
      "incorrect": 2,
      "not_attempted": 0,
      "attempted": 2,
      "accuracy": 0.0,
      "incorrect_rate": 1.0,
      "not_attempted_rate": 0.0,
      "attempt_rate": 1.0,
      "accuracy_given_attempted": 0.0,
      "f1": 0.0
    },
    "accuracy": 0.0,
    "acceptable_range": null,
    "accuracy_threshold": 1.0
  },
  "validation": {
    "stable_answer": true,
    "answer_in_evidence": true,
    "question_unambiguous": true,
    "rewrite_guard_passed": true
  }
}
```
