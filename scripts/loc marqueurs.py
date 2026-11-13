# %%
import json
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"

select = pd.read_csv("../data/intermediaire/meta_clean.csv")


# %%
# visualisation de la position des marqueurs sur les sujets

with open(folder_path + "100008/20110301T161801.json", "r", encoding="utf-8") as f:
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


fig, axes = plt.subplots(1, 2, figsize=(7, 7))

# Vue de face : X / Y
ax = axes[0]
ax.plot(x, y, ".")
texts = [ax.text(x[i], y[i], label, fontsize=7) for i, label in enumerate(labels)]
adjust_text(texts,ax=ax,arrowprops=dict(arrowstyle="->", color="red"))
ax.set_title("Vue X / Y")
ax.set_aspect("equal")

# Vue de côté : Z / Y
ax = axes[1]
ax.plot(z, y, ".")
texts = [ax.text(z[i], y[i], label, fontsize=7) for i, label in enumerate(labels)]
adjust_text(texts,ax=ax,arrowprops=dict(arrowstyle="->", color="red"))
ax.set_title("Vue Z / Y")
ax.set_aspect("equal")

plt.tight_layout()
plt.show()
# %%
