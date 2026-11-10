# Bibliographie : la course, le genou et les blessures

Messages clés, chiffres et sources du contexte biologique, pour la présentation (`presentation/presentation.qmd`) et le rapport.

## Le fil de l'histoire

1. La course est l'un des sports les plus accessibles, pratiqué par des millions de personnes pour leur santé.
2. Mais elle blesse beaucoup, surtout les débutants, et le marathon attire de plus en plus de débutants.
3. Le genou est le premier touché, avec deux blessures en tête : le PFPS et l'ITBS.
4. Ces deux douleurs du genou ont en partie une origine à la hanche, visible dans la foulée.
5. Elles sont difficiles à diagnostiquer : pas d'examen de référence.
6. Le ML et le DL peuvent lire la foulée mieux que l'œil, et nous dire où regarder.

## Messages clés et chiffres

### 1. La course, un sport de santé accessible

- 13,2 millions de Français ont couru en 2025, environ un million de plus qu'il y a cinq ans (Observatoire du running, UESC, 2026).
- Motivations : bien-être 55 %, santé 50 %, plaisir 42 %, compétition 39 %, gestion du poids 24 % (UESC, 2026).
- « Néo-runners » (moins de 2 ans de pratique) : 63 % de femmes, 80 % de moins de 35 ans (UESC, 2026).
- 40 % des Français courent, dont 13 % au moins une fois par semaine (+5 points depuis 2018) ; 90 % jugent la course efficace pour se maintenir en forme (Odoxa, 2023, 992 personnes).
- 61 % des Français de 15 ans et plus font du sport au moins une fois par semaine (INJEP, 2025).
- L'OMS recommande 150 à 300 min d'activité modérée ou 75 à 150 min d'activité soutenue par semaine ; 27,5 % des adultes n'y arrivent pas (OMS Europe, 2021).
- **Non trouvé** : la part de coureurs pour qui la course est le seul sport, ou un moyen de « se remettre en forme ».

### 2. Un risque de blessure élevé, surtout chez les débutants

- 19 % à 79 % des coureurs se blessent à la jambe sur une année, selon les définitions (van Gent et al., 2007).
- Débutants : 17,8 blessures pour 1 000 h de course, contre 7,7 chez les coureurs réguliers (Videbæk et al., 2015).
- Hypothèse admise : une hausse trop rapide du volume dépasse la capacité d'adaptation des tissus, mais les études n'identifient pas encore quelles erreurs d'entraînement causent les blessures (Nielsen et al., 2012).
- Facteurs de risque établis : grande distance hebdomadaire chez l'homme, antécédent de blessure (van Gent et al., 2007).
- Marathon de Paris 2026 : 58 853 partants, 49 % de premiers marathons, âge moyen 38 ans, 33 % de femmes (28 % en 2024).
- Les personnes de 29, 39, 49 ans… sont 48 % plus nombreuses que prévu parmi les premiers marathoniens : « crise de sens » à l'approche d'une nouvelle décennie (Alter et Hershfield, PNAS, 2014).
- Premiers marathoniens de New York : 9,5 % de blessures graves (pas de départ ou abandon), 49 % de blessures mineures, sur 675 coureurs (Phys Sportsmed, 2021).

### 3. Le genou en première ligne

- Le genou est la région la plus touchée (van Gent et al., 2007) : 28 % des blessures, 40 % chez les femmes contre 31 % chez les hommes (Francis et al., 2019).
- PFPS = blessure la plus fréquente du coureur, ITBS = la deuxième (Taunton et al., 2002, 2 002 blessures). Le PFPS représente 17 % des pathologies (Francis et al., 2019) ; l'ITBS touche 1,6 % à 12 % des coureurs (revue ITBS, 2024).
- Vérifié dans nos données : le genou est l'articulation blessée la plus fréquente (348 séances sur 1 832) ; PFPS (134) et ITBS (126) sont les deux diagnostics précis les plus nombreux, derrière « douleur » (232) et « autre » (184).
- PFPS chez l'adulte : jusqu'à 57 % d'évolution défavorable 5 à 8 ans après le diagnostic (IASP, 2023).

### 4. PFPS et ITBS : deux mécanismes, une origine commune à la hanche

