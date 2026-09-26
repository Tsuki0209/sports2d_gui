from sports2d_gui.config import default_config, parse_toml_text, toml_text, validate_config


def test_roundtrip():
    cfg = default_config()
    text = toml_text(cfg)
    loaded = parse_toml_text(text)
    assert loaded["base"]["video_input"] == ["demo.mp4"]
    assert loaded["kinematics"]["do_ik"] is False


def test_validation():
    cfg = default_config()
    cfg["base"]["video_input"] = []
    assert validate_config(cfg)
