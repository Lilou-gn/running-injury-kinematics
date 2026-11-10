"""Graphes propres à la présentation, dans la charte commune (python/charte_graphique.py).

Lancer depuis la racine du dépôt :
    python presentation/figures_presentation.py

Sorties : presentation/figures/*.png (format slide 16:9, 300 dpi).
La figure d'adduction de hanche lit data/coureurs.csv.
Les chiffres de l'entonnoir viennent de scripts/01_nettoyer_meta.py (voir README).
"""
from pathlib import Path
import sys

import matplotlib.pyplot as plt

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "python"))
from charte_graphique import (  # noqa: E402
    COULEURS_GROUPES, ENCRE_DOUCE, ENCRE_TEXTE, ENCRE_TITRE, FOND, GRILLE,
    MISE_EN_AVANT, appliquer_charte, titrer,
)

SORTIE = RACINE / "presentation" / "figures"
TAILLE_SLIDE = (9.6, 5.4)


def sauver(fig, nom):
    SORTIE.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(*TAILLE_SLIDE)
    fig.savefig(SORTIE / f"{nom}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def blessures_debutants():
    """Videbæk et al. (2015) : blessures pour 1 000 h de course."""
    profils = ["Coureurs réguliers", "Débutants"]
    valeurs = [7.7, 17.8]
    couleurs = [ENCRE_DOUCE, COULEURS_GROUPES["ITBS"]]  # le rouge de la charte = risque

    fig, ax = plt.subplots(figsize=TAILLE_SLIDE)
    fig.subplots_adjust(top=0.70, bottom=0.14, left=0.22, right=0.95)
    barres = ax.barh(profils, valeurs, color=couleurs, height=0.55)
    for barre, valeur in zip(barres, valeurs):
        ax.text(valeur + 0.3, barre.get_y() + barre.get_height() / 2,
                f"{valeur:.1f}".replace(".", ","), va="center",
                fontsize=18, fontweight="bold", color=ENCRE_TITRE)
    ax.set_xlim(0, 21)
    ax.set_xlabel("Blessures pour 1 000 heures de course")
    ax.grid(visible=False)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=16)
    titrer(fig, "Les débutants se blessent deux fois plus",
           "Ramené au temps passé à courir, le risque d'un débutant est 2,3 fois celui "
           "d'un coureur régulier.",
           legende="Source : Videbæk et al., Sports Medicine, 2015 (méta-analyse).")
    sauver(fig, "p01_blessures_debutants")


def entonnoir_selection():
    """De 1 832 séances à 587 coureurs (scripts/01_nettoyer_meta.py).

    Écrit la figure complète et une version par étape (p02_entonnoir_1 à 4),
    pour la faire apparaître pas à pas dans la présentation.
    """
    etapes = [
        ("Séances de course enregistrées", 1832, "1 402 coureurs"),
        ("Sains, PFPS ou ITBS", 836, "996 séances (813 coureurs) avec une autre blessure"),
        ("Diagnostic cohérent", 832, "2 coureurs sains une fois, blessés une autre"),
        ("Une séance par coureur", 587, "la première ; 110 coureurs venus plusieurs fois"),
    ]
    groupes = {"sain": 361, "PFPS": 128, "ITBS": 98}
    largeur_max = etapes[0][1]
    hauteur = 0.62

    for nb_visibles in range(1, len(etapes) + 1):
        fig, ax = plt.subplots(figsize=TAILLE_SLIDE)
        fig.subplots_adjust(top=0.74, bottom=0.08, left=0.03, right=0.97)
        for i, (nom, n, detail) in enumerate(etapes[:nb_visibles]):
            y = len(etapes) - 1 - i
            x0 = (largeur_max - n) / 2
            if i < len(etapes) - 1:
                ax.barh(y, n, left=x0, height=hauteur, color=GRILLE, edgecolor="none")
            else:  # dernière étape : découpée par groupe
                gauche = x0
                for g, eff in groupes.items():
                    ax.barh(y, eff, left=gauche, height=hauteur, color=COULEURS_GROUPES[g],
                            edgecolor=FOND, linewidth=1.5)
                    ax.text(gauche + eff / 2, y, f"{eff}", ha="center", va="center",
                            fontsize=12, fontweight="bold", color="white")
                    gauche += eff
            ax.text(x0 - 25, y + 0.08, f"{n:,}".replace(",", " "), ha="right", va="center",
                    fontsize=19, fontweight="bold", color=ENCRE_TITRE)
            ax.text(x0 - 25, y - 0.2, nom, ha="right", va="center", fontsize=11.5,
                    color=ENCRE_TEXTE)
            ax.text(x0 + n + 25, y, detail, ha="left", va="center", fontsize=11.5,
                    color=ENCRE_DOUCE)
        ax.set_xlim(-700, largeur_max + 700)
        ax.set_ylim(-0.6, len(etapes) - 0.4)
        ax.axis("off")
        titrer(fig, "De 1 832 séances à 587 coureurs comparables",
               "La grosse perte vient des autres blessures, pas du nettoyage. "
               "Dernière barre : 361 sains, 128 PFPS, 98 ITBS.")
        nom_fichier = ("p02_entonnoir_selection" if nb_visibles == len(etapes)
                       else f"p02_entonnoir_{nb_visibles}")
        sauver(fig, nom_fichier)


