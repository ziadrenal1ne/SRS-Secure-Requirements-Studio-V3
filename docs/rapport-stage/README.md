# Rapport de stage / PFA — LaTeX

Ce dossier contient le rapport de stage/PFA décrivant le développement de
**Secure Requirements Studio (SRS)**, réalisé au sein de la Fondation OCP.

Ce rapport est **externe à l'application SRS** — il n'est pas généré par
l'outil lui-même (voir Document 2 §26-27 des spécifications projet : SRS
génère uniquement le Cahier des Charges, la Conception, le Diagramme MVP et
les Exigences de cybersécurité comme livrables applicatifs).

## Structure

```
rapport-stage/
├── rapport-stage.tex      # Fichier principal (page de garde, TOC, \input des chapitres)
├── chapters/               # Un fichier .tex par chapitre/annexe
├── figures/                # Images et diagrammes à insérer
├── references.bib          # Bibliographie
└── README.md               # Ce fichier
```

## Compiler le rapport

Prérequis : une distribution LaTeX (TeX Live / MiKTeX) avec `pdflatex`.

```bash
cd docs/rapport-stage
pdflatex rapport-stage.tex
pdflatex rapport-stage.tex   # deuxième passe pour la table des matières
```

Ou avec `latexmk` (recommandé, gère les passes automatiquement) :

```bash
latexmk -pdf rapport-stage.tex
```

## Compléter le rapport

Le rapport contient des marqueurs `\TODO{...}` (affichés en rouge dans le
PDF) partout où une information réelle est nécessaire mais n'était pas
disponible au moment de la rédaction : noms d'encadrants, dates, chiffres
officiels de la Fondation OCP, résultats de tests, captures d'écran, etc.

**Ne remplacez jamais un `\TODO{}` par une information inventée.** S'il vous
manque une donnée, laissez le marqueur ou notez-la comme "à confirmer" —
c'est le même principe de traçabilité que celui appliqué par SRS lui-même
dans les documents qu'il génère (voir chapitre 6 du rapport).

Rechercher tous les marqueurs restants avant la remise finale :

```bash
grep -rn '\\TODO{' chapters/ rapport-stage.tex
```
