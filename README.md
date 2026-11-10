# Détection des blessures du genou chez le coureur

La cinématique du membre inférieur pendant l'appui permet-elle de distinguer les coureurs atteints d'un syndrome fémoro-patellaire (PFPS) ou d'un syndrome de la bandelette ilio-tibiale (ITBS) des coureurs sains ? Et les variables sur lesquelles s'appuient les modèles sont-elles cohérentes avec la physiopathologie connue de ces deux syndromes ?

Le projet compare des modèles classiques (R, tidymodels) et du deep learning (Python, PyTorch) sur les mêmes coureurs, découpés dans les mêmes plis.

## Démarrer : les trois fichiers à utiliser

| Fichier | Contenu |
|---|---|
| [data/coureurs.csv](data/coureurs.csv) | 587 coureurs (une ligne chacun) : label, métadonnées et 79 variables cinématiques |
| [data/plis.csv](data/plis.csv) | Plis de validation croisée communs à R et Python (5 plis × 5 répétitions) |
| [data/dictionnaire_variables.csv](data/dictionnaire_variables.csv) | Rôle, description et unité de chaque colonne |

Pas besoin de relancer les scripts pour travailler : les fichiers sont versionnés.

```r
coureurs <- read.csv("data/coureurs.csv")
plis <- read.csv("data/plis.csv")   # même ordre de sub_id que coureurs
```

```python
import pandas as pd
coureurs = pd.read_csv("data/coureurs.csv")
plis = pd.read_csv("data/plis.csv")
```

Pour la répétition `r` et le pli `k`, le jeu de test est formé des coureurs où `plis[f"rep{r}"] == k`. On commence par `rep1` à l'étape 1.

## Les données

