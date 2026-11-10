# Charte graphique commune du projet (ggplot2)
#
# Règles suivies :
# - cours de data visualisation (R. Mahmoud) : un message par graphe, titre-message,
#   encre proportionnelle, couleur pour distinguer ou mettre en évidence, pas de 3D,
#   légendes dans l'ordre des données, textes assez grands ;
# - « Créer un beau graphique » (C. Thompson) : couleurs qui ont un sens, différenciables
#   par tous, atténuées, contraste >= 3:1, hiérarchie typographique, police lisible,
#   annotations plutôt que légende, place pour respirer, fond qui rassemble.
#
# Usage : source("R/theme_projet.R") puis + theme_projet() et sauver_figure(p, "nom").

library(ggplot2)

# ---- Police : Atkinson Hyperlegible, conçue pour la lisibilité (amphi, basse vision) ----
police <- "sans"
if (requireNamespace("showtext", quietly = TRUE)) {
  ok <- tryCatch({
    sysfonts::font_add_google("Atkinson Hyperlegible", "atkinson")
    TRUE
  }, error = function(e) FALSE)
  if (ok) {
    showtext::showtext_auto()
    showtext::showtext_opts(dpi = 300)
    police <- "atkinson"
  }
}

# ---- Couleurs ----
# Palette « Douleur » (choisie par le groupe) : couleurs chaudes = blessure (douleur),
# gris-bleu froid = coureurs sains, qui servent de référence.
# Testée avec colorspace : écart Lab >= 22 entre chaque paire en deutéranopie,
# protanopie et tritanopie ; trois niveaux de gris distincts en noir et blanc.
# Contraste sur le fond : sain 5,2:1, PFPS 2,8:1 (compensé par les étiquettes), ITBS 9,5:1.
couleurs_groupes <- c(sain = "#5E6A77", PFPS = "#C98A1A", ITBS = "#7A1E3A")
formes_groupes <- c(sain = 21, PFPS = 22, ITBS = 24)  # redondance pour le noir et blanc

encre_titre <- "#14202E"   # titre : le plus foncé
encre_texte <- "#3F4A57"   # sous-titre, axes, annotations
encre_douce <- "#6B7580"   # légende de figure, source
fond <- "#F8F8F8"
grille <- "#E3E5E8"
# Couleur d'accent pour « pointer » un élément quand les groupes ne sont pas en jeu.
# Volontairement différente des couleurs de groupes, pour ne pas suggérer un diagnostic.
mise_en_avant <- "#14202E"

# Mot coloré dans un titre ou sous-titre (remplace la légende) : nécessite ggtext.
mot <- function(texte, couleur) sprintf("<span style='color:%s'>**%s**</span>", couleur, texte)
groupe_md <- function(g) mot(g, couleurs_groupes[[g]])

# ---- Thème ----
theme_projet <- function(base_size = 14) {
  theme_minimal(base_size = base_size, base_family = police) +
    theme(
      text = element_text(colour = encre_texte),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      # Titre en texte simple (mesure fiable de la hauteur) : couper les titres longs
      # avec un retour à la ligne explicite (\n).
      plot.title = element_text(
        size = rel(1.5), face = "bold", colour = encre_titre, lineheight = 0.95,
        margin = margin(0, 0, base_size * 0.6, 0)
      ),
      # Marge haute : compense les jambages (p, g) d'un titre sur une seule ligne,
      # que showtext ne compte pas dans la hauteur du titre.
      plot.subtitle = ggtext::element_textbox_simple(
        size = rel(1.1), colour = encre_texte, lineheight = 1.2,
        margin = margin(base_size * 0.6, 0, base_size * 1.2, 0)
      ),
      plot.caption = ggtext::element_textbox_simple(
        size = rel(0.8), colour = encre_douce, lineheight = 1.2,
        margin = margin(base_size, 0, 0, 0)
      ),
      axis.title = element_text(size = rel(1), colour = encre_texte),
      axis.title.y = element_text(margin = margin(0, base_size * 0.6, 0, 0)),
      axis.title.x = element_text(margin = margin(base_size * 0.6, 0, 0, 0)),
      axis.text = element_text(size = rel(0.95), colour = encre_texte),
      strip.text = element_text(size = rel(1.05), face = "bold", colour = encre_titre, hjust = 0),
      panel.grid.major = element_line(colour = grille, linewidth = 0.4),
      panel.grid.minor = element_blank(),
      panel.spacing = unit(base_size * 1.5, "pt"),
      legend.position = "none",
      plot.margin = margin(base_size * 1.5, base_size * 1.5, base_size, base_size * 1.5),
      plot.background = element_rect(fill = fond, colour = fond)
    )
}

# Pourcentages à la française : « 35 % ».
pourcent <- function(x, accuracy = 1) scales::percent(x, accuracy = accuracy, suffix = " %",
                                                       decimal.mark = ",")

source_donnees <-"Source : Running Injury Clinic Kinematic Dataset (Ferber et al., 2024), 587 coureurs."

# ---- Export : version notebook et version slide (16:9, textes agrandis) ----
sauver_figure <- function(p, nom, dossier = "figures/exploration", largeur = 9, hauteur = 5.5) {
  racine <- rprojroot::find_root(rprojroot::has_file("data/coureurs.csv"))
  dir.create(file.path(racine, dossier), recursive = TRUE, showWarnings = FALSE)
  dir.create(file.path(racine, "figures/slides"), recursive = TRUE, showWarnings = FALSE)
  ggsave(file.path(racine, dossier, paste0(nom, ".png")), p,
         width = largeur, height = hauteur, dpi = 300, bg = fond)
  # Slide : même graphe au format 16:9. On ne réapplique pas le thème, pour garder
  # les réglages propres à chaque figure et les proportions texte / graphe.
  # Projeté plein écran (13,3 pouces), le texte de base fait alors environ 19 pt.
  ggsave(file.path(racine, "figures/slides", paste0(nom, ".png")), p,
         width = 9.6, height = 5.4, dpi = 300, bg = fond)
  invisible(p)
}
