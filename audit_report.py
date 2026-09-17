import glob
import re
import os
import pypdf

print('=== AUDIT RAPPORT PFA FONDATION OCP ===')

# 1. Placeholders check
forbidden = [
    'TODO', 'FIXME', 'XXX', 'TBD', 'Lorem ipsum', '[À compléter]', '[A COMPLETER]',
    '[Nom]', '[Prénom]', '[Entreprise]', '[Organisme]', '[Date]', '[Année]', '[Insérer]',
    '[Ajouter]', '<à compléter>', '????'
]

placeholders = []
for fpath in glob.glob(r'rapport-pfa/**/*.tex', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    for token in forbidden:
        if token.lower() in content.lower():
            placeholders.append((fpath, token))

print('Placeholders count:', len(placeholders))

# 2. 1st person singular check
first_person_patterns = [r'\bje\b', r'\bj\'ai\b', r'\bmon\b', r'\bma\b', r'\bmes\b']
fp_found = []
for fpath in glob.glob(r'rapport-pfa/**/*.tex', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    for pat in first_person_patterns:
        matches = re.findall(pat, content, re.IGNORECASE)
        if matches:
            fp_found.append((fpath, pat, matches))

print('First person occurrences count:', len(fp_found))

# 3. Check for old title occurrences in inappropriate places
old_title_pat = r'Plateforme de Gestion des Bénéficiaires Axe Économie Sociale et Solidaire'
old_title_matches = []
for fpath in glob.glob(r'rapport-pfa/**/*.tex', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if re.search(old_title_pat, content, re.IGNORECASE):
        old_title_matches.append(fpath)

print('Old raw title occurrences:', len(old_title_matches))

# 4. Total Pages & Structure
pdf_path = r'rapport-pfa\Rapport_PFA_Plateforme_Beneficiaires_Fondation_OCP.pdf'
reader = pypdf.PdfReader(pdf_path)
print('Total Pages in Official PDF:', len(reader.pages))

fig_count = 0
tab_count = 0
for fpath in glob.glob(r'rapport-pfa/**/*.tex', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()
    fig_count += len(re.findall(r'\\begin\{figure\}', c)) + len(re.findall(r'\\screenshotplaceholder', c))
    tab_count += len(re.findall(r'\\begin\{table\}', c))

print('Total Figures in LaTeX:', fig_count)
print('Total Tables in LaTeX:', tab_count)

puml_files = glob.glob(r'rapport-pfa/diagrams-source/*.puml')
print('Total PUML source diagrams:', len(puml_files))
