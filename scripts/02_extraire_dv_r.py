"""Étape 2 : extrait dv_r pour les coureurs retenus, sans stocker l'archive de 22,7 Go.

Par défaut, seules les portions utiles de ric_data.zip sont lues sur Figshare (environ
6 Go transférés). L'extraction reprend là où elle s'est arrêtée si on la relance.

Entrée : data/intermediaire/meta_clean.csv
Sortie : data/intermediaire/dv_r_brut.csv

Options :
  --zip CHEMIN           lit une copie locale de ric_data.zip au lieu de Figshare
  --garder-json DOSSIER  conserve aussi les JSON (environ 13 Go), utile pour recalculer
                         les courbes d'angles
"""
import argparse
import csv
import io
import json
import struct
import time
import urllib.error
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import inflate64  # l'archive est en Deflate64, que zipfile ne sait pas décompresser
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
ENTREE = RACINE / "data" / "intermediaire" / "meta_clean.csv"
SORTIE = RACINE / "data" / "intermediaire" / "dv_r_brut.csv"
URL = "https://ndownloader.figshare.com/files/42651352"
TAILLE = 22749955646
ESSAIS = 12


def lire_plage_http(debut, fin):
    requete = urllib.request.Request(
        URL, headers={"Range": f"bytes={debut}-{fin}", "User-Agent": "running-injury-kinematics"}
    )
    for essai in range(ESSAIS):
        try:
            with urllib.request.urlopen(requete, timeout=180) as reponse:
                if reponse.status != 206:
                    raise RuntimeError(f"Lecture partielle refusée (HTTP {reponse.status})")
                return reponse.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as erreur:
            if essai == ESSAIS - 1:
                raise
            print(f"  réseau ({erreur}), nouvel essai", flush=True)
            time.sleep(min(5 * (essai + 1), 30))


class ZipDistant(io.RawIOBase):
    """Fichier en lecture seule adossé à des requêtes HTTP Range."""

    def __init__(self):
        self.position = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, decalage, origine=0):
        base = {0: 0, 1: self.position, 2: TAILLE}[origine]
        self.position = base + decalage
        return self.position

    def readinto(self, tampon):
        if self.position >= TAILLE or len(tampon) == 0:
            return 0
        fin = min(TAILLE, self.position + len(tampon)) - 1
        donnees = lire_plage_http(self.position, fin)
        tampon[: len(donnees)] = donnees
        self.position += len(donnees)
        return len(donnees)


def decompresser(info, brut):
    if info.compress_type == 9:
        donnees = inflate64.Inflater().inflate(brut)
    elif info.compress_type == 8:
        donnees = zlib.decompress(brut, -15)
    elif info.compress_type == 0:
        donnees = brut
    else:
        raise ValueError(f"Compression {info.compress_type} non gérée")
    if zlib.crc32(donnees) != info.CRC:
        raise ValueError(f"Somme de contrôle incorrecte : {info.filename}")
    return donnees


def lire_entree(info, lire_plage):
    # En-tête local : 30 octets + nom + champ extra, de longueur variable.
    marge = 1024
    fin = min(TAILLE, info.header_offset + 30 + marge + info.compress_size) - 1
    bloc = lire_plage(info.header_offset, fin)
    nom, extra = struct.unpack("<HH", bloc[26:30])
    debut = 30 + nom + extra
    brut = bloc[debut : debut + info.compress_size]
    if len(brut) != info.compress_size:
        raise ValueError(f"Lecture incomplète : {info.filename}")
    return decompresser(info, brut)


def extraire(ligne, info, lire_plage, dossier_json):
    donnees = lire_entree(info, lire_plage)
    if dossier_json:
        chemin = dossier_json / str(ligne.sub_id) / ligne.filename
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(donnees)
    contenu = json.loads(donnees)
    dv = contenu.get("dv_r") or {}
    sortie = {
        "sub_id": ligne.sub_id,
        "filename": ligne.filename,
        "hz_r": contenu.get("hz_r"),
        "n_images": max((len(v) for v in (contenu.get("running") or {}).values()), default=0),
    }
    for cote, prefixe in (("left", "L_"), ("right", "R_")):
        for nom, valeur in (dv.get(cote) or {}).items():
            sortie[prefixe + nom] = valeur
    return sortie


def main():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--zip", type=Path)
    parseur.add_argument("--garder-json", type=Path)
    parseur.add_argument("--workers", type=int, default=4)
    args = parseur.parse_args()

    meta = pd.read_csv(ENTREE)
    deja_faits = pd.read_csv(SORTIE).to_dict("records") if SORTIE.exists() else []
    faits = {r["sub_id"] for r in deja_faits}
    a_faire = [l for l in meta.itertuples() if l.sub_id not in faits]
    print(f"Coureurs : {len(meta)} | déjà extraits : {len(faits)} | à faire : {len(a_faire)}", flush=True)

    if args.zip:
        def lire_plage(debut, fin):
            with open(args.zip, "rb") as f:
                f.seek(debut)
                return f.read(fin - debut + 1)

        archive = zipfile.ZipFile(args.zip)
    else:
        lire_plage = lire_plage_http
        archive = zipfile.ZipFile(io.BufferedReader(ZipDistant(), 1 << 20))

    index = {i.filename.replace(chr(92), "/"): i for i in archive.infolist()}

    lignes = list(deja_faits)
    echecs = []
    debut = time.time()

    def sauvegarder():
        if not lignes:
            return
        colonnes = list(dict.fromkeys(c for r in lignes for c in r))
        temporaire = SORTIE.with_suffix(".tmp")
        with open(temporaire, "w", newline="", encoding="utf-8") as f:
            ecrivain = csv.DictWriter(f, colonnes)
            ecrivain.writeheader()
            ecrivain.writerows(sorted(lignes, key=lambda r: r["sub_id"]))
        temporaire.replace(SORTIE)

    with ThreadPoolExecutor(args.workers) as pool:
        taches = {}
        for ligne in a_faire:
            info = index[f"reformat_data/{ligne.sub_id}/{ligne.filename}"]
            taches[pool.submit(extraire, ligne, info, lire_plage, args.garder_json)] = ligne
        for n, tache in enumerate(as_completed(taches), 1):
            ligne = taches[tache]
            try:
                lignes.append(tache.result())
            except Exception as erreur:  # on continue : une relance reprendra ce coureur
                echecs.append(ligne.sub_id)
                print(f"  ÉCHEC {ligne.sub_id} : {erreur}", flush=True)
            if n % 25 == 0:
                sauvegarder()
                print(f"  {n}/{len(a_faire)} en {time.time() - debut:.0f} s", flush=True)
    sauvegarder()

    print(f"Extraits : {len(lignes)} | échecs : {len(echecs)} {echecs[:20]}")
    if echecs:
        raise SystemExit("Extraction incomplète : relancer le script pour reprendre.")
    print(f"Écrit : {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
