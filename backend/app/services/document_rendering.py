"""Renders the structured content dict built by DocumentGeneratorService
into each export format. Markdown is the source of truth; HTML is
derived from it. DOCX and PDF are built directly from the content dict
so their structure (headings, tables) doesn't depend on markdown-to-X
conversion fidelity.
"""
import io

import markdown2
from docx import Document
from docx.shared import Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def render_markdown(content: dict) -> str:
    if "cahier_des_charges" in content:
        return render_business_markdown(content)

    p = content["project"]
    lines = [
        f"# Cahier des charges — {p['name']}",
        "",
        f"*{p['organization']} — généré le {content['generated_at']}*",
        "",
        "## 1. Résumé exécutif",
        "",
        content["executive_summary"],
        "",
        f"**Statut du projet :** {p['status']} · "
        f"**Complétude du cadrage :** {content['completeness']['overall_completion']}% · "
        f"**Confiance moyenne :** {content['completeness']['overall_confidence']}%",
        "",
    ]

    if content["stakeholders"]:
        lines += ["## 2. Parties prenantes", ""]
        for s in content["stakeholders"]:
            lines.append(f"- **{s['concept']}** : {s['answer']}")
        lines.append("")

    lines += ["## 3. Exigences", ""]
    for req_type, reqs in content["requirements_by_type"].items():
        label = content["requirement_type_labels"].get(req_type, req_type)
        lines.append(f"### {label}")
        lines.append("")
        for r in reqs:
            lines.append(f"**{r['requirement_key']} — {r['title']}** (priorité : {r['priority']}, risque : {r['risk']})")
            lines.append("")
            lines.append(r["description"])
            lines.append("")
            if r["acceptance_criteria"]:
                lines.append("Critères d'acceptation :")
                for c in r["acceptance_criteria"]:
                    lines.append(f"- {c}")
                lines.append("")
            if r["dependencies"]:
                lines.append(f"Dépendances : {', '.join(r['dependencies'])}")
                lines.append("")
    if not content["requirements_by_type"]:
        lines.append("_Aucune exigence n'a encore été générée pour ce projet._")
        lines.append("")

    lines += ["## 4. Dictionnaire de données", ""]
    if content["data_dictionary"]:
        lines.append("| Nom | Domaine | Description |")
        lines.append("|---|---|---|")
        for d in content["data_dictionary"]:
            lines.append(f"| {d['name']} | {d['domain']} | {d['description']} |")
        lines.append("")
    else:
        lines.append("_Aucune entité documentée pour le moment._")
        lines.append("")

    lines += ["## 5. User Stories", ""]
    for us in content["user_stories"]:
        lines.append(f"- **{us['requirement_key']}** — {us['story']}")
    if not content["user_stories"]:
        lines.append("_Aucune user story disponible._")
    lines.append("")

    lines += ["## 6. Plan de test", ""]
    if content["test_plan"]:
        lines.append("| Exigence | Cas de test | Priorité | Statut |")
        lines.append("|---|---|---|---|")
        for t in content["test_plan"]:
            lines.append(f"| {t['requirement_key']} | {t['test_case']} | {t['priority']} | {t['status']} |")
        lines.append("")
    else:
        lines.append("_Aucun cas de test disponible._")
        lines.append("")

    lines += ["## 7. Conception — Diagramme MVP", ""]
    lines.append(
        "Diagramme unique de conception représentant le MVP : acteurs, frontend, "
        "backend, modules justifiés par les exigences, données et contrôles de "
        "sécurité. Conformément au principe de conception de ce document, seuls "
        "les éléments requis par les exigences confirmées apparaissent — pas de "
        "briques ajoutées par défaut (microservices, Kubernetes, etc.)."
    )
    lines.append("")
    mvp_diagram = content["diagrams"].get("mvp_diagram_mermaid", "")
    if mvp_diagram:
        lines += ["```mermaid", mvp_diagram, "```", ""]

    sec = content["security"]
    lines += ["## 8. Sécurité", ""]
    if not sec["available"]:
        lines.append(sec["note"])
        lines.append("")
    else:
        lines.append(f"**Score de sécurité global : {sec['security_score']}/100**")
        lines.append("")
        lines.append("| Contrôle | Statut | Recommandation |")
        lines.append("|---|---|---|")
        for c in sec["checklist"]:
            lines.append(f"| {c['name']} | {c['status']} | {c['recommendation']} |")
        lines.append("")
        lines.append("### Registre des risques")
        lines.append("")
        for r in sec["risk_register"]:
            lines.append(f"- **{r['risk_id']} — {r['title']}** (impact : {r['impact']}, statut : {r['status']}) — {r['mitigation']}")
        lines.append("")

    lines += ["## 9. Traçabilité", ""]
    lines.append(
        "Chaque exigence référence le concept du Knowledge Graph dont elle est issue "
        "(`source_concept_key`) — voir `/requirements/traceability-matrix` pour la matrice complète."
    )
    lines.append("")

    lines += ["## 10. Déploiement, maintenance et formation", ""]
    lines.append(f"**Déploiement :** {content['deployment_notes'] or 'Non documenté.'}")
    lines.append("")
    lines.append(f"**Disponibilité :** {content['availability_notes'] or 'Non documentée.'}")
    lines.append("")
    lines.append(f"**Maintenance / recette :** {content['maintenance_notes'] or 'Non documentée.'}")
    lines.append("")
    lines.append(f"**Formation :** {content['training_notes'] or 'Non documentée.'}")
    lines.append("")
    lines.append(f"**Supervision :** {content['monitoring_notes'] or 'Non documentée.'}")
    lines.append("")

    if content["unimplemented_sections"]:
        lines += ["## 11. Sections non générées", ""]
        for s in content["unimplemented_sections"]:
            lines.append(f"- **{s['name']}** — {s['reason']}")
        lines.append("")

    return "\n".join(lines)


