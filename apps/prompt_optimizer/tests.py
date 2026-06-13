from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from apps.prompt_optimizer.models import OptimizationRecord, SavedPrompt, PromptType
from apps.prompt_templates.models import PromptTemplate
from apps.ai_providers.factory import AIProviderFactory
from apps.ai_providers.base import AIResponse
from apps.shared.exceptions import custom_exception_handler


class PromptOptimizerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a test prompt template
        self.template = PromptTemplate.objects.create(
            title="Test Template",
            template_text="Please write a python code to do {task}",
            category="coding"
        )
        
        # Create a test optimization record
        self.record = OptimizationRecord.objects.create(
            raw_prompt="write a script to parse csv",
            prompt_type=PromptType.CODING,
            ai_provider="openai",
            ai_model="gpt-4o",
            optimized_prompt="Optimized prompt text here",
            suggested_role="Python expert",
            improvements_made=["improved code quality"],
            output_structure="Python code block",
            token_count=150,
            session_id="sess_12345"
        )

    def test_optimization_record_creation(self):
        self.assertEqual(self.record.raw_prompt, "write a script to parse csv")
        self.assertEqual(self.record.prompt_type, PromptType.CODING)
        self.assertFalse(self.record.is_saved)

    def test_save_prompt_model_relation(self):
        saved = SavedPrompt.objects.create(
            title="Saved parsed CSV",
            prompt_type=self.record.prompt_type,
            optimized_prompt=self.record.optimized_prompt,
            optimization_record=self.record
        )
        self.assertEqual(saved.optimization_record.id, self.record.id)

    @patch('apps.ai_providers.factory.AIProviderFactory.get_provider')
    def test_optimize_api_view(self, mock_get_provider):
        # Mock provider complete call
        mock_provider = MagicMock()
        mock_provider.complete.return_value = AIResponse(
            content='{"optimized_prompt": "Opt", "suggested_role": "Role", "improvements_made": ["done"], "output_structure": "Format"}',
            provider="openai",
            model="gpt-4o",
            total_tokens=100
        )
        mock_get_provider.return_value = mock_provider

        url = reverse('api-optimize')
        payload = {
            "raw_prompt": "optimize this text",
            "prompt_type": "coding",
            "provider": "openai",
            "model": "gpt-4o"
        }
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertTrue(response_json['success'])

    def test_get_template_by_id(self):
        url = reverse('api-templates')
        response = self.client.get(f"{url}?id={self.template.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], "Test Template")

    def test_save_prompt_api_view(self):
        url = reverse('api-save')
        payload = {
            "optimization_id": str(self.record.id),
            "title": "Saved Prompt Title",
            "tags": ["coding", "test"]
        }
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify the record is updated in the database
        self.record.refresh_from_db()
        self.assertTrue(self.record.is_saved)

    def test_delete_saved_prompt(self):
        saved = SavedPrompt.objects.create(
            title="Prompt to delete",
            prompt_type=self.record.prompt_type,
            optimized_prompt=self.record.optimized_prompt,
            optimization_record=self.record
        )
        self.record.is_saved = True
        self.record.save()
        
        url = reverse('api-delete-saved-prompt', kwargs={'pk': saved.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify deletion and reset of is_saved field
        self.assertFalse(SavedPrompt.objects.filter(id=saved.id).exists())
        self.record.refresh_from_db()
        self.assertFalse(self.record.is_saved)

    def test_switch_model_api_view(self):
        url = reverse('api-switch-model')
        payload = {
            "provider": "gemini",
            "model": "gemini-2.0-flash"
        }
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.session['default_provider'], 'gemini')
        self.assertEqual(self.client.session['default_model'], 'gemini-2.0-flash')

    def test_custom_exception_handler_typo_fixed(self):
        # Call the exception handler directly to check the keys
        from rest_framework.exceptions import APIException
        exc = APIException(detail="test error detail")
        
        context = {}
        res = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(res)
        self.assertIn('status_code', res.data)
        self.assertNotIn('st atus_code', res.data)
        self.assertEqual(res.data['status_code'], 500)
