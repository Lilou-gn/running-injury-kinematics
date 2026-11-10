"""Charte graphique commune du projet, version Python (matplotlib).

Même palette, même police et même hiérarchie de textes que R/theme_projet.R,
pour que les graphes R et Python se ressemblent dans la présentation.

Usage :
    from charte_graphique import appliquer_charte, COULEURS_GROUPES, titrer, sauver_figure
    appliquer_charte()
    fig, ax = plt.subplots()
    ...
    titrer(fig, "Titre-message du graphe", "Sous-titre : ce qu'on regarde")
    sauver_figure(fig, "05_mon_graphe")
"""
from pathlib import Path
import urllib.request

import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- Couleurs (identiques à R/theme_projet.R) ----
# Palette « Douleur » : couleurs chaudes = blessure, gris-bleu froid = sains (référence).
COULEURS_GROUPES = {"sain": "#5E6A77", "PFPS": "#C98A1A", "ITBS": "#7A1E3A"}
MARQUEURS_GROUPES = {"sain": "o", "PFPS": "s", "ITBS": "^"}  # redondance noir et blanc
ORDRE_GROUPES = ["sain", "PFPS", "ITBS"]

ENCRE_TITRE = "#14202E"
ENCRE_TEXTE = "#3F4A57"
ENCRE_DOUCE = "#6B7580"
FOND = "#F8F8F8"
GRILLE = "#E3E5E8"
MISE_EN_AVANT = "#14202E"  # accent hors groupes, pour « pointer » un élément

SOURCE_DONNEES = ("Source : Running Injury Clinic Kinematic Dataset "
                  "(Ferber et al., 2024), 587 coureurs.")

_URL_POLICE = "https://github.com/google/fonts/raw/main/ofl/atkinsonhyperlegible/"
_DOSSIER_POLICE = Path.home() / ".cache" / "running-injury-kinematics" / "polices"


def _charger_police():
    """Télécharge Atkinson Hyperlegible une fois, sinon se replie sur DejaVu Sans."""
    try:
        _DOSSIER_POLICE.mkdir(parents=True, exist_ok=True)
        for nom in ("AtkinsonHyperlegible-Regular.ttf", "AtkinsonHyperlegible-Bold.ttf"):
            chemin = _DOSSIER_POLICE / nom
            if not chemin.exists():
                urllib.request.urlretrieve(_URL_POLICE + nom, chemin)
            font_manager.fontManager.addfont(str(chemin))
        return "Atkinson Hyperlegible"
    except Exception:
        return "DejaVu Sans"


def appliquer_charte(taille_base=14):
    """Règle le style matplotlib : police, couleurs, grille discrète, fond commun."""
    police = _charger_police()
    plt.rcParams.update({
        "font.family": police,
        "font.size": taille_base,
        "text.color": ENCRE_TEXTE,
        "axes.labelcolor": ENCRE_TEXTE,
        "axes.edgecolor": GRILLE,
        "axes.facecolor": FOND,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.titlesize": taille_base * 1.05,
        "axes.titleweight": "bold",
        "axes.titlecolor": ENCRE_TITRE,
        "axes.titlelocation": "left",
        "grid.color": GRILLE,
        "grid.linewidth": 0.6,
        "xtick.color": ENCRE_TEXTE,
        "ytick.color": ENCRE_TEXTE,
        "xtick.labelsize": taille_base * 0.95,
        "ytick.labelsize": taille_base * 0.95,
        "legend.frameon": False,
        "figure.facecolor": FOND,
        "savefig.facecolor": FOND,
        "figure.dpi": 110,
    })
    return police


def titrer(fig, titre, sous_titre=None, legende=None):
    """Titre-message (gras, foncé), sous-titre et légende de figure, alignés à gauche."""
    taille = plt.rcParams["font.size"]
    fig.suptitle(titre, x=0.01, ha="left", fontsize=taille * 1.5, fontweight="bold",
                 color=ENCRE_TITRE)
    if sous_titre:
        fig.text(0.01, 0.905, sous_titre, ha="left", va="top", fontsize=taille * 1.1,
                 color=ENCRE_TEXTE, wrap=True)
    fig.text(0.01, -0.02, legende or SOURCE_DONNEES, ha="left", va="top",
             fontsize=taille * 0.8, color=ENCRE_DOUCE, wrap=True)


def sauver_figure(fig, nom, dossier="figures/exploration"):
    """Enregistre la version notebook et la version slide (16:9) du graphe."""
    racine = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "coureurs.csv").exists())
    for sous_dossier, taille in ((dossier, None), ("figures/slides", (9.6, 5.4))):
        sortie = racine / sous_dossier
        sortie.mkdir(parents=True, exist_ok=True)
        if taille:
            fig.set_size_inches(*taille)
        fig.savefig(sortie / f"{nom}.png", dpi=300, bbox_inches="tight")
