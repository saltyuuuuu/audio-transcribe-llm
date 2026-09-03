from audio_transcribe_llm.config import load_dotenv


def test_load_dotenv(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("ARK_API_KEY=test-key\nTEXT_MODEL_ID='deepseek-v4-pro'\n", encoding="utf-8")
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    monkeypatch.delenv("TEXT_MODEL_ID", raising=False)
    load_dotenv(env_path)
    assert __import__("os").environ["ARK_API_KEY"] == "test-key"
    assert __import__("os").environ["TEXT_MODEL_ID"] == "deepseek-v4-pro"

