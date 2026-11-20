import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from charte_graphique import appliquer_charte, sauver_figure, titrer

folder_path = Path("/home/charles/Téléchargements/données/ric_data/reformat_data/")
BASE_DIR = Path(__file__).resolve().parent
select = pd.read_csv(BASE_DIR.parent / "data/coureurs.csv")

ZONES = {
    "Bassin": ("#14202E", "o"),
    "Cuisse": ("#7A1E3A", "s"),
    "Jambe": ("#5E6A77", "^"),
    "Pied": ("#C98A1A", "D"),
}


def localisation_marqueurs(idx):
    coureur = select.iloc[idx]
    chemin = folder_path / str(coureur["sub_id"]) / coureur["filename"]
    with chemin.open(encoding="utf-8") as fichier:
        positions = json.load(fichier)["neutral"]

    segments = pd.DataFrame.from_dict(
        positions, orient="index", columns=["X", "Y", "Z"]
    )
    zones = segments.index.to_series().str.extract(
        r"(pelvis|thigh|shank|foot|toe)", expand=False
    ).map({
        "pelvis": "Bassin", "thigh": "Cuisse", "shank": "Jambe",
        "foot": "Pied", "toe": "Pied",
    })

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 6.8), sharey=True)
    fig.subplots_adjust(left=0.10, right=0.96, top=0.83, bottom=0.23, wspace=0.14)
    for ax, coordonnee, titre, ancrage in zip(
        axes, ("X", "Z"), ("Vue de face", "Vue de profil"), ("E", "W")
    ):
        for zone, (couleur, symbole) in ZONES.items():
            points = segments.loc[zones == zone]
            ax.scatter(
                points[coordonnee], points["Y"], label=zone, c=couleur,
                marker=symbole, s=40, edgecolors="white", linewidths=0.45, zorder=3,
            )
        ax.set_title(titre, loc="center")
        ax.set_xlabel(f"{coordonnee} (mm)")
        ax.margins(x=0.12)
        ax.set_aspect("equal", adjustable="box", anchor=ancrage)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=3 if coordonnee == "X" else 2))
        ax.grid(axis="x", visible=False)

    axes[0].set_ylabel("Hauteur Y (mm)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncols=4, bbox_to_anchor=(0.5, 0.035))
    titrer(fig, "Position des marqueurs au repos",
           legende="Source : Running Injury Clinic Kinematic Dataset (Ferber et al., 2024).")
    sauver_figure(fig, "loc_marqueurs", taille_slide=fig.get_size_inches())
    plt.close(fig)
    return positions


if __name__ == "__main__":
    appliquer_charte(taille_base=15)
    localisation_marqueurs(10)
