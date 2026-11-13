# %%
import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text
import numpy as np
from scipy.signal import find_peaks, savgol_filter

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"

select = pd.read_csv("../data/intermediaire/meta_clean.csv")


#%%
#visualisation des coordonnées d'un marqueur pendant une course

idx_JSON = 10

coureur = select["sub_id"][idx_JSON]
filename = select["filename"][idx_JSON]
with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
    data = json.load(f)

serie = data["running"]


#%%

fs = 200  # fréquence d'échantillonnage

def detecter_foulée(serie):
    # Coordonnée Y moyenne des 4 marqueurs du pied
    y = np.mean([np.asarray(serie[f"R_foot_{i}"])[:, 1] for i in range(1, 5)], axis=0)

    # Lissage léger pour limiter les petites fluctuations
    y_smooth = savgol_filter(y, 21, 3)

    # Recherche des minima (à adapter après observation)
    minima, properties = find_peaks(-y_smooth,distance=int(0.6 * fs))

    return y, y_smooth, minima


fig, ax = plt.subplots()

y, y_smooth, minima = detecter_foulée(serie)

t = np.arange(len(y)) / fs

ax.plot(t, y, alpha=0.4, label="Signal brut")
ax.plot(t, y_smooth, label="Signal lissé")
ax.plot(t[minima], y_smooth[minima], "ro", label="Minima détectés")

ax.set_xlabel("Temps (secondes)")
ax.set_ylabel("Coordonnée Y")
ax.legend()
ax.grid()

plt.tight_layout()
plt.show()



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


foulees = decouper_foulees(serie, minima)

fig, ax = plt.subplots()
for foulee in foulees:
    y = foulee["R_foot_1"][:,1]
    ax.plot(range(len(y)), y)

ax.set_xlabel("Temps (secondes)")
ax.set_ylabel("Coordonnée Y")
ax.grid()


#%%

def normaliser_foulee(foulee, n_frames=150):

    foulee_normalisee = {}

    for nom, signal in foulee.items():
        signal = np.asarray(signal, dtype=np.float32)

        ancienne_taille = len(signal)

        # Axe temporel initial et axe temporel cible
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


foulees_normalisees = [normaliser_foulee(f) for f in foulees]

fig, ax = plt.subplots()
for foulee in foulees_normalisees:
    y = foulee["R_foot_1"][:,1]
    ax.plot(range(len(y)), y)

ax.set_xlabel("Temps (secondes)")
ax.set_ylabel("Coordonnée Y")
ax.grid()


# %%



# %%
