# %%
import json
import pandas as pd

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"

select = pd.read_csv("../data/coureurs.csv")

# %%
def explore_json(data, level=0, name="root"):
    indent = "    " * level

    if isinstance(data, dict):
        print(f"{indent}{name} : dict ({len(data)} clés)")

        for key, value in data.items():
            explore_json(value, level + 1, key)

    elif isinstance(data, list):
        print(f"{indent}{name} : list ({len(data)} éléments)")

        if len(data) > 0:
            # On explore uniquement le premier élément
            explore_json(data[0], level + 1, "[0]")

    else:
        print(f"{indent}{name} : {type(data).__name__} = {data}")


# %%
# visualisation de la position des marqueurs sur les sujets

with open(folder_path + "100008/20110301T161801.json", "r", encoding="utf-8") as f:
    data = json.load(f)

explore_json(data)


# %%
def open_json(idx):
    coureur = select["sub_id"][idx]
    filename = select["filename"][idx]
    
    with open(folder_path + f"{coureur}/{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

init1 = open_json(1)["running"].keys()
init2 = open_json(2)["running"].keys()

for idx in range(2,len(select)):
    print(idx)
    data = open_json(idx)
    cles = data["running"].keys()
    if cles != init1 and cles != init2:
        print("ici pas la même structure")

# toutes les données ont presque la meme structure, seule différence : certains on les marqueurs des doigts de pieds et d'autres non.
# Comme on ne veut pas se séparer de la moitié des données, on décide d'ignorer les canaux des doigts de pied pour tout le monde

# %%
