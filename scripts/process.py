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
    y = np.mean([np.asarray(serie[f"R_foot_{i}"])[:, 1] for i in range(1, 5)], axis=0)

    # Lissage léger pour limiter les petites fluctuations
    y_smooth = savgol_filter(y, 21, 3)

    # Recherche des minima (à adapter après observation)
    minima, properties = find_peaks(-y_smooth,distance=int(0.6 * fs))

    return y, y_smooth, minima


#%%

def decouper_foulees(serie, minima):

    minima = np.asarray(minima, dtype=int)

    # Conversion des séries en tableaux NumPy
    marqueurs = {nom: np.asarray(signal, dtype=np.float32) for nom, signal in serie.items()}

    # Découpage des foulées
    foulees = []

    for debut, fin in zip(minima[:-1], minima[1:]):
        foulee = {nom: signal[debut:fin].copy() for nom, signal in marqueurs.items()}
        foulees.append(foulee)

    return foulees


#%%

def normaliser_foulee(foulee, n_frames=150):

    foulee_normalisee = {}

    for nom, signal in foulee.items():
        signal = np.asarray(signal, dtype=np.float32)

        ancienne_taille = len(signal)

        # Axe temporel initial et axe temporel cible : meme début, meme fin, mais tailles différentes
        ancien_temps = np.linspace(0, 1, ancienne_taille)
        nouveau_temps = np.linspace(0, 1, n_frames)

        # Interpolation indépendante pour X, Y et Z
        signal_interpole = np.stack([
            np.interp(
                nouveau_temps,
                ancien_temps,
                signal[:, axe]
            )
            for axe in range(3)
        ], axis=1)

        foulee_normalisee[nom] = signal_interpole

    return foulee_normalisee


# %%

def foulees_vers_array(foulees_normalisees):
    """
    Retourne un tableau de forme :
    (nombre_foulees, 30, 200, 3)
    """

    resultats = []

    for foulee in foulees_normalisees:

        # Empilement dans un ordre toujours identique
        marqueurs = [foulee[nom] for nom in foulee.keys()]

        resultats.append(np.stack(marqueurs))

    return np.asarray(resultats, dtype=np.float32)


# %%

def process_coureur(idx, graph = False):

    coureur = select["sub_id"][idx]
    filename = select["filename"][idx]
    
    with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    serie = data["running"]

    fs = select["hz_r"][idx]
    y, y_smooth, minima = detecter_foulée(serie, fs)

    foulees = decouper_foulees(serie, minima)

    foulees_normalisees = [normaliser_foulee(f) for f in foulees]

    X_coureur = foulees_vers_array(foulees_normalisees)

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
            y = foulee["R_foot_1"][:,1]
            ax.plot(range(len(y)), y)

        ax.set_xlabel("Temps (secondes)")
        ax.set_ylabel("Coordonnée Y")
        ax.grid()


        fig, ax = plt.subplots()
        for foulee in foulees_normalisees:
            y = foulee["R_foot_1"][:,1]
            ax.plot(range(len(y)), y)

        ax.set_xlabel("Temps (secondes)")
        ax.set_ylabel("Coordonnée Y")
        ax.grid()

    print(f"taille finale des données du coureur : {X_coureur.shape}")

    
# %%