def render_business_markdown(content: dict) -> str:
    p = content["project"]
    cdc = content["cahier_des_charges"]
    conception = content["conception_mvp"]
    lines = [
        f"# Cahier des charges - {p['name']}",
        "",
        f"**Titre complet :** {cdc['title']}",
        "",
        f"*{p['organization']} - genere le {content['generated_at']}*",
        "",
        "## Cahier des Charges genere",
        "",
        "### Resume",
        "",
        cdc["summary"],
        "",
        f"**Score de completude :** {cdc['completeness_score']}%",
        "",
    ]
    if cdc["points_to_confirm"]:
        lines += ["### Points a confirmer", ""]
        lines += [f"- {point}" for point in cdc["points_to_confirm"]]
        lines.append("")

    for section in cdc["sections"]:
        lines += [f"## {section['title']}", ""]
        lines += [f"- {item}" for item in section["items"]]
        lines.append("")

    lines += [
        "## Conception MVP",
        "",
        "### Resume architectural",
        "",
        conception["summary"],
        "",
        "### Modules",
        "",
    ]
    lines += [f"- {module}" for module in conception["modules"]]
    lines += [
        "",
        "### Diagramme unique",
        "",
        "```mermaid",
        conception["diagram"],
        "```",
        "",
    ]
    return "\n".join(lines)


def render_latex(content: dict) -> str:
    md = render_markdown(content)
    escaped = (
        md.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )
    body = []
    for line in escaped.splitlines():
        if line.startswith("\\#\\# "):
            body.append(f"\\section*{{{line[6:]}}}")
        elif line.startswith("\\#\\#\\# "):
            body.append(f"\\subsection*{{{line[8:]}}}")
        elif line.startswith("\\# "):
            body.append(f"\\title{{{line[3:]}}}\\maketitle")
        elif line.startswith("- "):
            body.append(f"\\noindent\\textbullet\\ {line[2:]}\\\\")
        elif line.startswith("```"):
            continue
        else:
            body.append(line + "\n")
    return "\\documentclass[11pt]{article}\n\\usepackage[utf8]{inputenc}\n\\begin{document}\n" + "\n".join(body) + "\n\\end{document}\n"


