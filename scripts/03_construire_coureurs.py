"""Étape 3 : assemble coureurs.csv, plis.csv et le dictionnaire des variables.

Entrées : data/intermediaire/meta_clean.csv, data/intermediaire/dv_r_brut.csv
Sorties : data/coureurs.csv, data/plis.csv, data/dictionnaire_variables.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
INTER = RACINE / "data" / "intermediaire"
SORTIE = RACINE / "data"
GRAINE = 2026
N_PLIS, N_REPETITIONS = 5, 5
SEUIL_MAD = 8  # écart robuste au-delà duquel une valeur d'angle est jugée impossible

# Nom dans dv_r -> (famille, description, unité). Ordre = lignes 2 à 77 de gait_steps.m.
VARIABLES = {
    "STEP_WIDTH": ("foulée", "Largeur de pas (écart latéral entre les talons)", "m"),
    "STRIDE_RATE": ("foulée", "Cadence", "foulées/min"),
    "STRIDE_LENGTH": ("foulée", "Longueur de foulée", "m"),
    "SWING_TIME": ("foulée", "Temps d'oscillation (pied en l'air)", "s"),
    "STANCE_TIME": ("foulée", "Temps d'appui", "s"),
    "PELVIS_PEAK_DROP_ANGLE": ("bassin", "Pic de chute du bassin (signe inversé à droite, convention des auteurs)", "°"),
    "PELVIS_DROP_EXCURSION": ("bassin", "Amplitude de chute du bassin, du contact au pic (signe inversé à droite)", "°"),
    "ANKLE_DF_PEAK_ANGLE": ("cheville", "Pic de dorsiflexion", "°"),
    "ANKLE_EVE_PEAK_ANGLE": ("cheville", "Pic d'éversion (pronation)", "°"),
    "ANKLE_EVE_percent_STANCE": ("cheville", "Moment du pic d'éversion", "fraction de l'appui (0-1)"),
    "ANKLE_EVE_EXCURSION": ("cheville", "Amplitude d'éversion, du contact au pic", "°"),
    "ANKLE_ROT_PEAK_ANGLE": ("cheville", "Pic de rotation du pied par rapport au tibia", "°"),
    "ANKLE_ROT_EXCURSION": ("cheville", "Amplitude de rotation du pied", "°"),
    "KNEE_FLEX_PEAK_ANGLE": ("genou", "Pic de flexion du genou (valeur négative = flexion)", "°"),
    "KNEE_ADD_PEAK_ANGLE": ("genou", "Pic d'adduction du genou (varus)", "°"),
    "KNEE_ADD_EXCURSION": ("genou", "Amplitude d'adduction du genou", "°"),
    "KNEE_ABD_PEAK_ANGLE": ("genou", "Pic d'abduction du genou (valgus)", "°"),
    "KNEE_ABD_EXCURSION": ("genou", "Amplitude d'abduction du genou", "°"),
    "KNEE_ROT_PEAK_ANGLE": ("genou", "Pic de rotation du tibia sous le fémur", "°"),
    "KNEE_ROT_EXCURSION": ("genou", "Amplitude de rotation du tibia", "°"),
    "HIP_EXT_PEAK_ANGLE": ("hanche", "Pic d'extension de hanche", "°"),
    "HIP_ADD_PEAK_ANGLE": ("hanche", "Pic d'adduction de hanche", "°"),
    "HIP_ADD_EXCURSION": ("hanche", "Amplitude d'adduction de hanche", "°"),
    "HIP_ROT_PEAK_ANGLE": ("hanche", "Pic de rotation de hanche", "°"),
    "HIP_ROT_EXCURSION": ("hanche", "Amplitude de rotation de hanche (souvent 0 : distribution très asymétrique)", "°"),
    "FOOT_PROG_ANGLE": ("pied", "Angle de progression du pied (moyenne 20-50 % de l'appui)", "°"),
    "FOOT_ANG_at_HS": ("pied", "Angle du pied au contact (type d'attaque)", "°"),
    "MHW_EXC_FROM_TO": ("pied", "Medial heel whip : rotation du talon après le décollement", "°"),
    "ANKLE_EVE_PEAK_VEL": ("cheville", "Vitesse maximale d'éversion", "°/s"),
    "ANKLE_ROT_PEAK_VEL": ("cheville", "Vitesse maximale de rotation du pied", "°/s"),
    "KNEE_ABD_PEAK_VEL": ("genou", "Vitesse maximale d'abduction du genou", "°/s"),
    "KNEE_ADD_PEAK_VEL": ("genou", "Vitesse maximale d'adduction du genou", "°/s"),
    "HIP_ABD_PEAK_VEL": ("hanche", "Vitesse maximale d'abduction de hanche", "°/s"),
    "KNEE_ROT_PEAK_VEL": ("genou", "Vitesse maximale de rotation du genou", "°/s"),
    "HIP_ROT_PEAK_VEL": ("hanche", "Vitesse maximale de rotation de hanche", "°/s"),
    "PRONATION_ONSET": ("cheville", "Début de pronation (entrée à 20 % du pic d'éversion)", "% de l'appui"),
    "PRONATION_OFFSET": ("cheville", "Fin de pronation (sortie des 20 % du pic d'éversion)", "% de l'appui"),
    "PEAK_HIP_ADD_VELOCITY": ("hanche", "Vitesse maximale d'adduction de hanche", "°/s"),
    "PEAK_PELVIC_DROP_VELOCITY": ("bassin", "Vitesse maximale de chute du bassin", "°/s"),
    "VERTICAL_OSCILLATION": ("foulée", "Oscillation verticale du bassin", "mm"),
}

META = {
    "sub_id": ("identifiant", "Identifiant du coureur (une ligne par coureur)", ""),
    "filename": ("identifiant", "Fichier JSON de la séance retenue (ric_data.zip)", ""),
    "datestring": ("identifiant", "Date et heure de la séance", ""),
    "label": ("cible", "Diagnostic : sain, PFPS ou ITBS", ""),
    "blesse": ("cible", "1 = PFPS ou ITBS, 0 = sain", ""),
    "speed_r": ("controle", "Vitesse de course sur tapis (= longueur x cadence / 60)", "m/s"),
    "age": ("controle", "Âge", "ans"),
    "Height": ("controle", "Taille", "cm"),
    "Weight": ("controle", "Poids", "kg"),
    "IMC": ("controle", "Indice de masse corporelle", "kg/m²"),
    "Gender": ("controle", "Sexe (Female / Male)", ""),
    "DominantLeg": ("controle", "Jambe dominante (Left / Right)", ""),
    "annee": ("confusion", "Année d'enregistrement : très liée au label, à ne pas donner au modèle", ""),
    "hz_r": ("confusion", "Fréquence d'acquisition (200 Hz, 4 coureurs à 120 Hz)", "Hz"),
    "InjSide": ("info_blessure", "Côté blessé (vide chez les sains) : NE PAS utiliser comme variable", ""),
    "InjDuration": ("info_blessure", "Durée de la blessure (vide chez les sains) : NE PAS utiliser comme variable", "jours"),
    "blessure_secondaire": ("info_blessure", "Diagnostic secondaire déclaré (texte libre) : NE PAS utiliser comme variable", ""),
    "antecedent_autre_blessure": ("qualite", "1 = une séance antérieure avec une autre blessure", ""),
    "gabarit_impute": ("qualite", "1 = taille ou poids imputé (médiane par sexe)", ""),
    "jambe_dominante_imputee": ("qualite", "1 = jambe dominante manquante, mise à Right", ""),
    "qualite_suspecte": ("qualite", "1 = angles physiquement impossibles (échec probable du calcul)", ""),
}


def plis_stratifies(labels, rng):
    """Attribue un pli 1..N_PLIS à chaque coureur, en équilibrant chaque classe."""
    plis = np.empty(len(labels), dtype=int)
    for classe in np.unique(labels):
        idx = rng.permutation(np.flatnonzero(labels == classe))
        decalage = rng.integers(N_PLIS)
        plis[idx] = (np.arange(len(idx)) + decalage) % N_PLIS + 1
    return plis


def main():
    meta = pd.read_csv(INTER / "meta_clean.csv")
    dv = pd.read_csv(INTER / "dv_r_brut.csv")
    x = meta.merge(dv, on=["sub_id", "filename"], how="left", validate="1:1").copy()

    colonnes_dv = [c for c in dv.columns if c[:2] in ("L_", "R_")]
    vides = [c for c in colonnes_dv if (x[c].fillna(0) == 0).all()]
    noms = list(dict.fromkeys(c[2:] for c in colonnes_dv if c not in vides))
    if noms != list(VARIABLES):
        raise ValueError(f"Variables dv_r inattendues : {sorted(set(noms) ^ set(VARIABLES))}")
    if not (x["L_STEP_WIDTH"] == x["R_STEP_WIDTH"]).all():
        raise ValueError("STEP_WIDTH diffère entre gauche et droite")

    x["STEP_WIDTH"] = x["L_STEP_WIDTH"]
    cinematique = ["STEP_WIDTH"] + [
        f"{cote}_{nom}" for cote in ("L", "R") for nom in VARIABLES if nom != "STEP_WIDTH"
    ]

    # Angles impossibles : on signale le coureur sans modifier ses valeurs.
    angles = [c for c in cinematique if c.endswith(("PEAK_ANGLE", "EXCURSION")) and "HIP_ROT_EXC" not in c]
    ecart = (x[angles] - x[angles].median()).abs()
    z = ecart / (ecart.median() * 1.4826)
    x["qualite_suspecte"] = (z > SEUIL_MAD).any(axis=1).astype(int)
    x["blesse"] = (x["label"] != "sain").astype(int)

    colonnes = list(META) + cinematique
    coureurs = x[colonnes].sort_values("sub_id")
    coureurs.to_csv(SORTIE / "coureurs.csv", index=False)

    rng = np.random.default_rng(GRAINE)
    plis = pd.DataFrame({"sub_id": coureurs["sub_id"].to_numpy(), "label": coureurs["label"].to_numpy()})
    for r in range(1, N_REPETITIONS + 1):
        plis[f"rep{r}"] = plis_stratifies(plis["label"].to_numpy(), rng)
    plis.to_csv(SORTIE / "plis.csv", index=False)

    lignes = []
    for nom, (role, description, unite) in META.items():
        lignes.append({"variable": nom, "role": role, "famille": "", "cote": "",
                       "description": description, "unite": unite, "ligne_gait_steps": ""})
    rang = {nom: i + 2 for i, nom in enumerate(VARIABLES)}
    for col in cinematique:
        cote, nom = ("", col) if col == "STEP_WIDTH" else (col[0], col[2:])
        famille, description, unite = VARIABLES[nom]
        lignes.append({"variable": col, "role": "cinematique", "famille": famille,
                       "cote": {"L": "gauche", "R": "droite"}.get(cote, "les deux"),
                       "description": description, "unite": unite,
                       "ligne_gait_steps": rang[nom]})
    pd.DataFrame(lignes).to_csv(SORTIE / "dictionnaire_variables.csv", index=False)

    # Contrôles finaux.
    assert coureurs["sub_id"].is_unique and len(coureurs) == len(meta)
    assert coureurs[cinematique].notna().all(axis=1).sum() >= len(coureurs) - 4
    print(f"Colonnes dv_r vides retirées : {len(vides)} | variables cinématiques : {len(cinematique)}")
    print(f"coureurs.csv : {coureurs.shape[0]} lignes x {coureurs.shape[1]} colonnes")
    print(f"Labels : {coureurs['label'].value_counts().to_dict()} | blessés : {coureurs['blesse'].sum()}")
    print(f"Qualité suspecte : {coureurs.loc[coureurs['qualite_suspecte'] == 1, 'sub_id'].tolist()}")
    print(f"Valeurs manquantes : {coureurs[cinematique].isna().sum()[lambda s: s > 0].to_dict()}")
    print("Effectifs par pli (rep1) :")
    print(pd.crosstab(plis["rep1"], plis["label"]).to_string())


if __name__ == "__main__":
    main()
