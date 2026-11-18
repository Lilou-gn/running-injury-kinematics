# %%
import json
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
from pathlib import Path
from charte_graphique import appliquer_charte, COULEURS_GROUPES, titrer, sauver_figure

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/" # à modifier selon votre emplacement des données
BASE_DIR = Path(__file__).resolve().parent
select = pd.read_csv(BASE_DIR.parent/"data/coureurs.csv")
appliquer_charte()


# %%
# visualisation de la position des marqueurs sur les sujets
def localisation_marqueurs(idx):
    coureur = select["sub_id"][idx]
    filename = select["filename"][idx]
        
    with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    x = []
    y = []
    z = []
    labels = []

    for marqueur, values in data["neutral"].items():

        x.append(values[0])
        y.append(values[1])
        z.append(values[2])
        labels.append(marqueur)


    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 7))

    # Vue de face : X / Y
    ax1.plot(x, y, ".")
    texts = [ax1.text(x[i], y[i], label, fontsize=7) for i, label in enumerate(labels)]
    adjust_text(texts,ax=ax1,arrowprops=dict(arrowstyle="->", color="red"))
    ax1.set_title("Vue X / Y")
    ax1.set_aspect("equal")

    # Vue de côté : Z / Y
    ax2.plot(z, y, ".")
    texts = [ax2.text(z[i], y[i], label, fontsize=7) for i, label in enumerate(labels)]
    adjust_text(texts,ax=ax2,arrowprops=dict(arrowstyle="->", color="red"))
    ax2.set_title("Vue Z / Y")
    ax2.set_aspect("equal")

    titrer(fig, "Position des marqueurs sur l'individu au repos (en mm)", "")
    sauver_figure(fig, "loc_marqueurs")

    return data["neutral"]

localisation_marqueurs(10) #localisation des marqueurs sur le 10e coureur

# %%
