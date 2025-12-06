
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import types

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create Mocks for dependencies to avoid loading the whole app
mock_flask = MagicMock()
mock_flask.globals = MagicMock() # Ensure flask.globals exists
mock_app = MagicMock()
mock_app.config = {
    'OLLAMA_API_URL': 'http://localhost:11434/api/chat',
    'OLLAMA_MODEL': 'test-model'
}
mock_flask.current_app = mock_app

# Patch sys.modules to prevent actual imports of heavy dependencies
module_patches = {
    'flask': mock_flask,
    'flask.globals': mock_flask.globals,
    'app': MagicMock(),
    'models': MagicMock(),
    'models.knowledge': MagicMock(),
    'models.course': MagicMock(),
    'models.user': MagicMock(),
    'models.records': MagicMock(),
    'models.exam': MagicMock(),
    'services.learning_service': MagicMock(),
    'services.exam_service': MagicMock(),
    'services.review_service': MagicMock(),
    'services.settings_service': MagicMock(),
    'services.course_service': MagicMock(),
    'flask_sqlalchemy': MagicMock(),
}

with patch.dict('sys.modules', module_patches):
    # Now we can import AIService safely. 
    # Note: We import it directly from the module file to avoid services/__init__.py logic if possible,
    # but since we mocked the siblings, even services/__init__ should be fine.
    
    # However, importing services.ai_service might still trigger services/__init__ which imports mocked modules.
    from services.ai_service import AIService

class TestGenericPrompts(unittest.TestCase):
    def setUp(self):
        self.ai_service = AIService()
        # Mock _make_request to inspect the prompt instead of calling API
        self.ai_service._make_request = MagicMock(return_value="Mock Response")

    def test_generate_explanation_generic(self):
        # Test default
        self.ai_service.generate_explanation("Chapter 1", "Concept A", "concept")
        call_args = self.ai_service._make_request.call_args
        prompt = call_args[0][0]
        self.assertIn("通用课程", prompt)
        self.assertNotIn("数据库", prompt)

        # Test explicit generic
        self.ai_service.generate_explanation("Chapter 1", "Concept A", "concept", course_name="通用课程")
        call_args = self.ai_service._make_request.call_args
        prompt = call_args[0][0]
        self.assertIn("通用课程", prompt)
    
    def test_generate_explanation_specific(self):
        self.ai_service.generate_explanation("Chapter 1", "Concept A", "concept", course_name="操作系统")
        call_args = self.ai_service._make_request.call_args
        prompt = call_args[0][0]
        self.assertIn("操作系统", prompt)
        self.assertNotIn("数据库", prompt)
        
    def test_generate_questions_generic(self):
        self.ai_service.generate_questions("Choice", ["Ch1"], count=5)
        call_args = self.ai_service._make_request.call_args
        prompt = call_args[0][0]
        self.assertIn("通用课程", prompt)
        self.assertNotIn("数据库", prompt)
        
    def test_review_answers_generic(self):
        self.ai_service.review_answers("Q&A", course_name="Python编程")
        call_args = self.ai_service._make_request.call_args
        prompt = call_args[0][0]
        self.assertIn("Python编程", prompt)
        self.assertNotIn("数据库", prompt)

if __name__ == '__main__':
    unittest.main()
