"""AI client for the Interview Engine.

The application supports two modes:
- TemplateLLMClient: deterministic, no network calls.
- GeminiLLMClient: Google Gemini assistant for adaptive interview reasoning.
"""

import asyncio
import json
import re
from typing import Protocol

from pydantic import BaseModel

from app.domain import focp_knowledge
from app.logging import get_logger
from app.models.knowledge_graph import KnowledgeGraphNode
from app.services.ai_settings import EffectiveAISettings, load_ai_settings

logger = get_logger(__name__)


class AnswerInterpretation(BaseModel):
    completion_delta: int
    confidence_delta: int
    captured_data: dict
    missing_information: list[str]
    follow_up_needed: bool
    consultant_note: str


class AIClient(Protocol):
    async def generate_question(
        self, node: KnowledgeGraphNode, history: list[dict], planned_question=None
    ) -> str: ...

    async def interpret_answer(
        self,
        node: KnowledgeGraphNode,
        question: str,
        answer: str,
        history: list[dict],
    ) -> AnswerInterpretation: ...


LLMClient = AIClient


class TemplateLLMClient:
    async def generate_question(
        self, node: KnowledgeGraphNode, history: list[dict], planned_question=None
    ) -> str:
        if planned_question is not None:
            return planned_question.question
        already_asked = len(node.generated_questions)
        if already_asked == 0:
            return f"{node.label} - {node.description} Pouvez-vous decrire ce point pour ce projet ?"
        missing = ", ".join(node.missing_information) if node.missing_information else None
        if missing:
            return f"Concernant {node.label}, il manque encore des precisions sur : {missing}. Pouvez-vous completer ?"
        return f"Pouvez-vous apporter plus de details ou un exemple concret sur {node.label} ?"

    async def interpret_answer(
        self,
        node: KnowledgeGraphNode,
        question: str,
        answer: str,
        history: list[dict],
    ) -> AnswerInterpretation:
        cleaned = answer.strip()
        word_count = len(re.findall(r"\w+", cleaned))

        if not cleaned:
            completion_delta, confidence_delta = 0, 0
        elif word_count < 4:
            completion_delta, confidence_delta = 10, 10
        elif word_count < 15:
            completion_delta, confidence_delta = 30, 25
        elif word_count < 40:
            completion_delta, confidence_delta = 55, 45
        else:
            completion_delta, confidence_delta = 85, 70

        follow_up_needed = (node.completion + completion_delta) < 80
        return AnswerInterpretation(
            completion_delta=completion_delta,
            confidence_delta=confidence_delta,
            captured_data={"raw_answer": cleaned},
            missing_information=[] if not follow_up_needed else ["Reponse encore incomplete ou peu detaillee."],
            follow_up_needed=follow_up_needed,
            consultant_note="Reponse enregistree par le moteur template.",
        )


_CONSULTANT_SYSTEM_PROMPT = """Tu es un consultant metier senior travaillant sur \
une plateforme de gestion des beneficiaires de l'Axe Economie Sociale et Solidaire \
de la Fondation OCP. Tu t'adresses a des collaborateurs non techniques. Pose des \
questions simples, courtes, concretes et comprehensibles. Ne demande jamais de \
choisir une technologie, une architecture, un protocole, une base de donnees, une \
API ou un mecanisme de cybersecurite technique."""


def _load_google_genai():
    try:
        from google import genai
        from google.genai import types

        return genai, types
    except Exception as exc:
        raise RuntimeError(
            "Google GenAI SDK is not available in the backend runtime. "
            "Install it in the environment that runs FastAPI with: pip install google-genai"
        ) from exc


