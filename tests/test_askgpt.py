import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import yaml
from io import StringIO
import askgpt


class TestAskGPT(unittest.TestCase):

    def test_cargar_config_success(self):
        mock_config = {"openai_api_key": "test_key", "model": "gpt-4"}
        with patch("builtins.open", mock_open(read_data=yaml.dump(mock_config))):
            config = askgpt.cargar_config("config.yaml")
            self.assertEqual(config, mock_config)

    def test_cargar_config_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    askgpt.cargar_config("config.yaml")
                    mock_print.assert_called_with("⚠️  Archivo config.yaml no encontrado.")
                    mock_exit.assert_called_with(1)

    def test_cargar_config_yaml_error(self):
        with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")):
            with patch("sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    askgpt.cargar_config("config.yaml")
                    mock_exit.assert_called_with(1)

    @patch('askgpt.OpenAI')
    def test_preguntar_a_gpt_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        config = {"openai_api_key": "test_key", "model": "gpt-4"}
        result = askgpt.preguntar_a_gpt("test question", config)
        
        self.assertEqual(result, "Test response")
        mock_openai.assert_called_with(api_key="test_key")
        mock_client.chat.completions.create.assert_called_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "test question"}],
            temperature=0.7
        )

    @patch('askgpt.OpenAI')
    def test_preguntar_a_gpt_default_model(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        config = {"openai_api_key": "test_key"}
        askgpt.preguntar_a_gpt("test question", config)
        
        mock_client.chat.completions.create.assert_called_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "test question"}],
            temperature=0.7
        )

    @patch('askgpt.OpenAI')
    def test_preguntar_a_gpt_api_error(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        config = {"openai_api_key": "test_key"}
        result = askgpt.preguntar_a_gpt("test question", config)
        
        self.assertIn("❌ Error en la consulta a GPT:", result)
        self.assertIn("API Error", result)

    @patch('askgpt.preguntar_a_gpt')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_modo_interactivo_salir(self, mock_print, mock_input, mock_preguntar):
        mock_input.side_effect = ["salir"]
        config = {"openai_api_key": "test_key"}
        
        askgpt.modo_interactivo(config)
        
        mock_print.assert_called_with("💬 Asistente GPT — Escribí 'salir' para terminar.\n")
        mock_preguntar.assert_not_called()

    @patch('askgpt.preguntar_a_gpt')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_modo_interactivo_pregunta_y_salir(self, mock_print, mock_input, mock_preguntar):
        mock_input.side_effect = ["test question", "exit"]
        mock_preguntar.return_value = "Test response"
        config = {"openai_api_key": "test_key"}
        
        askgpt.modo_interactivo(config)
        
        mock_preguntar.assert_called_once_with("test question", config)
        mock_print.assert_any_call("\nTest response\n")

    @patch('askgpt.modo_interactivo')
    @patch('askgpt.cargar_config')
    def test_main_no_args(self, mock_cargar_config, mock_modo_interactivo):
        mock_config = {"openai_api_key": "test_key"}
        mock_cargar_config.return_value = mock_config
        
        with patch.object(sys, 'argv', ['askgpt.py']):
            askgpt.main()
        
        mock_cargar_config.assert_called_once()
        mock_modo_interactivo.assert_called_once_with(mock_config)

    @patch('askgpt.preguntar_a_gpt')
    @patch('askgpt.cargar_config')
    @patch('builtins.print')
    def test_main_with_args(self, mock_print, mock_cargar_config, mock_preguntar):
        mock_config = {"openai_api_key": "test_key"}
        mock_cargar_config.return_value = mock_config
        mock_preguntar.return_value = "Test response"
        
        with patch.object(sys, 'argv', ['askgpt.py', 'test', 'question']):
            askgpt.main()
        
        mock_cargar_config.assert_called_once()
        mock_preguntar.assert_called_once_with("test question", mock_config)
        mock_print.assert_called_once_with("Test response")


if __name__ == '__main__':
    unittest.main()