**Source :** *Running Injury Clinic Kinematic Dataset*, Université de Calgary : 1 798 sujets enregistrés sur tapis entre 2009 et 2017 (capture Vicon, 7 segments). Ferber et al., *Scientific Data*, 2024. Les données sont sur [Figshare](https://doi.org/10.25452/figshare.plus.24255795.v2), sous licence CC BY 4.0.

**Effectifs retenus :**

| | Sains | PFPS | ITBS | Total |
|---|---|---|---|---|
| Coureurs | 361 | 128 | 98 | 587 |

Répondre toujours « sain » donne déjà 61,5 % de bonnes réponses. Il faut donc juger les modèles sur l'accuracy équilibrée, la sensibilité et la spécificité, pas sur l'accuracy brute.

### Comment on passe de 1 832 séances à 587 coureurs

| Étape | Séances | Coureurs | Ce qui est retiré, et pourquoi |
|---|---|---|---|
| Fichier `run_data_meta.csv` | 1 832 | 1 402 | Toutes les séances de course du dataset |
| 1. Garder sain, PFPS et ITBS | 836 | 589 | 996 séances avec une autre blessure (tendinite, arthrose, lombalgie…) : hors sujet |
| 2. Retirer les diagnostics contradictoires | 832 | 587 | 2 coureurs sains à une séance et blessés à une autre (100198, 100313) : label incertain |
| 3. Une séance par coureur | 587 | 587 | 245 séances répétées : on garde la première |

**Étape 1, définition du label.** On reprend celle des auteurs (README Figshare). Un coureur est **sain** si trois conditions sont réunies : `InjDefn` vaut « No injury », l'articulation blessée est vide ou vaut « No injury », et aucun diagnostic n'est renseigné. Il est **PFPS** ou **ITBS** si c'est son diagnostic principal (`SpecInjury`), après regroupement des orthographes (`pfps` → PFPS, `itbs` → ITBS).

**Étape 3, pourquoi une seule séance.** 110 coureurs sont venus plusieurs fois, souvent avec plusieurs essais le même jour. Si on garde toutes leurs séances, un même coureur peut se retrouver à la fois dans les plis d'entraînement et de test : le modèle reconnaîtrait la personne, pas la blessure. On garde la première séance, comme le font les auteurs dans l'article.

Les étapes suivantes ne retirent plus personne, elles nettoient les valeurs :

4. **Valeurs impossibles.** Elles sont mises à vide puis imputées par la médiane du sexe : âge hors 10-90 ans, taille hors 130-220 cm, poids hors 30-200 kg. Seuls 3 coureurs sont concernés (colonne `gabarit_impute`). La jambe dominante manquante (85 coureurs) est mise à « Right », la modalité majoritaire.
5. **Côté et durée de blessure vidés chez les sains.** Le fichier brut indique un côté blessé pour 184 sains, ce qui est sans objet.
6. **Variables cinématiques (`dv_r`).** Ce sont les valeurs résumées calculées par les auteurs (médiane sur les foulées), lues dans les JSON. Sur les 76 champs, 36 sont des emplacements vides (toujours 0) : il reste 40 variables. `STEP_WIDTH` étant identique pour les deux jambes, on en garde une colonne. Cela fait 1 + 39 × 2 = **79 variables**, préfixées `L_` (gauche) ou `R_` (droite).

### Ce qui est signalé, mais pas retiré

| Colonne | Coureurs | Pourquoi c'est signalé |
|---|---|---|
| `qualite_suspecte` | 3 sains (100540, 100545, 201091) | Angles impossibles (rotation du genou à 179°, dorsiflexion à 136°) : échec probable du calcul des auteurs |
| `antecedent_autre_blessure` | 9 sains, 1 PFPS, 1 ITBS | Une séance antérieure avec une autre blessure |
| `blessure_secondaire` | 1 sain, 24 PFPS, 21 ITBS | Diagnostic secondaire déclaré (dont des ITBS avec un PFPS secondaire) |

Ces colonnes permettent des analyses de sensibilité (relancer en excluant ces coureurs).

### Les pièges à connaître avant de modéliser

- **Fuite d'information :** `InjSide`, `InjDuration` et `blessure_secondaire` ne sont renseignées que chez les blessés. Elles ne doivent jamais entrer dans un modèle. Il en va de même pour `annee` et `hz_r` (voir le point suivant). Les variables utilisables sont celles de rôle `cinematique` et `controle` dans le dictionnaire.
- **Année d'enregistrement :** la colonne `annee` est bien dans `coureurs.csv`, pour l'analyser, mais pas pour la donner au modèle. Elle est fortement confondue avec le label. De 2009 à 2011, on compte 43 sains pour 108 blessés ; de 2012 à 2017, 318 sains pour 118 blessés. Un modèle peut donc apprendre l'époque (matériel, cliniciens) plutôt que la blessure. À décrire dans l'analyse, et à tester si le temps le permet.
- **Vitesse :** les sains courent un peu plus vite (2,77 m/s en moyenne, contre 2,60 pour les PFPS et 2,64 pour les ITBS), et la vitesse modifie tous les angles. Elle sert de variable de contrôle. Elle vaut exactement longueur de foulée × cadence / 60 : ces trois variables sont redondantes.
- **Conventions de signe :** la flexion du genou est négative. La chute du bassin (`PELVIS_*`) est de signe opposé entre gauche et droite, c'est la convention des auteurs, conservée telle quelle. Les « pics » sont des médianes sur toutes les foulées enregistrées.
- **Valeurs manquantes :** seule `VERTICAL_OSCILLATION` en a, pour 4 coureurs. Trois d'entre eux ont été enregistrés à 120 Hz au lieu de 200.
- **Les plis sont stratifiés sur sain / PFPS / ITBS**, ce qui permet aussi de séparer PFPS et ITBS plus tard. Une même graine ne donne pas les mêmes plis en R et en Python : c'est pour ça que les plis sont dans un fichier.

## Reproduire les données

```bash
pip install -r requirements.txt
python scripts/01_nettoyer_meta.py      # métadonnées -> data/intermediaire/meta_clean.csv
python scripts/02_extraire_dv_r.py      # dv_r depuis Figshare -> data/intermediaire/dv_r_brut.csv
python scripts/03_construire_coureurs.py  # -> coureurs.csv, plis.csv, dictionnaire
```

- `ric_data.zip` pèse 22,7 Go. Le script 02 ne télécharge que les 587 JSON utiles (environ 6 Go) en lisant l'archive à distance, et ne stocke rien d'autre que `dv_r`. S'il s'arrête (réseau), il suffit de le relancer : il reprend où il en était.
- `--zip CHEMIN` utilise une copie locale de l'archive. `--garder-json DOSSIER` conserve les JSON (environ 13 Go), nécessaires pour recalculer les courbes d'angles complètes.
- L'archive est compressée en Deflate64, que le module `zipfile` de Python ne sait pas lire, d'où la dépendance `inflate64`.

**Courbes d'angles pour le CNN :** elles ne sont pas stockées dans les JSON. Il faut les recalculer avec le code MATLAB des auteurs (`gait_kinematics.m`, `gait_steps.m`, dans `Supplemental_materials.zip` sur Figshare), ou le porter en Python.

## Charte graphique (commune à tout le groupe)

Pour que la présentation soit cohérente, **tous les graphes utilisent la même charte**, en R comme en Python. Elle suit le cours de data visualisation (R. Mahmoud) et les conseils de Cara Thompson ([« Créer un beau graphique »](https://cararthompson.github.io/rencontresR/slides/beau-graphique.html)).

**Couleurs des groupes : palette « Douleur ».** Les couleurs chaudes signalent la blessure (la douleur), le gris-bleu froid signale les coureurs sains, qui servent de référence.

| Groupe | Couleur | Code | Forme de point |
|---|---|---|---|
| Sain | gris-bleu | `#5E6A77` | rond |
| PFPS | ambre | `#C98A1A` | carré |
| ITBS | lie-de-vin | `#7A1E3A` | triangle |

La palette a été testée par simulation de daltonisme (deutéranopie, protanopie, tritanopie) : les trois couleurs restent distinctes, y compris en noir et blanc. Toujours dans l'ordre sain, PFPS, ITBS.

**Autres éléments :** fond `#F8F8F8`, titres `#14202E`, texte `#3F4A57`. Police [Atkinson Hyperlegible](https://fonts.google.com/specimen/Atkinson+Hyperlegible), conçue pour la lisibilité (amphi, vidéoprojecteur). Pour mettre en évidence autre chose qu'un groupe, on utilise le bleu nuit `#14202E` et on grise le reste.

**Règles pour chaque graphe :**
- un seul message, écrit en phrase dans le titre ; le sous-titre dit ce qu'on regarde ;
- source et définitions en bas du graphe (légende de figure) ;
- les noms de groupes colorés dans le sous-titre plutôt qu'une légende séparée ;
- barres qui partent de 0, pas de camembert, pas de 3D ;
- pourcentages à la française (« 35 % ») ;
- deux exports : `figures/exploration/` (notebook) et `figures/slides/` (16:9, pour la présentation).

**En R (ggplot2) :**

```r
source("R/theme_projet.R")
p <- ggplot(coureurs, aes(label, speed_r, fill = label)) +
  geom_boxplot() +
  scale_fill_manual(values = couleurs_groupes) +
  labs(title = "Titre-message", subtitle = "Ce qu'on regarde", caption = source_donnees) +
  theme_projet()
sauver_figure(p, "05_mon_graphe")
```

**En Python (matplotlib) :**

```python
from charte_graphique import appliquer_charte, COULEURS_GROUPES, titrer, sauver_figure
appliquer_charte()
# ... tracer avec color=COULEURS_GROUPES[groupe] ...
titrer(fig, "Titre-message", "Ce qu'on regarde")
sauver_figure(fig, "05_mon_graphe")
```

Les fichiers de la charte sont [R/theme_projet.R](R/theme_projet.R) et [python/charte_graphique.py](python/charte_graphique.py). Si on change une couleur, on la change dans les deux.

## Organisation du dépôt

```
data/
  brut/run_data_meta.csv         métadonnées Figshare (non modifiées)
  intermediaire/                 sorties des scripts 01 et 02
  coureurs.csv  plis.csv  dictionnaire_variables.csv
scripts/                         pipeline de préparation (01 -> 03)
R/theme_projet.R                 charte graphique ggplot2
python/charte_graphique.py       charte graphique matplotlib
```

**Branches :** `main` contient le socle commun ci-dessus. Chacun travaille sur sa branche, créée depuis `main` :

- `donnees-biologie` (A) : description des groupes, tests, ancrage biologique ;
- `modeles-r` (B) : régression logistique, forêt aléatoire, SVM ;
- `deep-learning` (C) : MLP, puis CNN 1D.

Toute modification de `coureurs.csv` passe par les scripts et par `main`, pour que tout le monde travaille sur la même version.

## Références

- Ferber R. et al. (2024). *A biomechanical dataset of 1,798 healthy and injured subjects during treadmill walking and running.* Scientific Data. doi:10.1038/s41597-024-04011-7.
- Running Injury Clinic Kinematic Dataset, Figshare+, [doi:10.25452/figshare.plus.24255795.v2](https://doi.org/10.25452/figshare.plus.24255795.v2).
