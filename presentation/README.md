# Présentation orale (20 min)

Diaporama Quarto (revealjs) de la restitution du 20 novembre, dans la charte commune du projet.

## Générer la présentation

Depuis ce dossier :

```bash
quarto render presentation.qmd     # -> presentation.html
```

Pour une version en un seul fichier (à envoyer ou à ouvrir sans connexion) :

```bash
# mettre embed-resources: true dans l'en-tête, puis :
quarto render presentation.qmd
```

Pendant l'oral : touche **S** pour les notes de l'orateur, **F** pour le plein écran, **Échap** pour la vue d'ensemble.

## Contenu

| Fichier | Rôle |
|---|---|
| `presentation.qmd` | Les slides. Le déroulé et la durée de chaque partie sont en commentaire en tête du fichier. |
| `theme.scss` | Couleurs et typographie, reprises de `python/charte_graphique.py` et `R/theme_projet.R`. |
| `progression.html` | Repère de progression en haut à droite (Problème · Données · Modèles · Biologie). |
| `polices.html`, `polices/` | Police Atkinson Hyperlegible embarquée (licence OFL), pour que la présentation marche hors ligne. |
| `figures_presentation.py` | Graphes propres à la présentation : blessures des débutants, entonnoir de sélection (une image par étape, pour l'animation) et adduction de hanche par groupe (lit `data/coureurs.csv`). À lancer depuis la racine du dépôt : `python presentation/figures_presentation.py`. |
| `figures/` | Sorties du script ci-dessus. |

Les autres graphes viennent de `figures/slides/` (exploration 1). Les chiffres et les sources du contexte sont dans `../bibliographie.md`.

## Ce qui reste à faire

- **Lancer `python presentation/figures_presentation.py` depuis la racine du dépôt** : la figure `p03_adduction_hanche.png` livrée est une image d'attente, la vraie est calculée sur `data/coureurs.csv` (son titre s'adapte au résultat du test).
- Les slides encadrées en pointillés (« À compléter par Lilou » ou « par Charles ») attendent les résultats des branches `modeles-r` et `deep-learning`. La slide « Les modèles regardent-ils là où la biologie l'attend ? » se remplit à la fin, avec les deux.
