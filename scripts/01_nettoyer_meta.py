"""Étape 1 : nettoie les métadonnées de course et choisit une séance par coureur.

Entrée : data/brut/run_data_meta.csv (fichier Figshare, contrôlé par MD5)
Sortie : data/intermediaire/meta_clean.csv
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
ENTREE = RACINE / "data" / "brut" / "run_data_meta.csv"
SORTIE = RACINE / "data" / "intermediaire" / "meta_clean.csv"
MD5_ATTENDU = "63d779c59fa8133865f61f632c403c36"

BORNES = {"age": (10, 90), "Height": (130, 220), "Weight": (30, 200)}


def normaliser(serie):
    return serie.str.lower().str.strip()


def attribuer_label(d):
    """Applique la définition « non blessé » et les regroupements du README des auteurs."""
    spec = normaliser(d["SpecInjury"]).replace(
        {"pfps": "patellofemoral pain syndrome", "itbs": "itb syndrome"}
    )
    joint = normaliser(d["InjJoint"].fillna(""))
    sain = (
        (normaliser(d["InjDefn"]) == "no injury")
        & joint.isin(["", "no injury", "no injury,no injury"])
        & (spec.isna() | (spec == "no injury"))
    )
    return np.select(
        [sain, spec == "patellofemoral pain syndrome", spec == "itb syndrome"],
        ["sain", "PFPS", "ITBS"],
        default="autre",
    )


def main():
    md5 = hashlib.md5(ENTREE.read_bytes()).hexdigest()
    if md5 != MD5_ATTENDU:
        raise ValueError(f"{ENTREE.name} diffère de la version Figshare (MD5 {md5})")

    d = pd.read_csv(ENTREE)
    print(f"Séances brutes : {len(d)} | coureurs : {d.sub_id.nunique()}")

    d["label"] = attribuer_label(d)
    d["date"] = pd.to_datetime(d["datestring"])

    # Valeurs impossibles -> manquantes.
    for col, (mini, maxi) in BORNES.items():
        d.loc[~d[col].between(mini, maxi), col] = np.nan
    d["Gender"] = d["Gender"].replace({"Unknown": np.nan})
    d["DominantLeg"] = d["DominantLeg"].replace({"Ambidextrous": np.nan})
    d["InjSide"] = d["InjSide"].replace({"Bi-lateral": "Bilateral"})

    retenues = d[d["label"] != "autre"]

    # Diagnostics contradictoires entre séances : coureur retiré.
    nb_labels = retenues.groupby("sub_id")["label"].nunique()
    ambigus = nb_labels[nb_labels > 1].index
    retenues = retenues[~retenues["sub_id"].isin(ambigus)]

    # Première séance de chaque coureur. On garde la ligne entière, pour que toutes
    # les colonnes proviennent bien de la même séance.
    multi = int((retenues.groupby("sub_id").size() > 1).sum())
    m = (
        retenues.sort_values(["date", "filename"])
        .drop_duplicates("sub_id")
        .sort_values("sub_id")
        .copy()
    )

    # Le fichier brut indique souvent un côté blessé chez les sains : valeur sans objet.
    m.loc[m["label"] == "sain", ["InjSide", "InjDuration"]] = np.nan

    # Drapeaux pour les analyses de sensibilité.
    autres = d.loc[d["label"] == "autre", ["sub_id", "date"]]
    premier_autre = autres.groupby("sub_id")["date"].min()
    m["antecedent_autre_blessure"] = (m["date"] > m["sub_id"].map(premier_autre)).astype(int)
    secondaire = normaliser(m["SpecInjury2"].fillna(""))
    m["blessure_secondaire"] = secondaire.where(~secondaire.isin(["", "no injury"]), "")

    # Imputation : médiane par sexe.
    m["annee"] = m["date"].dt.year
    m["IMC"] = m["Weight"] / (m["Height"] / 100) ** 2
    m["gabarit_impute"] = m[["Height", "Weight"]].isna().any(axis=1).astype(int)
    m["jambe_dominante_imputee"] = m["DominantLeg"].isna().astype(int)
    for col in ["age", "Height", "Weight", "IMC"]:
        m[col] = m[col].fillna(m.groupby("Gender")[col].transform("median"))
    m["DominantLeg"] = m["DominantLeg"].fillna("Right")

    colonnes = [
        "sub_id", "filename", "datestring", "annee", "label", "speed_r", "age",
        "Height", "Weight", "IMC", "Gender", "DominantLeg", "InjSide", "InjDuration",
        "blessure_secondaire", "antecedent_autre_blessure", "gabarit_impute",
        "jambe_dominante_imputee",
    ]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    m[colonnes].to_csv(SORTIE, index=False)

    print(f"Coureurs au diagnostic contradictoire retirés : {len(ambigus)}")
    print(f"Coureurs retenus avec plusieurs séances (première gardée) : {multi}")
    print(f"Retenus : {len(m)} | {m['label'].value_counts().to_dict()}")
    print(f"Gabarit imputé : {m['gabarit_impute'].sum()} | "
          f"jambe dominante imputée : {m['jambe_dominante_imputee'].sum()}")
    print(f"Antécédent d'autre blessure : {m.groupby('label')['antecedent_autre_blessure'].sum().to_dict()}")
    print(f"Blessure secondaire : {(m['blessure_secondaire'] != '').groupby(m['label']).sum().to_dict()}")
    print(f"Écrit : {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
