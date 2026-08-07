import io
import json

import pytest

from app.services.document_generator import DocumentGeneratorService
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.requirement import RequirementService
from app.services.security_engine import SecurityEngineService

from tests.conftest import create_project


async def _create_project(client) -> str:
    """Creates a project through the real no-auth public API. The app has
    no authentication layer, so this is the actual project-creation path,
    not a stand-in for one."""
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "short_name": "TP"},
    )
    return create.json()["id"]


# --- Service-level tests ---


@pytest.mark.asyncio
async def test_build_content_on_fresh_project_has_no_fabricated_data(db_session):
    project = await create_project(db_session, name="Projet Test", short_name="PT")
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    content = await DocumentGeneratorService(db_session).build_content(project_id)

    assert content["requirements_by_type"] == {}
    assert content["data_dictionary"] == []
    assert content["security"]["available"] is False
    assert "n'a pas encore été documenté" in content["executive_summary"]
    assert len(content["unimplemented_sections"]) == 2


@pytest.mark.asyncio
async def test_generate_is_idempotent_upsert(db_session):
    project = await create_project(db_session, name="Projet Test", short_name="PT")
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    service = DocumentGeneratorService(db_session)
    first = await service.generate(project_id)
    first_id = first.id
    second = await service.generate(project_id)
    assert first_id == second.id


@pytest.mark.asyncio
async def test_export_formats_produce_valid_files(db_session):
    project = await create_project(db_session, name="PGB Al Moutmir", short_name="PGB", org_name="Fondation OCP")
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    node = await kg.apply_update(
        project_id, "business.objective", completion_delta=90,
        captured_data={"raw_answer": "Consolider les donnees beneficiaires du programme Al Moutmir."},
    )
    await RequirementService(db_session).generate_for_node(project_id, node)
    await SecurityEngineService(db_session).analyze(project_id)

    doc_service = DocumentGeneratorService(db_session)
    await doc_service.generate(project_id)

    # JSON: must round-trip through json.loads and contain real content
    json_bytes, json_media, json_name = await doc_service.export(project_id, "json")
    assert json_media == "application/json"
    assert json_name.endswith(".json")
    parsed = json.loads(json_bytes)
    assert parsed["project"]["name"] == "PGB Al Moutmir"
    assert "business" in parsed["requirements_by_type"]

    # Markdown: must contain the requirement key and section headers
    md_bytes, md_media, _ = await doc_service.export(project_id, "md")
    md_text = md_bytes.decode("utf-8")
    assert "# Cahier des charges" in md_text
    assert "BR-001" in md_text
    assert "```mermaid" in md_text

    # HTML: must be valid-looking HTML derived from the markdown
    html_bytes, html_media, _ = await doc_service.export(project_id, "html")
    html_text = html_bytes.decode("utf-8")
    assert html_media == "text/html"
    assert "<html" in html_text
    assert "BR-001" in html_text

    # DOCX: must be a real, parseable .docx (a zip-based OOXML package)
    docx_bytes, docx_media, docx_name = await doc_service.export(project_id, "docx")
    assert docx_name.endswith(".docx")
    from docx import Document

    parsed_docx = Document(io.BytesIO(docx_bytes))
    docx_text = "\n".join(p.text for p in parsed_docx.paragraphs)
    assert "PGB Al Moutmir" in docx_text
    assert "BR-001" in docx_text

    # PDF: must start with the PDF magic bytes and be parseable structure-wise
    pdf_bytes, pdf_media, pdf_name = await doc_service.export(project_id, "pdf")
    assert pdf_name.endswith(".pdf")
    assert pdf_bytes[:5] == b"%PDF-"
    assert pdf_bytes.rstrip()[-5:] == b"%%EOF" or b"%%EOF" in pdf_bytes[-1024:]


@pytest.mark.asyncio
async def test_export_unsupported_format_raises(db_session):
    project = await create_project(db_session, name="P", short_name="P")
    project_id = project.id
    kg = KnowledgeGraphService(db_session)
    await kg.seed_project_graph(project_id)

    service = DocumentGeneratorService(db_session)
    await service.generate(project_id)

    from app.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await service.export(project_id, "xml")


# --- API-level tests ---


@pytest.mark.asyncio
async def test_documents_api_generate_get_and_export(client, unique_email):
    project_id = await _create_project(client)

    gen = await client.post(f"/api/v1/projects/{project_id}/documents/generate")
    assert gen.status_code == 200
    assert "executive_summary" in gen.json()["content"]

    fetched = await client.get(f"/api/v1/projects/{project_id}/documents")
    assert fetched.status_code == 200

    for fmt, expect_prefix in [
        ("json", None),
        ("md", b"# Cahier"),
        ("html", b"<!DOCTYPE"),
        ("docx", b"PK"),  # OOXML files are zip archives
        ("pdf", b"%PDF-"),
    ]:
        resp = await client.get(
            f"/api/v1/projects/{project_id}/documents/export",
            params={"format": fmt},
        )
        assert resp.status_code == 200, f"format={fmt}"
        assert "attachment" in resp.headers["content-disposition"]
        if expect_prefix:
            assert resp.content[: len(expect_prefix)] == expect_prefix, f"format={fmt}"


@pytest.mark.asyncio
async def test_documents_get_without_generate_returns_404(client, unique_email):
    project_id = await _create_project(client)

    resp = await client.get(f"/api/v1/projects/{project_id}/documents")
    assert resp.status_code == 404


