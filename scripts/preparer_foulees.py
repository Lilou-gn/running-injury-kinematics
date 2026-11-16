"""Préparation des foulées pour le CNN 1D.

Corrige les problèmes vus sur la première version (process.py) :
- marqueurs choisis par leur nom (l'ordre et le nombre de canaux varient selon les fichiers) ;
- positions exprimées par rapport au centre du bassin et divisées par la taille du coureur :
  le réseau voit le mouvement, plus la place sur le tapis ni la morphologie ;
- interpolation qui ramène vraiment chaque foulée sur 150 points (0 à 100 % du cycle) ;
- même nombre de foulées par coureur (celles du milieu de l'enregistrement), pour qu'un
  enregistrement de 60 s ne pèse pas trois fois plus qu'un de 20 s.

La standardisation (moyenne 0, écart-type 1) n'est PAS faite ici : elle doit être calculée
sur les coureurs d'entraînement de chaque pli, dans le script du modèle.

Usage (depuis la racine du dépôt) :
    python scripts/preparer_foulees.py --json /chemin/vers/reformat_data

Sorties dans data/features/ :
    X_foulees.npy      (n_foulees, 84, 150) float32 : 28 marqueurs x 3 axes, 150 instants
    foulees.csv        une ligne par foulée : sub_id, label, blesse, numéro de la foulée
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

RACINE = Path(__file__).resolve().parents[1]

SEGMENTS = ["pelvis", "L_thigh", "R_thigh", "L_shank", "R_shank", "L_foot", "R_foot"]
MARQUEURS = [f"{s}_{i}" for s in SEGMENTS for i in range(1, 5)]   # 28 marqueurs
PIED_DROIT = [MARQUEURS.index(f"R_foot_{i}") for i in range(1, 5)]
BASSIN = [MARQUEURS.index(f"pelvis_{i}") for i in range(1, 5)]
AXE_VERTICAL = 1          # axe Y : vertical (le bassin est à environ 1 000 mm)
DUREE_FOULEE = (0.5, 1.1)  # durée plausible d'une foulée, en secondes


def lire_marqueurs(chemin):
    """Tableau (28, n_images, 3) des marqueurs, dans un ordre fixe."""
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    course = donnees["running"]
    manquants = [m for m in MARQUEURS if m not in course]
    if manquants:
        raise ValueError(f"marqueurs absents : {manquants}")
    return np.asarray([course[m] for m in MARQUEURS], dtype=np.float64)


def centrer_et_mettre_a_l_echelle(marqueurs, taille_cm):
    """Positions relatives au centre du bassin, à chaque instant, divisées par la taille."""
    centre = marqueurs[BASSIN].mean(axis=0, keepdims=True)   # (1, n_images, 3)
    return (marqueurs - centre) / (taille_cm * 10)            # taille en mm


def decouper_foulees(marqueurs, hauteur_pied, fs):
    """Découpe d'un point bas du pied droit au suivant (un cycle complet)."""
    lisse = savgol_filter(hauteur_pied, 21, 3)
    minima, _ = find_peaks(-lisse, distance=int(0.6 * fs))
    foulees = []
    for debut, fin in zip(minima[:-1], minima[1:]):
        if DUREE_FOULEE[0] <= (fin - debut) / fs <= DUREE_FOULEE[1]:
            foulees.append(marqueurs[:, debut:fin + 1, :])
    return foulees


def normaliser_foulee(foulee, n_points):
    """Ramène la foulée sur n_points répartis de 0 à 100 % du cycle."""
    n = foulee.shape[1]
    t_ancien = np.arange(n)
    t_nouveau = np.linspace(0, n - 1, n_points)
    sortie = np.empty((foulee.shape[0], n_points, 3))
    for m in range(foulee.shape[0]):
        for axe in range(3):
            sortie[m, :, axe] = np.interp(t_nouveau, t_ancien, foulee[m, :, axe])
    return sortie


def foulees_du_milieu(foulees, n_max):
    """Garde les n_max foulées centrales (le début et la fin sont moins stables)."""
    if len(foulees) <= n_max:
        return foulees
    debut = (len(foulees) - n_max) // 2
    return foulees[debut:debut + n_max]


def main():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--json", type=Path, required=True,
                         help="dossier reformat_data (un sous-dossier par coureur)")
    parseur.add_argument("--n-foulees", type=int, default=20)
    parseur.add_argument("--points", type=int, default=150)
    parseur.add_argument("--limite", type=int, default=None, help="pour tester sur quelques coureurs")
    args = parseur.parse_args()

    coureurs = pd.read_csv(RACINE / "data" / "coureurs.csv")
    if args.limite:
        coureurs = coureurs.head(args.limite)

    X, lignes, problemes = [], [], []
    for c in coureurs.itertuples():
        try:
            brut = lire_marqueurs(args.json / str(c.sub_id) / c.filename)
            hauteur_pied = brut[PIED_DROIT, :, AXE_VERTICAL].mean(axis=0)
            marqueurs = centrer_et_mettre_a_l_echelle(brut, c.Height)
            foulees = foulees_du_milieu(decouper_foulees(marqueurs, hauteur_pied, c.hz_r), args.n_foulees)
            if not foulees:
                raise ValueError("aucune foulée détectée")
        except Exception as erreur:
            problemes.append((c.sub_id, str(erreur)))
            continue
        for numero, foulee in enumerate(foulees):
            f = normaliser_foulee(foulee, args.points)            # (28, points, 3)
            X.append(f.transpose(0, 2, 1).reshape(84, args.points).astype(np.float32))
            lignes.append({"sub_id": c.sub_id, "label": c.label, "blesse": c.blesse, "foulee": numero})

    sortie = RACINE / "data" / "features"
    sortie.mkdir(parents=True, exist_ok=True)
    np.save(sortie / "X_foulees.npy", np.stack(X))
    meta = pd.DataFrame(lignes)
    meta.to_csv(sortie / "foulees.csv", index=False)

    par_coureur = meta.groupby("sub_id").size()
    print(f"{len(X)} foulées pour {meta.sub_id.nunique()} coureurs "
          f"(de {par_coureur.min()} à {par_coureur.max()} par coureur)")
    print(f"Forme de X : {np.stack(X).shape}")
    if problemes:
        print(f"{len(problemes)} coureurs écartés :", problemes[:10])


if __name__ == "__main__":
    main()