- PFPS : douleur autour ou derrière la rotule, aggravée par les activités qui chargent le genou (Crossley et al., 2016) ; multifactoriel (surcharge, erreurs d'entraînement, mécanique de hanche et de genou) (IASP, 2023).
- ITBS : douleur externe du genou ; hypothèse actuelle = compression d'un coussinet graisseux très innervé quand le genou dépasse environ 30° de flexion, plutôt qu'un frottement (revue ITBS, 2024).
- Études prospectives (foulée filmée avant la blessure) : PFPS associé à plus d'adduction de hanche (Noehren et al., 2013 : 400 coureuses, 15 cas) ; ITBS associé à plus d'adduction de hanche et de rotation interne du genou (Noehren et al., 2007 : 18 cas).
- PFPS plus fréquent chez la femme ; moins de 34 ans = facteur de risque (Taunton et al., 2002).

### 5. Un diagnostic difficile

- PFPS : diagnostic d'exclusion, pas de test clinique définitif ; l'examen clinique est « la pierre angulaire » ; imagerie généralement inutile (Crossley et al., 2016 ; IASP, 2023).
- ITBS : diagnostic clinique ; les tests (Noble) n'ont pas une sensibilité ni une spécificité satisfaisantes ; imagerie seulement en cas d'échec ou de récidive (revue ITBS, 2024).

### 6. Ce que le ML et le DL apportent

- Le ML traite de grandes quantités de données biomécaniques et réduit leur dimension ; limites fréquentes : validation insuffisante, petits échantillons, populations mal décrites (Xiang et al., 2022).
- Sur nos données, un CNN sur les courbes d'angles distingue mieux les blessés que les modèles classiques, selon l'accuracy rapportée (Fuentes-Jiménez et al., 2026) ; attention, l'accuracy est trompeuse avec des classes déséquilibrées.
- Perspective : suivi de la foulée en temps réel avec des capteurs portables, pour la prévention (Xiang et al., 2022).

## Sources

**Pratique de la course**

- [Observatoire du running 2026, Union Sport & Cycle (UESC), relayé par Marathons.com](https://www.marathons.com/fr/conseils/observatoire-du-running-2026-13-2-millions-de-pratiquants-et-un-marche-toujours-en-croissance_3y4j)
- [Baromètre national des pratiques sportives 2025, INJEP, ministère des Sports](https://www.sports.gouv.fr/sport-en-france-une-progression-continue-depuis-2018-boostee-par-les-jeux-de-paris-2024-10055)
- [Baromètre Odoxa pour Winamax et RTL, « Les Français et la course à pied », mars 2023](https://patrickbayeux.com/wp-content/uploads/2024/06/2302-Barometre-Sport-Odoxa_Winamax_RTL-Les-Francais-et-la-course-a-pied.pdf)
- [OMS Europe, fiche « Activité physique », 2021](https://www.who.int/europe/news-room/fact-sheets/item/physical-activity)

**Blessures**

- [van Gent RN et al. (2007). Incidence and determinants of lower extremity running injuries in long distance runners: a systematic review. Br J Sports Med](https://pmc.ncbi.nlm.nih.gov/articles/PMC2465455)
- [Videbæk S et al. (2015). Incidence of running-related injuries per 1000 h of running in different types of runners. Sports Medicine](https://pmc.ncbi.nlm.nih.gov/articles/PMC4473093)
- [Nielsen RO et al. (2012). Training errors and running related injuries: a systematic review. Int J Sports Phys Ther](https://pmc.ncbi.nlm.nih.gov/articles/PMC3290924)
- [Taunton JE et al. (2002). A retrospective case-control analysis of 2002 running injuries. Br J Sports Med](https://pubmed.ncbi.nlm.nih.gov/11916889/)
- [Francis P et al. (2019). The proportion of lower limb running injuries by gender, anatomical location and specific pathology. J Sports Sci Med](https://jssm.org/jssm-18-21.xml-Fulltext)

**Marathon**

- [Chiffres clés du Marathon de Paris 2026, Marathons.com](https://www.marathons.com/fr/save-the-date/les-chiffres-cles-du-marathon-de-paris-2026-une-edition-record-et-populaire_kppg)
- [Alter AL, Hershfield HE (2014). People search for meaning when they approach a new decade in chronological age. PNAS (résumé de la British Psychological Society)](https://bps.org.uk/research-digest/why-youre-particularly-likely-run-your-first-marathon-when-your-age-ends-9)
- [Blessures chez les premiers marathoniens de New York, The Physician and Sportsmedicine, 2021 (résumé de Sports Performance Bulletin)](https://sportsperformancebulletin.com/injuries-health/endurance-injuries-and-health/first-time-marathon-runners-the-true-risk-of-injury)

**PFPS et ITBS**

- [Crossley KM et al. (2016). Patellofemoral pain consensus statement. Br J Sports Med](https://pmc.ncbi.nlm.nih.gov/articles/PMC4975817)
- [IASP (2023). Fiche « Patellofemoral Pain »](https://www.iasp-pain.org/resources/fact-sheets/patellofemoral-pain-pfp/)
- [Revue sur l'ITBS (2024). Current Physical Medicine and Rehabilitation Reports](https://link.springer.com/article/10.1007/s40141-024-00442-w)
- [Noehren B et al. (2007). Prospective study of the biomechanical factors associated with iliotibial band syndrome. Clinical Biomechanics](https://read.qxmd.com/read/17728030/asb-clinical-biomechanics-award-winner-2006-prospective-study-of-the-biomechanical-factors-associated-with-iliotibial-band-syndrome)
- [Noehren B et al. (2013). Prospective evidence for a hip etiology in patellofemoral pain. Med Sci Sports Exerc](https://scholars.uky.edu/en/publications/prospective-evidence-for-a-hip-etiology-in-patellofemoral-pain/)

**Machine learning et données**

- [Xiang L et al. (2022). Recent machine learning progress in lower limb running biomechanics with wearable technology: a systematic review. Frontiers in Neurorobotics](https://pmc.ncbi.nlm.nih.gov/articles/PMC9201717)
- [Fuentes-Jiménez D et al. (2026). Explainable machine-learning based detection of knee injuries in runners. arXiv](https://arxiv.org/pdf/2602.11668)
- [Ferber R et al. (2024). A biomechanical dataset of 1,798 healthy and injured subjects during treadmill walking and running. Scientific Data](https://doi.org/10.1038/s41597-024-04011-7)

*Lu et vérifié sur les pages citées, sauf Taunton (2002), Noehren (2007, 2013), Alter et Hershfield (2014) et l'étude new-yorkaise (2021), dont seuls les résumés ont pu être lus.*
