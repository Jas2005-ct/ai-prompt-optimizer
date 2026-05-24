"""Prompt Optimization Service — core pipeline logic."""
import json
import logging
from django.conf import settings
from django.core.cache import cache
from apps.ai_providers.factory import AIProviderFactory
from apps.shared.exceptions import PromptOptimizationException
from apps.shared.utils import generate_cache_key

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """
You are an expert AI Prompt Engineer specializing in optimizing prompts for large language models.
Your task is to transform raw, unstructured user prompts into professional, production-ready AI prompts.

For the given raw prompt, you MUST return a valid JSON object with the following structure:
{
    "optimized_prompt": "The fully rewritten, optimized prompt",
    "suggested_role": "A role assignment for the AI, e.g. 'You are a senior backend engineer...'",
    "improvements_made": [
        "Improved clarity: ...",
        "Added context: ...",
        "Fixed grammar: ...",
        "Structured output: ..."
    ],
    "output_structure": "Recommended output format, e.g. Step-by-step, JSON, Table, etc."
}

Prompt Type: {prompt_type}

Optimization Guidelines:
- Add clear role assignment
- Fix grammar and clarity
- Add output format instructions
- Add context constraints
- Specify expected output length/depth
- Include professional AI instructions
- Make the prompt specific and actionable
- Return ONLY valid JSON, no extra text
"""


PROMPT_TYPE_GUIDELINES = {
    'general': 'General AI assistant task. Optimize for clarity and completeness.',
    'coding': 'Software development task. Add language, framework, best practices, error handling requirements.',
    'sql': 'Database/SQL task. Include schema context hints, performance, and output format.',
    'uiux': 'UI/UX design task. Include design system, accessibility, and component structure.',
    'image': 'Image generation task. Add style, lighting, composition, artistic direction.',
    'api': 'API design/generation. Include REST standards, versioning, authentication, response format.',
    'devops': 'DevOps/infrastructure task. Include environment, tools, security, scalability.',
    'documentation': 'Documentation task. Include audience, format, depth, structure.',
    'architecture': 'System architecture task. Include scale, technology choices, trade-offs.',
}


class PromptOptimizationService:
    """
    Core service for optimizing user prompts.
    Orchestrates: AI provider call -> response parsing -> DB record creation.
    """

    def __init__(self, provider_name: str = None, model: str = None):
        self.provider_name = provider_name or settings.DEFAULT_AI_PROVIDER
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
            prompt_type=prompt_type
        ) + f"\nSpecific type guidance: {PROMPT_TYPE_GUIDELINES.get(prompt_type, '')}"

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
