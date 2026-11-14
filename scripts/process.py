# %%
import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
import numpy as np
from scipy.signal import find_peaks, savgol_filter

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"

select = pd.read_csv("../data/coureurs.csv")


#%%

fs = 200  # fréquence d'échantillonnage

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


def process_coureur(idx, graph = False):

    coureur = select["sub_id"][idx]
    filename = select["filename"][idx]
    
    with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    canaux = data["running"]
    list_canaux = list(canaux.values())[:28] # on a vu précédemment que les canaux étaient tous dans le meme ordre et que les 28 premiers étaient tout le temps présent
    data_table = np.asarray(list_canaux)

    # on a bien un tableau de taille 28*4000*3

    fs = select["hz_r"][idx]
    y, y_smooth, minima = detecter_foulée(data_table, fs)

    foulees = [data_table[:,debut:fin,:] for debut, fin in zip(minima[:-1], minima[1:])]

    foulees_normalisees = np.asarray([normaliser_foulee(f) for f in foulees])

    if graph:
        fig, ax = plt.subplots()
        t = np.arange(len(y)) / fs

        ax.plot(t, y, alpha=0.4, label="Signal brut")
        ax.plot(t, y_smooth, label="Signal lissé")
        ax.plot(t[minima], y_smooth[minima], "ro", label="Minima détectés")

        ax.set_xlabel("Temps (secondes)")
        ax.set_ylabel("Coordonnée Y")
        ax.legend()
        ax.grid()

        plt.tight_layout()

        fig, ax = plt.subplots()
        for foulee in foulees:
            y = foulee[24, : , 1] #24 = canal R_foot_1
            ax.plot(range(len(y)), y)

        ax.set_xlabel("Temps (secondes)")
        ax.set_ylabel("Coordonnée Y")
        ax.grid()


        fig, ax = plt.subplots()
        for foulee in foulees_normalisees:
            y = foulee[24, : , 1] #24 = canal R_foot_1
            ax.plot(range(len(y)), y)

        ax.set_xlabel("Temps (secondes)")
        ax.set_ylabel("Coordonnée Y")
        ax.grid()

    return foulees_normalisees

nb_foulees = 0
for i in range(587):
    coureur = process_coureur(i)
    print(f"{i} : {coureur.shape}")
    nb_foulees += coureur.shape[0]

print(f"nombre total d'observations : {nb_foulees}")


# %%
