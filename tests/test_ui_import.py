import unittest
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from sports2d_gui.app import MainWindow
from sports2d_gui.views import (
    AdvancedView, AnglesView, CalibView, EnvView, KinematicsView,
    OutputView, PoseView, PostView, ProjectView, ResultsView,
)

app = QApplication.instance() or QApplication(sys.argv)


class TestUIImport(unittest.TestCase):
    def test_instantiate_views(self):
        views = [
            ProjectView, PoseView, CalibView, AnglesView, PostView,
            KinematicsView, OutputView, AdvancedView, ResultsView, EnvView
        ]
        for v in views:
            instance = v()
            self.assertIsNotNone(instance)

    def test_main_window_instantiation(self):
        window = MainWindow()
        self.assertIsNotNone(window)


if __name__ == "__main__":
    unittest.main()
