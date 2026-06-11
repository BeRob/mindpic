import unittest
from unittest.mock import Mock, patch
from pathlib import Path

from mindpic import settings
from mindpic.colorize import generate_timestamp, is_timestamp_line, iter_blocks
from mindpic.app import MindPicApp


class FakeText:
    def __init__(self, initial="note"):
        self.value = initial
        self.inserts = []

    def get(self, start, end):
        assert (start, end) == ("1.0", "end-1c")
        return self.value

    def index(self, mark):
        assert mark == "insert"
        return "1.4"

    def insert(self, mark, text):
        assert mark == "insert"
        self.inserts.append(text)
        self.value += text


class SaveBehaviorTests(unittest.TestCase):
    def make_app(self):
        app = MindPicApp.__new__(MindPicApp)
        app.config = {"example": True}
        app.ui = Mock()
        app.ui.text = FakeText("note")
        app._save_geometry = Mock()
        app._recolorize = Mock()
        return app

    @patch("mindpic.app.save_config")
    @patch("mindpic.app.save_content")
    def test_autosave_state_save_does_not_insert_timestamp(self, save_content, save_config):
        app = self.make_app()

        app.save_current_state()

        self.assertEqual(app.ui.text.inserts, [])
        save_content.assert_called_once_with("note")
        save_config.assert_called_once_with(app.config)
        app._save_geometry.assert_called_once()
        app._recolorize.assert_not_called()

    @patch("mindpic.app.save_config")
    @patch("mindpic.app.save_content")
    def test_explicit_save_inserts_timestamp_before_saving(self, save_content, save_config):
        app = self.make_app()

        app.save_with_timestamp()

        self.assertEqual(len(app.ui.text.inserts), 1)
        self.assertTrue(app.ui.text.inserts[0].startswith("\n"))
        save_content.assert_called_once()
        saved_text = save_content.call_args.args[0]
        self.assertIn("note\n", saved_text)
        self.assertRegex(saved_text, r"\d{2}-\d{2}-\d{4} \d{2}:\d{2}")
        app._recolorize.assert_called_once()


class TimestampTests(unittest.TestCase):
    def test_generated_timestamp_is_plain_and_detected(self):
        ts = generate_timestamp()
        self.assertRegex(ts, r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$")
        self.assertTrue(is_timestamp_line(ts + " private note"))

    def test_blocks_detect_plain_timestamps(self):
        lines = [
            "09-06-2026 12:00 first\n",
            "body\n",
            "09-06-2026 12:05 second\n",
        ]
        self.assertEqual(iter_blocks(lines), [(0, 2), (2, 3)])


class PathTests(unittest.TestCase):
    def test_default_dev_project_path_is_repo_root_not_hardcoded_windows_path(self):
        self.assertNotIn("D:", str(settings.DEV_PROJECT_PATH))
        self.assertEqual(settings.DEV_PROJECT_PATH, Path(__file__).resolve().parents[1])


class BorderlessMenuTests(unittest.TestCase):
    def test_menu_borderless_toggle_passes_ui_and_resizer(self):
        app = MindPicApp.__new__(MindPicApp)
        app.root = Mock()
        app.config = {}
        app.ui = Mock()
        app._dragger = Mock()
        app._resizer = Mock()
        app._schedule_config_save = Mock()

        with patch("mindpic.app.ui_mod.apply_borderless") as apply_borderless:
            app._menu_set_borderless(True)

        apply_borderless.assert_called_once_with(
            app.root,
            enabled=True,
            dragger=app._dragger,
            ui=app.ui,
            resizer=app._resizer,
        )
        app._schedule_config_save.assert_called_once()


class HotkeyToggleTests(unittest.TestCase):
    def make_app(self):
        app = MindPicApp.__new__(MindPicApp)
        app.root = Mock()
        app._visible = True
        app._last_hotkey_toggle_ts = 0.0
        return app

    @patch("mindpic.app.time.time", side_effect=[100.0, 100.05])
    def test_duplicate_f9_events_are_debounced(self, _time):
        app = self.make_app()

        first = app.toggle_visibility_from_hotkey()
        second = app.toggle_visibility_from_hotkey()

        self.assertEqual(first, "break")
        self.assertEqual(second, "break")
        app.root.withdraw.assert_called_once()
        app.root.deiconify.assert_not_called()
        self.assertFalse(app._visible)

    @patch("mindpic.app.time.time", side_effect=[100.0, 100.5])
    def test_separate_f9_presses_still_toggle_back(self, _time):
        app = self.make_app()

        app.toggle_visibility_from_hotkey()
        app.toggle_visibility_from_hotkey()

        app.root.withdraw.assert_called_once()
        app.root.deiconify.assert_called_once()
        self.assertTrue(app._visible)


if __name__ == "__main__":
    unittest.main()