class GeminiLLMClient:
    def __init__(self, settings: EffectiveAISettings):
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._timeout = settings.gemini_timeout_seconds
        self._temperature = settings.gemini_temperature
        self._top_p = settings.gemini_top_p
        self._max_output_tokens = settings.gemini_max_output_tokens

    async def _call(self, system: str, user: str) -> str:
        if not self._api_key:
            raise RuntimeError("Gemini API key is not configured.")

        def request() -> str:
            genai, types = _load_google_genai()
            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model=self._model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=self._temperature,
                    top_p=self._top_p,
                    max_output_tokens=self._max_output_tokens,
                ),
            )
            return response.text or ""

        return await asyncio.wait_for(asyncio.to_thread(request), timeout=self._timeout)

    async def generate_question(
        self, node: KnowledgeGraphNode, history: list[dict], planned_question=None
    ) -> str:
        history_text = "\n".join(
            f"Q: {h['question']}\nR: {h['answer']}" for h in history[-6:]
        ) or "(aucun echange precedent)"
        prompt = f"""Tu travailles pour la Fondation OCP, Axe Eco-Social.
Tu connais les cooperatives marocaines, beneficiaires directs et indirects, ESG, ODD,
reporting CSV mensuel, statistiques, tableaux de bord, architecture logicielle et cybersecurite.

Contexte OCP de reference :
- Regions : {', '.join(focp_knowledge.MOROCCAN_REGIONS[:5])}...
- ODD : {', '.join(focp_knowledge.SUSTAINABLE_DEVELOPMENT_GOALS[:3])}...
- Beneficiaires : {', '.join(focp_knowledge.BENEFICIARY_CATEGORIES)}

Concept a explorer: {node.label}
Description: {node.description}
Domaine: {node.domain}
Completion actuelle: {node.completion}%
Informations manquantes: {node.missing_information}
Historique recent:
{history_text}

Question de reference a respecter si aucune adaptation utile n'est necessaire:
{planned_question.question if planned_question else node.label}

Pose UNE question de business analyst senior, adaptee aux reponses precedentes.
La question doit rester non technique, en 1 a 2 phrases maximum.
Tu peux proposer des choix simples, mais l'utilisateur doit pouvoir repondre librement.
Ne mentionne pas SQL, API, JWT, OAuth2, RBAC, ABAC, Docker, architecture, chiffrement, transactions ou backend."""
        try:
            question = await self._call(_CONSULTANT_SYSTEM_PROMPT, prompt)
            return question.strip() or await TemplateLLMClient().generate_question(node, history)
        except Exception as exc:
            logger.warning("gemini_generate_question_failed", concept_key=node.concept_key, error=str(exc))
            return await TemplateLLMClient().generate_question(node, history)

    async def interpret_answer(
        self,
        node: KnowledgeGraphNode,
        question: str,
        answer: str,
        history: list[dict],
    ) -> AnswerInterpretation:
        prompt = f"""Analyse cette reponse pour le projet Fondation OCP Axe Eco-Social.
Concept: {node.label} ({node.description})
Question: {question}
Reponse: {answer}

Contexte OCP : Pense aux categories de beneficiaires ({', '.join(focp_knowledge.BENEFICIARY_CATEGORIES)}),
aux conventions ({', '.join(focp_knowledge.CONVENTION_TYPES)}), et aux periodes de reporting.

Inferer les impacts sur: exigences fonctionnelles, exigences techniques, cybersecurite,
architecture, base de donnees, API, roles applicatifs, tableaux de bord, risques,
tests, deploiement, maintenance et documents.

Reponds STRICTEMENT en JSON valide:
{{
  "completion_delta": <entier 0-100>,
  "confidence_delta": <entier 0-100>,
  "captured_data": {{<faits et impacts structures>}},
  "missing_information": [<points a clarifier>],
  "follow_up_needed": <true ou false>,
  "consultant_note": "<synthese courte des impacts>"
}}"""
        try:
            raw = (await self._call(_CONSULTANT_SYSTEM_PROMPT, prompt)).strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
            return AnswerInterpretation(**json.loads(raw))
        except Exception as exc:
            logger.warning("gemini_interpret_answer_failed", concept_key=node.concept_key, error=str(exc))
            return await TemplateLLMClient().interpret_answer(node, question, answer, history)


_client_instance: AIClient | None = None
_client_signature: str | None = None


def get_llm_client() -> AIClient:
    global _client_instance, _client_signature
    runtime = load_ai_settings()
    signature = runtime.model_dump_json(exclude={"gemini_api_key"})
    if _client_instance is not None and _client_signature == signature:
        return _client_instance

    _client_instance = GeminiLLMClient(runtime) if runtime.provider == "gemini" else TemplateLLMClient()
    _client_signature = signature
    return _client_instance


def reset_llm_client_cache() -> None:
    global _client_instance, _client_signature
    _client_instance = None
    _client_signature = None
