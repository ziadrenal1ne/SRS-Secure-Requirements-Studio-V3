import glob
import subprocess
import os
import shutil
import pypdf

print('Sanitizing LaTeX files...')
for fpath in glob.glob(r'rapport-pfa/**/*.tex', recursive=True):
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()
    c_mod = (c.replace('\u2014', '--')
              .replace('\u2013', '--')
              .replace('\u2019', "'")
              .replace('\u2018', "'")
              .replace('\u0153', 'oe')
              .replace('\u0152', 'OE'))
    if c_mod != c:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c_mod)
        print('Cleaned:', fpath)

print('Compiling with Tectonic...')
res = subprocess.run([
    r'C:\Users\xpszi\.gemini\antigravity-ide\brain\43b8c7dc-8f11-47e1-a8c3-8b912783e48c\bin\tectonic.exe',
    r'rapport-pfa\main.tex',
    '--outdir', r'rapport-pfa'
], capture_output=True, text=True, encoding='utf-8', errors='replace')

print('Tectonic Exit Code:', res.returncode)
if res.returncode != 0:
    for line in res.stderr.splitlines():
        if 'error' in line.lower() or '!' in line or 'missing' in line.lower():
            print(line)
else:
    pdf_path = r'rapport-pfa\main.pdf'
    final_official_pdf = r'rapport-pfa\Rapport_PFA_Plateforme_Beneficiaires_Fondation_OCP.pdf'
    shutil.copyfile(pdf_path, final_official_pdf)
    shutil.copyfile(pdf_path, r'rapport-pfa\rapport-pfa.pdf')
    shutil.copyfile(pdf_path, 'Rapport_PFA_Plateforme_Beneficiaires_Fondation_OCP.pdf')
    shutil.copyfile(pdf_path, 'rapport-pfa.pdf')
    
    reader = pypdf.PdfReader(final_official_pdf)
    print('SUCCESS! Total Pages in PDF:', len(reader.pages))
    print('PDF File size:', os.path.getsize(final_official_pdf), 'bytes')
