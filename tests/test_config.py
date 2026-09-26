import unittest
from sports2d_gui.config import default_config, get_preset, parse_toml_text, toml_text, validate_config


class TestConfig(unittest.TestCase):
    def test_roundtrip(self):
        cfg = default_config()
        text = toml_text(cfg)
        loaded = parse_toml_text(text)
        assert loaded["base"]["video_input"] == ["demo.mp4"]
        assert loaded["kinematics"]["do_ik"] is False

    def test_validation(self):
        cfg = default_config()
        cfg["base"]["video_input"] = []
        issues = validate_config(cfg)
        assert len(issues) > 0

    def test_presets(self):
        preset = get_preset("高精度・詳細解析 (Performance & Filtered)")
        assert preset["pose"]["mode"] == "performance"
        assert preset["post-processing"]["filter_type"] == "kalman"


if __name__ == "__main__":
    unittest.main()
