# %%
import json

folder_path = "/home/charles/Téléchargements/données/ric_data/reformat_data/"



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
