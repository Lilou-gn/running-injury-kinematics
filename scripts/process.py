# %%
import json
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from charte_graphique import appliquer_charte, COULEURS_GROUPES, titrer, sauver_figure
from pathlib import Path

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"
BASE_DIR = Path(__file__).resolve().parent
select = pd.read_csv(BASE_DIR.parent/"data/coureurs.csv")
appliquer_charte()

canaux = ['pelvis_1', 'pelvis_2', 'pelvis_3', 'pelvis_4', 
          'L_thigh_1', 'L_thigh_2', 'L_thigh_3', 'L_thigh_4', 
          'R_thigh_1', 'R_thigh_2', 'R_thigh_3', 'R_thigh_4', 
          'L_shank_1', 'L_shank_2', 'L_shank_3', 'L_shank_4', 
          'R_shank_1', 'R_shank_2', 'R_shank_3', 'R_shank_4', 
          'L_foot_1', 'L_foot_2', 'L_foot_3', 'L_foot_4', 
          'R_foot_1', 'R_foot_2', 'R_foot_3', 'R_foot_4']


#%%

def detecter_foulée(serie, fs):
    # Coordonnée Y moyenne des 4 marqueurs du pied
    y = np.mean(serie[24:28,:,1], axis=0)

    # Lissage léger pour limiter les petites fluctuations (ne sera pas sauvegardée, sert uniquement à la recherche des minima)
    y_smooth = savgol_filter(y, 21, 3)

    # Recherche des minima
    minima, properties = find_peaks(-y_smooth,distance=int(0.6 * fs))

    return y, y_smooth, minima


#%%

def normaliser_foulee(foulee, n_frames=150):

    ancienne_taille = np.shape(foulee)[1]

    foulee_normalisee = np.zeros((28, n_frames, 3))

    for i in range(28): #itérer sur les canaux
        for j in range(3): #itérer sur les axes
            foulee_normalisee[i, :, j] = np.interp(
                range(n_frames), 
                range(ancienne_taille), 
                foulee[i, :, j])

    return foulee_normalisee


# %%

def normaliser_par_bassin(foulee):

    # Centre du bassin à chaque frame : (150, 3)
    centre_bassin = np.mean(foulee[:4],axis=0)

    # Soustraction du centre à tous les marqueurs
    foulee_normalisee = foulee - centre_bassin[None, :, :]

    return foulee_normalisee

#%%

def load_coureur(idx):
    coureur = select["sub_id"][idx]
    filename = select["filename"][idx]
    
    with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    canaux = data["running"]
    list_canaux = list(canaux.values())[:28] # on a vu précédemment que les canaux étaient tous dans le meme ordre et que les 28 premiers étaient tout le temps présent
    data_table = np.asarray(list_canaux)

    return data_table


def show_coureur(data_table):
    x = list(range(data_table.shape[1]))
    for i in range(28):
        fig, (ax1, ax2, ax3) = plt.subplots(3,1)
        fig.suptitle(canaux[i])
        ax1.plot(x, data_table[i, :, 0])
        ax1.set_title("coord X (droite/gauche)")
        ax2.plot(x, data_table[i, :, 1])
        ax2.set_title("coord Y (haut/bas)")
        ax3.plot(x, data_table[i, :, 2])
        ax3.set_title("coord Z (avant/arrière)")
        fig.tight_layout()


#%%