def adduction_hanche():
    """Pic d'adduction de hanche par groupe, dans nos données (data/coureurs.csv).

    Une valeur par coureur : la moyenne des deux jambes. Test de Kruskal-Wallis entre
    les trois groupes. Le titre s'adapte au résultat du test.
    """
    import numpy as np
    import pandas as pd
    from scipy.stats import kruskal

    coureurs = pd.read_csv(RACINE / "data" / "coureurs.csv")
    gauche = coureurs["L_HIP_ADD_PEAK_ANGLE"]
    droite = coureurs["R_HIP_ADD_PEAK_ANGLE"]
    # Garde-fou sur la convention de signe : l'adduction doit être positive des deux côtés.
    if gauche.median() < 0 < droite.median():
        gauche = -gauche
    coureurs["hanche"] = (gauche + droite) / 2
    groupes = ["sain", "PFPS", "ITBS"]
    valeurs = [coureurs.loc[coureurs["label"] == g, "hanche"].dropna() for g in groupes]
    p = kruskal(*valeurs).pvalue
    medianes = {g: v.median() for g, v in zip(groupes, valeurs)}

    fig, ax = plt.subplots(figsize=TAILLE_SLIDE)
    fig.subplots_adjust(top=0.72, bottom=0.12, left=0.10, right=0.97)
    rng = np.random.default_rng(1)
    for i, (g, v) in enumerate(zip(groupes, valeurs)):
        x = i + rng.uniform(-0.2, 0.2, len(v))
        ax.scatter(x, v, s=14, alpha=0.45, color=COULEURS_GROUPES[g], edgecolors="none")
        q1, q3 = v.quantile([0.25, 0.75])
        ax.vlines(i, q1, q3, color=ENCRE_TITRE, linewidth=2.5, zorder=3)
        ax.scatter(i, v.median(), s=110, color=FOND, edgecolors=ENCRE_TITRE,
                   linewidths=2, zorder=4)
        ax.text(i + 0.27, v.median(), f"{v.median():.1f}°".replace(".", ","),
                va="center", fontsize=13, fontweight="bold", color=ENCRE_TITRE)
    ax.set_xticks(range(3), [f"{g}\n(n = {len(v)})" for g, v in zip(groupes, valeurs)])
    ax.set_ylabel("Pic d'adduction de hanche (°)")
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", length=0, labelsize=14)

    p_txt = "p < 0,001" if p < 0.001 else f"p = {p:.3f}".replace(".", ",")
    # Groupes blessés dont la médiane dépasse nettement celle des sains (> 0,3°)
    au_dessus = [g for g in ("PFPS", "ITBS") if medianes[g] > medianes["sain"] + 0.3]
    if p < 0.05 and len(au_dessus) == 2:
        titre = "Les coureurs blessés ont plus d'adduction de hanche"
        sous_titre = (f"Comme l'annonce la littérature : la cuisse rentre davantage pendant "
                      f"l'appui ({p_txt}, Kruskal-Wallis).")
    elif p < 0.05 and len(au_dessus) == 1:
        g = au_dessus[0]
        autre = "ITBS" if g == "PFPS" else "PFPS"
        titre = f"Les coureurs {g} ont plus d'adduction de hanche, pas les {autre}"
        sous_titre = (f"Conforme à la littérature pour le {g} ({p_txt}, Kruskal-Wallis). "
                      f"Pour l'{autre}, une seule mesure ne suffit pas : il faut en combiner plusieurs.")
    else:
        titre = "Seule, l'adduction de hanche ne distingue pas les blessés"
        sous_titre = (f"La différence attendue par la littérature n'apparaît pas nettement "
                      f"({p_txt}, Kruskal-Wallis) : il faut combiner plusieurs mesures.")
    titrer(fig, titre, sous_titre,
           legende="Chaque point est un coureur (moyenne des deux jambes). Rond blanc : "
                   "médiane ; trait : écart interquartile. Source : Running Injury Clinic "
                   "Kinematic Dataset (Ferber et al., 2024), 587 coureurs.")
    sauver(fig, "p03_adduction_hanche")
    print(f"Adduction de hanche : médianes {medianes}, {p_txt}")


if __name__ == "__main__":
    appliquer_charte()
    blessures_debutants()
    entonnoir_selection()
    if (RACINE / "data" / "coureurs.csv").exists():
        adduction_hanche()
    else:
        print("data/coureurs.csv absent : figure d'adduction de hanche non générée")
    print("Figures écrites dans", SORTIE)
