import unittest
import os
import sys
import yaml
from unittest.mock import patch, MagicMock

# Add the parent directory to the sys.path to allow importing llm_handler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from llm_handler import LLMHandler
import litellm

class TestLLMHandler(unittest.TestCase):

    def setUp(self):
        # Create a dummy config.yaml for testing
        self.config_path = "./test_config.yaml"
        self.test_api_key = "test_api_key_123"
        self.test_model_name = "test_model"
        self.test_base_url = "http://test.api.com"

        self.default_config_content = {
            "active_model": "litellm",
            "api_key": "YOUR_API_KEY", # Should be overridden by env var in tests
            "model_name": "gpt-3.5-turbo"
        }
        with open(self.config_path, "w") as f:
            yaml.dump(self.default_config_content, f)

        # Set environment variable for API key
        os.environ["LLM_API_KEY"] = self.test_api_key

    def tearDown(self):
        # Clean up dummy config file and environment variable
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        if "LLM_API_KEY" in os.environ:
            del os.environ["LLM_API_KEY"]

    def test_init_loads_config_and_api_key(self):
        handler = LLMHandler(config_path=self.config_path)
        self.assertEqual(handler.active_model, "litellm")
        self.assertEqual(handler.api_key, self.test_api_key)
        self.assertEqual(handler.model_name, "gpt-3.5-turbo")

    def test_init_with_missing_config_file(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        handler = LLMHandler(config_path=self.config_path)
        self.assertEqual(handler.active_model, "litellm") # Default value
        self.assertEqual(handler.api_key, self.test_api_key)

    def test_send_message_no_api_key(self):
        del os.environ["LLM_API_KEY"]
        # Modify config to not have API key either
        no_key_config = {"active_model": "litellm", "model_name": "gpt-3.5-turbo"}
        with open(self.config_path, "w") as f:
            yaml.dump(no_key_config, f)

        handler = LLMHandler(config_path=self.config_path)
        response = handler.send_message("test_agent", "hello")
        self.assertIn("Error: API key not configured", response)

    @patch("litellm.completion")
    def test_send_litellm_message(self, mock_litellm_completion):
        mock_litellm_completion.return_value.choices[0].message.content = "LiteLLM response"
        
        config_content = {
            "active_model": "litellm",
            "model_name": self.test_model_name,
            "base_url": self.test_base_url
        }
        with open(self.config_path, "w") as f:
            yaml.dump(config_content, f)

        handler = LLMHandler(config_path=self.config_path)
        response = handler.send_message("test_agent", "test prompt")

        self.assertEqual(response, "LiteLLM response")
        mock_litellm_completion.assert_called_once_with(
            model=self.test_model_name,
            messages=[{"role": "user", "content": "test prompt"}],
            api_key=self.test_api_key
        )
        self.assertEqual(litellm.api_base, self.test_base_url)

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_send_gemini_message(self, mock_gemini_configure, mock_generative_model):
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance
        mock_model_instance.generate_content.return_value.text = "Gemini response"

        config_content = {
            "active_model": "gemini",
            "model_name": self.test_model_name
        }
        with open(self.config_path, "w") as f:
            yaml.dump(config_content, f)

        handler = LLMHandler(config_path=self.config_path)
        response = handler.send_message("test_agent", "test prompt")

        self.assertEqual(response, "Gemini response")
        mock_gemini_configure.assert_called_once_with(api_key=self.test_api_key)
        mock_generative_model.assert_called_once_with(self.test_model_name)
        mock_model_instance.generate_content.assert_called_once_with("test prompt")

    @patch("requests.post")
    def test_send_qwen_message(self, mock_requests_post):
        mock_response = MagicMock()
        mock_requests_post.return_value = mock_response
        mock_response.json.return_value = {"output": {"text": "Qwen response"}}
        mock_response.raise_for_status.return_value = None

        config_content = {
            "active_model": "qwen",
            "model_name": self.test_model_name,
            "base_url": self.test_base_url
        }
        with open(self.config_path, "w") as f:
            yaml.dump(config_content, f)

        handler = LLMHandler(config_path=self.config_path)
        response = handler.send_message("test_agent", "test prompt")

        self.assertEqual(response, "Qwen response")
        mock_requests_post.assert_called_once_with(
            self.test_base_url,
            headers={
                "Authorization": f"Bearer {self.test_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.test_model_name,
                "input": {
                    "messages": [
                        {"role": "user", "content": "test prompt"}
                    ]
                }
            }
        )

    @patch("anthropic.Anthropic")
    def test_send_claude_message(self, mock_anthropic):
        mock_client_instance = MagicMock()
        mock_anthropic.return_value = mock_client_instance
        mock_client_instance.messages.create.return_value.content[0].text = "Claude response"

        config_content = {
            "active_model": "claude",
            "model_name": self.test_model_name
        }
        with open(self.config_path, "w") as f:
            yaml.dump(config_content, f)

        handler = LLMHandler(config_path=self.config_path)
        response = handler.send_message("test_agent", "test prompt")

        self.assertEqual(response, "Claude response")
        mock_anthropic.assert_called_once_with(api_key=self.test_api_key)
        mock_client_instance.messages.create.assert_called_once_with(
            model=self.test_model_name,
            max_tokens=1000,
            messages=[{"role": "user", "content": "test prompt"}]
        )

if __name__ == "__main__":
    unittest.main()