def render_html(markdown_content: str) -> str:
    body = markdown2.markdown(
        markdown_content, extras=["tables", "fenced-code-blocks", "header-ids"]
    )
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Cahier des charges</title>
<style>
body {{ font-family: -apple-system, Segoe UI, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #1a1a1a; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; font-size: 0.9rem; }}
th {{ background: #f4f4f4; }}
code {{ background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 3px; }}
pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; border-radius: 6px; }}
h1, h2, h3 {{ color: #14532d; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def render_docx(content: dict) -> bytes:
    doc = Document()
    p = content["project"]

    doc.add_heading(f"Cahier des charges — {p['name']}", level=0)
    doc.add_paragraph(f"{p['organization']} — généré le {content['generated_at']}")

    doc.add_heading("1. Résumé exécutif", level=1)
    doc.add_paragraph(content["executive_summary"])
    doc.add_paragraph(
        f"Statut : {p['status']} · Complétude : {content['completeness']['overall_completion']}% · "
        f"Confiance : {content['completeness']['overall_confidence']}%"
    )

    if content["stakeholders"]:
        doc.add_heading("2. Parties prenantes", level=1)
        for s in content["stakeholders"]:
            doc.add_paragraph(f"{s['concept']} : {s['answer']}", style="List Bullet")

    doc.add_heading("3. Exigences", level=1)
    if not content["requirements_by_type"]:
        doc.add_paragraph("Aucune exigence n'a encore été générée pour ce projet.")
    for req_type, reqs in content["requirements_by_type"].items():
        label = content["requirement_type_labels"].get(req_type, req_type)
        doc.add_heading(label, level=2)
        for r in reqs:
            heading = doc.add_paragraph()
            run = heading.add_run(f"{r['requirement_key']} — {r['title']}")
            run.bold = True
            doc.add_paragraph(f"Priorité : {r['priority']} · Risque : {r['risk']} · Statut : {r['status']}")
            doc.add_paragraph(r["description"])
            for c in r["acceptance_criteria"]:
                doc.add_paragraph(c, style="List Bullet")

    doc.add_heading("4. Dictionnaire de données", level=1)
    if content["data_dictionary"]:
        table = doc.add_table(rows=1, cols=3)
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text = "Nom", "Domaine", "Description"
        for d in content["data_dictionary"]:
            row = table.add_row().cells
            row[0].text, row[1].text, row[2].text = d["name"], d["domain"], d["description"]
    else:
        doc.add_paragraph("Aucune entité documentée pour le moment.")

    doc.add_heading("5. User Stories", level=1)
    for us in content["user_stories"]:
        doc.add_paragraph(f"{us['requirement_key']} — {us['story']}", style="List Bullet")

    doc.add_heading("6. Plan de test", level=1)
    if content["test_plan"]:
        table = doc.add_table(rows=1, cols=4)
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = (
            "Exigence", "Cas de test", "Priorité", "Statut",
        )
        for t in content["test_plan"]:
            row = table.add_row().cells
            row[0].text, row[1].text, row[2].text, row[3].text = (
                t["requirement_key"], t["test_case"], t["priority"], t["status"],
            )
    else:
        doc.add_paragraph("Aucun cas de test disponible.")

    sec = content["security"]
    doc.add_heading("7. Sécurité", level=1)
    if not sec["available"]:
        doc.add_paragraph(sec["note"])
    else:
        doc.add_paragraph(f"Score de sécurité global : {sec['security_score']}/100")
        table = doc.add_table(rows=1, cols=3)
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text = "Contrôle", "Statut", "Recommandation"
        for c in sec["checklist"]:
            row = table.add_row().cells
            row[0].text, row[1].text, row[2].text = c["name"], c["status"], c["recommendation"]

    doc.add_heading("8. Déploiement, maintenance et formation", level=1)
    doc.add_paragraph(f"Déploiement : {content['deployment_notes'] or 'Non documenté.'}")
    doc.add_paragraph(f"Maintenance / recette : {content['maintenance_notes'] or 'Non documentée.'}")
    doc.add_paragraph(f"Formation : {content['training_notes'] or 'Non documentée.'}")

    style = doc.styles["Normal"]
    style.font.size = Pt(10.5)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def render_pdf(content: dict) -> bytes:
    if "cahier_des_charges" in content:
        return render_business_pdf(content)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=colors.HexColor("#14532d"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#14532d"))
    body = styles["BodyText"]

    p = content["project"]
    story = [
        Paragraph(f"Cahier des charges — {p['name']}", styles["Title"]),
        Paragraph(f"{p['organization']} — généré le {content['generated_at']}", body),
        Spacer(1, 12),
        Paragraph("1. Résumé exécutif", h1),
        Paragraph(content["executive_summary"] or "Non documenté.", body),
        Spacer(1, 12),
    ]

    story.append(Paragraph("2. Exigences", h1))
    if not content["requirements_by_type"]:
        story.append(Paragraph("Aucune exigence n'a encore été générée pour ce projet.", body))
    for req_type, reqs in content["requirements_by_type"].items():
        label = content["requirement_type_labels"].get(req_type, req_type)
        story.append(Paragraph(label, h2))
        for r in reqs:
            story.append(
                Paragraph(
                    f"<b>{r['requirement_key']} — {r['title']}</b> (priorité : {r['priority']}, risque : {r['risk']})",
                    body,
                )
            )
            story.append(Paragraph(r["description"] or "", body))
            story.append(Spacer(1, 6))

    story.append(Paragraph("3. Dictionnaire de données", h1))
    if content["data_dictionary"]:
        data = [["Nom", "Domaine", "Description"]] + [
            [d["name"], d["domain"], d["description"][:120]] for d in content["data_dictionary"]
        ]
        table = Table(data, colWidths=[4 * cm, 3 * cm, 9 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14532d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
    else:
        story.append(Paragraph("Aucune entité documentée pour le moment.", body))

    sec = content["security"]
    story.append(Spacer(1, 12))
    story.append(Paragraph("4. Sécurité", h1))
    if not sec["available"]:
        story.append(Paragraph(sec["note"], body))
    else:
        story.append(Paragraph(f"Score de sécurité global : {sec['security_score']}/100", body))
        data = [["Contrôle", "Statut", "Recommandation"]] + [
            [c["name"], c["status"], c["recommendation"][:100]] for c in sec["checklist"]
        ]
        table = Table(data, colWidths=[4 * cm, 2.5 * cm, 9.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14532d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)

    doc.build(story)
    return buf.getvalue()


def render_business_pdf(content: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=1.4 * cm, bottomMargin=1.4 * cm, leftMargin=1.5 * cm, rightMargin=1.5 * cm
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("CompactTitle", parent=styles["Title"], fontSize=14, leading=16)
    h1 = ParagraphStyle("CompactH1", parent=styles["Heading1"], fontSize=10.5, leading=12, textColor=colors.HexColor("#14532d"), spaceBefore=6, spaceAfter=3)
    body = ParagraphStyle("CompactBody", parent=styles["BodyText"], fontSize=8.2, leading=10)

    cdc = content["cahier_des_charges"]
    conception = content["conception_mvp"]
    story = [
        Paragraph("Cahier des Charges - Fondation OCP", title),
        Paragraph(cdc["summary"] or "Resume a confirmer.", body),
        Paragraph(f"Score de completude : {cdc['completeness_score']}%", body),
        Spacer(1, 6),
    ]
    if cdc["points_to_confirm"]:
        story.append(Paragraph("Points a confirmer", h1))
        for point in cdc["points_to_confirm"][:6]:
            story.append(Paragraph(f"- {point}", body))

    for section in cdc["sections"]:
        story.append(Paragraph(section["title"], h1))
        for item in section["items"][:6]:
            story.append(Paragraph(f"- {item}", body))

    story.append(Paragraph("Conception MVP", h1))
    story.append(Paragraph(conception["summary"], body))
    story.append(Paragraph("Modules : " + ", ".join(conception["modules"][:10]), body))
    story.append(Paragraph("Diagramme Mermaid unique disponible dans les exports Markdown et LaTeX.", body))

    doc.build(story)
    return buf.getvalue()
