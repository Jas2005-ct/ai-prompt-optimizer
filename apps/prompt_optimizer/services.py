"""Prompt Optimization Service — core pipeline logic."""
import json
import logging
from django.conf import settings
from django.core.cache import cache
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.exceptions import PromptOptimizationException
from apps.shared.utils import generate_cache_key

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """You are an expert AI Prompt Engineer specializing in optimizing prompts for large language models.
Your task is to transform a raw, unstructured user prompt into a high-quality, professional, production-ready AI prompt optimized specifically for the target task type.

Prompt Type: {prompt_type}

Specific Guidelines for this prompt type:
{type_guidance}

Optimization Objectives:
1. Role/Persona: Assign a highly specific and professional persona for the AI (e.g. "You are a senior backend engineer...").
2. Context & Objectives: Outline clear, precise requirements and expectations.
3. Specific Instructions: Break down tasks into structured, actionable guidelines.
4. Output Format: Explicitly instruct how the output should be structured (e.g. step-by-step list, code blocks, table, JSON).
5. Grammar & Clarity: Fix any spelling, grammar, and syntax issues to make the prompt clear.
6. Make it Actionable: Avoid vague words like "better", "fast", or "high-quality"; instead, define concrete standards.

For the given raw prompt, you MUST return a valid JSON object matching the following structure:
{{
    "optimized_prompt": "The fully rewritten, optimized prompt, formatted with Markdown headers and bullet points for maximum readability",
    "suggested_role": "A clear role/persona assignment for the AI, starting with 'You are a...'",
    "improvements_made": [
        "Specifically what was improved (e.g. 'Added clear database schema requirements')",
        "Include at least 3 distinct improvements"
    ],
    "output_structure": "Recommended response format, e.g. 'Annotated Python code block', 'Step-by-step numbered list', 'Markdown table'"
}}

Return ONLY the raw JSON object. Do not include markdown code block formatting (such as ```json) or any other conversational text in your response.
"""


PROMPT_TYPE_GUIDELINES = {
    'general': (
        "- Clarify the primary goal and eliminate ambiguous language.\n"
        "- Add target audience, desired tone, and format guidelines.\n"
        "- Structure the prompt with clear headings (e.g., Context, Instructions, Output Format)."
    ),
    'coding': (
        "- Identify the programming language, framework, and standards.\n"
        "- Enforce best practices, clean code conventions, and robust error handling/edge cases.\n"
        "- Request explanations of complex logic, comments, and structure."
    ),
    'sql': (
        "- Emphasize specifying the SQL dialect (e.g., PostgreSQL, MySQL, SQLite).\n"
        "- Request database schema context (tables, columns, types) and relationships.\n"
        "- Incorporate performance optimization constraints (indexing, query plans) and security warnings against SQL injection."
    ),
    'uiux': (
        "- Define target personas, user journeys, and interfaces.\n"
        "- Include design system constraints, responsiveness requirements, and accessibility (WCAG) standards.\n"
        "- Outline component structure, user flows, and wireframe specifications."
    ),
    'image': (
        "- Add rich visual details: subject, environment, lighting (cinematic, soft), composition (rule of thirds), and artistic style.\n"
        "- Include technical parameters (aspect ratio, resolution, camera settings).\n"
        "- Add negative prompt constraints to avoid text, warp, or low quality."
    ),
    'api': (
        "- Specify the API style (REST, GraphQL, gRPC) and status/error response standards.\n"
        "- Include request/response schema specifications (JSON), versioning, and authorization headers.\n"
        "- Request complete payload definitions or mock datasets."
    ),
    'devops': (
        "- Detail the cloud environment/provider (AWS, GCP, Azure) and infrastructure/container tools (Docker, Kubernetes, Terraform).\n"
        "- Enforce security policies (secrets management, IAM) and scalability requirements.\n"
        "- Include backup, logging, and monitoring requirements."
    ),
    'documentation': (
        "- Define the style guide or tone of voice (e.g. technical, friendly) and the target audience.\n"
        "- Specify document structure, table of contents, callouts, and technical depth.\n"
        "- Request definitions for jargon and structured headings."
    ),
    'architecture': (
        "- Detail architectural patterns (microservices, monolithic, serverless) and scalability limits.\n"
        "- Request database selections, technical trade-offs (CAP theorem, performance/cost), and data flow descriptions.\n"
        "- Specify security boundaries and high availability/disaster recovery strategies."
    ),
}


class PromptOptimizationService:
    """
    Core service for optimizing user prompts.
    Orchestrates: AI provider call -> response parsing -> DB record creation.
    """

    def __init__(self, provider_name: str = None, model: str = None):
        # Resolve user-friendly model category (e.g. 'gemini', 'openai', 'nvidia') to correct provider/model
        from apps.ai_providers.factory import MODEL_REGISTRY
        provider_name = provider_name or settings.DEFAULT_AI_PROVIDER
        
        if provider_name in MODEL_REGISTRY:
            resolved = MODEL_REGISTRY[provider_name]
            self.provider_name = resolved['provider']
            self.model = resolved['model_name']
        else:
            self.provider_name = provider_name
            self.model = model

        self.provider = AIProviderFactory.get_provider(self.provider_name, self.model)


    def optimize(self, raw_prompt: str, prompt_type: str = 'general', session_id: str = '') -> dict:
        """
        Main optimization pipeline.
        Returns dict with optimized_prompt, suggested_role, improvements_made, output_structure.
        """
        cache_key = generate_cache_key('optimization', {
            'prompt': raw_prompt,
            'type': prompt_type,
            'provider': self.provider_name,
        })

        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for prompt optimization: {cache_key}")
            return cached

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            prompt_type=prompt_type,
            type_guidance=PROMPT_TYPE_GUIDELINES.get(prompt_type, '')
        )

        user_prompt = f"Raw prompt to optimize:\n\n{raw_prompt}"

        try:
            ai_response = self.provider.complete(system_prompt, user_prompt)
            result = self._parse_ai_response(ai_response.content)
            result['token_count'] = ai_response.total_tokens
            result['ai_provider'] = self.provider_name
            result['ai_model'] = ai_response.model

            # Save to DB
            record = self._save_record(raw_prompt, prompt_type, session_id, result)
            result['record_id'] = str(record.id)

            cache.set(cache_key, result, timeout=300)
            return result

        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            raise PromptOptimizationException(str(e))

    def _parse_ai_response(self, content: str) -> dict:
        """Parse and validate JSON from AI response."""
        try:
            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            return json.loads(content.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse JSON from AI response: {e}")
            # Fallback: return raw content as optimized prompt
            return {
                'optimized_prompt': content,
                'suggested_role': '',
                'improvements_made': ['Content returned as-is due to parsing issue'],
                'output_structure': 'Plain text',
            }

    def _save_record(self, raw_prompt: str, prompt_type: str, session_id: str, result: dict):
        """Save the optimization result to the database."""
        from apps.prompt_optimizer.models import OptimizationRecord
        return OptimizationRecord.objects.create(
            raw_prompt=raw_prompt,
            prompt_type=prompt_type,
            ai_provider=result.get('ai_provider', ''),
            ai_model=result.get('ai_model', ''),
            optimized_prompt=result.get('optimized_prompt', ''),
            suggested_role=result.get('suggested_role', ''),
            improvements_made=result.get('improvements_made', []),
            output_structure=result.get('output_structure', ''),
            token_count=result.get('token_count', 0),
            session_id=session_id,
        )
