from app.env_sync import get_missing_env_defaults
from app.env_sync import sync_env_defaults


def test_get_missing_env_defaults_ignores_arrow_comment_text(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("DEDALUS_API_KEY=secret\n", encoding="utf-8")
    env_example_path = tmp_path / ".env.example"
    env_example_path.write_text(
        "\n".join(
            [
                "# Optional comma-separated navbar keys to show.",
                "# Unset => all optional nav items enabled.",
                "# NAVBAR_ENABLED_ITEMS=lobby,projects,settings",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    status = get_missing_env_defaults(env_path=env_path, env_example_path=env_example_path)

    assert status["missing_keys"] == ["NAVBAR_ENABLED_ITEMS"]
    assert status["missing_entries"] == [("NAVBAR_ENABLED_ITEMS", "lobby,projects,settings")]


def test_sync_env_defaults_does_not_append_arrow_comment_text(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("DEDALUS_API_KEY=secret\n", encoding="utf-8")
    env_example_path = tmp_path / ".env.example"
    env_example_path.write_text(
        "\n".join(
            [
                "# Unset => all optional nav items enabled.",
                "# Empty value => all optional nav items hidden.",
                "# NAVBAR_ENABLED_ITEMS=lobby,projects,settings",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = sync_env_defaults(env_path=env_path, env_example_path=env_example_path)
    synced = env_path.read_text(encoding="utf-8")

    assert result["updated"] is True
    assert result["added_count"] == 1
    assert "NAVBAR_ENABLED_ITEMS=lobby,projects,settings" in synced
    assert "Unset=> all optional nav items enabled." not in synced
    assert "Empty=> all optional nav items hidden." not in synced