def process_coureur(idx, graph = False):

    data_table = load_coureur(idx)
    # on a bien un tableau de taille 28*4000*3

    fs = select["hz_r"][idx]
    y, y_smooth, minima = detecter_foulée(data_table, fs)

    foulees = [data_table[:,debut:fin,:] for debut, fin in zip(minima[:-1], minima[1:])]

    foulees_normalisees = [normaliser_foulee(f) for f in foulees]

    foulees_normalisees_bassin = [normaliser_par_bassin(f) for f in foulees_normalisees]

    if graph:
        fig, ax = plt.subplots()
        t = np.arange(len(y)) / fs

        ax.plot(t, y, alpha=0.4)
        ax.plot(t, y_smooth)
        ax.plot(t[minima], y_smooth[minima], "ro", label="Minima\n détectés")

        ax.set_xlabel("Temps (frames)")
        ax.set_ylabel("Coordonnée Y")
        ax.legend(bbox_to_anchor=(1, 1))
        ax.grid()
        fig.tight_layout()
        sauver_figure(fig, "serie_complete_pied_Y")

        fig, ax = plt.subplots()
        for foulee in foulees:
            pied = foulee[24, : , 1] #24 = canal R_foot_1
            ax.plot(range(len(pied)), pied)
        ax.set_xlabel("Temps (frames)")
        ax.set_ylabel("Coordonnée Y")
        ax.grid()

        fig.tight_layout()
        sauver_figure(fig, "foulees_decoupes_simple")


        fig, (ax2, ax1) = plt.subplots(2,1)
        for foulee in foulees_normalisees:
            pied = foulee[24, : , 1] #24 = canal R_foot_1
            bassin = np.mean(foulee[:4, :, 1],axis=0)
            ax1.plot(range(len(bassin)), bassin)
            ax2.plot(range(len(pied)), pied)

        ax1.set_xlabel("Temps (frames)")
        ax1.set_ylabel("Coordonnée Y")
        ax1.set_title("Position du bassin")
        ax1.grid()

        ax2.set_xlabel("Temps (frames)")
        ax2.set_ylabel("Coordonnée Y")
        ax2.set_title("Position du pied droit")
        ax2.grid()

        fig.tight_layout()
        sauver_figure(fig, "foulees_normalisees")


        fig, (ax2, ax1) = plt.subplots(2,1)
        for foulee in foulees_normalisees_bassin:
            pied = foulee[24, : , 1] #24 = canal R_foot_1
            bassin = np.mean(foulee[:4, :, 1],axis=0)
            ax1.plot(range(len(bassin)), bassin)
            ax2.plot(range(len(pied)), pied)

        ax1.set_xlabel("Temps (frames)")
        ax1.set_ylabel("Coordonnée Y")
        ax1.set_title("Position du bassin (normalisée)")
        ax1.grid()

        ax2.set_xlabel("Temps (frames)")
        ax2.set_ylabel("Coordonnée Y")
        ax2.set_title("Position du pied droit (normalisée)")
        ax2.grid()

        fig.tight_layout()
        sauver_figure(fig, "foulees_normalisees_bassin")

    return foulees_normalisees_bassin

#%%

"""
# code pour controler la bonne réalisation du pré-processing avant de sauvegarder
nb_foulees = 0
for i in range(587):
    coureur = process_coureur(i)
    print(f"{i} : {len(coureur)} foulées de {coureur[0].shape}")
    nb_foulees += len(coureur)

print(f"nombre total de foulées : {nb_foulees}")
# on a désormais 26361 observations
"""

# %%

process_coureur(105, graph=True)


X = []
y = []
groups = []

for i in range(587):

    print(i)
    coureur = process_coureur(i)
    classe = select["label"][i]

    if np.max(np.abs(coureur))>1e4: #élimination des coureurs aux valeurs aberantes (problème de récolte des données)
        print("skip")
        pass

    else:
        for foulee in coureur:

            # (28, 150, 3) -> (84, 150)
            foulee = np.asarray(foulee, dtype=np.float32)
            foulee = foulee.transpose(0, 2, 1)
            foulee = foulee.reshape(84, 150)

            X.append(foulee)
            y.append(classe)
            groups.append(i)

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y)
groups = np.asarray(groups)

print(X.shape)
print(y.shape, np.unique(y))
print(groups.shape)

np.save("../data/features/foulee.npy", X)
np.save("../data/features/label_foulee.npy", y)
np.save("../data/features/coureur_foulee.npy", groups)

# %%
fig, ax = plt.subplots()
ax.plot(load_coureur(10)[24,:,1], label = "coureur 1")
ax.plot(load_coureur(500)[24,:,1], label = "coureur 2")
ax.set_ylabel("Coordonnée Y du pied droit")
ax.set_xlabel("Temps (frames)")
titrer(fig, "Comparaison des séries de deux coureurs")
ax.legend()
fig.tight_layout()
titrer(fig, "Les séries sont différentes en taille et en valeurs d'un coureur à un autre")
sauver_figure(fig, "comparaison_series")

# %%

data_table = load_coureur(10)
x = np.arange(data_table.shape[1])

fig, axes = plt.subplots(3, 1, figsize=(6.4, 6.8), sharex=True)
fig.subplots_adjust(left=0.16, right=0.96, top=0.81, bottom=0.11, hspace=0.45)
for coord, (ax, titre) in enumerate(zip(axes, (
    "X · Droite / gauche",
    "Y · Haut / bas",
    "Z · Avant / arrière",
))):
    ax.plot(x, data_table[8, :, coord])
    ax.set_title(titre)

axes[-1].set_xlabel("Temps (images)")
titrer(fig, "Trois coordonnées pour un marqueur", "Exemple sur la cuisse droite",
       legende="Source : Running Injury Clinic Kinematic Dataset.")
sauver_figure(fig, "representation_series_brut", taille_slide=fig.get_size_inches())
# %%
