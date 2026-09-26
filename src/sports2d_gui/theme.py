from __future__ import annotations

DARK_THEME_QSS = """
/* Modern Clean Dark Theme (Linear / Tailwind Inspired) */
QMainWindow, QDialog {
    background-color: #0b0f19;
    color: #f1f5f9;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #cbd5e1;
}

/* Header & Top Bar */
#topHeaderBar {
    background-color: #111827;
    border-bottom: 1px solid #1f2937;
    padding: 8px 16px;
}

#statusBanner {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 14px;
}

/* Sidebar & Navigation */
QListWidget#sidebar {
    background-color: #0f172a;
    border: none;
    border-right: 1px solid #1e293b;
    outline: none;
    padding-top: 8px;
}

QListWidget#sidebar::item {
    padding: 10px 14px;
    border-radius: 6px;
    margin: 2px 8px;
    color: #94a3b8;
    font-weight: 500;
}

QListWidget#sidebar::item:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QListWidget#sidebar::item:selected {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
}

/* Scroll Area */
QScrollArea {
    background-color: #0b0f19;
    border: none;
}

/* Card Widget Container */
CardWidget {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
    border-color: #1e293b;
    opacity: 0.5;
}

/* Primary Run Button */
QPushButton#runButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    font-weight: 700;
    font-size: 13px;
    padding: 8px 20px;
    border-radius: 6px;
}

QPushButton#runButton:hover {
    background-color: #1d4ed8;
}

QPushButton#runButton:pressed {
    background-color: #1e40af;
}

QPushButton#runButton:disabled {
    background-color: #334155;
    color: #64748b;
}

/* Danger Stop Button */
QPushButton#stopButton {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 6px;
}

QPushButton#stopButton:hover {
    background-color: #dc2626;
}

QPushButton#stopButton:disabled {
    background-color: #334155;
    color: #64748b;
}

/* Inputs & Form Elements */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #030712;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QPlainTextEdit:focus {
    border-color: #3b82f6;
    background-color: #0b0f19;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #111827;
    color: #f8fafc;
    selection-background-color: #2563eb;
    border: 1px solid #334155;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #030712;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #60a5fa;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #0b0f19;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0b0f19;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 20px;
    border-radius: 4px;
}

/* Status Bar */
QStatusBar {
    background-color: #0f172a;
    color: #94a3b8;
    border-top: 1px solid #1e293b;
    font-size: 12px;
}

/* Drop Zone */
#dropZone {
    background-color: #0f172a;
    border: 2px dashed #334155;
    border-radius: 10px;
    padding: 16px;
}

#dropZone[dragOver="true"] {
    background-color: #1e293b;
    border-color: #3b82f6;
}
"""
