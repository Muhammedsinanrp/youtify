#!/usr/bin/env python3
"""
Youtify - Elegant Cross-Platform Local Music Player
Supports Windows, macOS, and Linux
"""

import sys
import os
import json
import random
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QLabel,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QInputDialog,
    QMenu,
    QFrame,
    QSplitter,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Supported audio extensions across Windows, Mac, and Linux
EXTS = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".opus", ".aac", ".wma"}

def get_config_path() -> Path:
    """Return an OS-idiomatic configuration file path."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / "Youtify" / "youtify-config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Youtify" / "youtify-config.json"
    else:
        # Linux and Unix-like systems
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg_config) if xdg_config else Path.home() / ".config"
        return base / "youtify" / "youtify-config.json"

def get_default_music_dir() -> str:
    """Return standard user Music directory if present, else user home."""
    music = Path.home() / "Music"
    if music.exists():
        return str(music)
    return str(Path.home())

CFG_FILE = get_config_path()

THEMES = {
    "Midnight": {
        "bg": "#0f111a",
        "panel": "#191c28",
        "panel_alt": "#212536",
        "fg": "#e2e8f0",
        "muted": "#8892b0",
        "accent": "#7c5cff",
        "accent_hover": "#9373ff",
    },
    "Cyberpunk": {
        "bg": "#0d0f18",
        "panel": "#171a29",
        "panel_alt": "#20253b",
        "fg": "#f1f5f9",
        "muted": "#94a3b8",
        "accent": "#00e5ff",
        "accent_hover": "#33ebff",
    },
    "Sunset": {
        "bg": "#191217",
        "panel": "#261b23",
        "panel_alt": "#33242f",
        "fg": "#fde8e9",
        "muted": "#b89da9",
        "accent": "#ff5c77",
        "accent_hover": "#ff758c",
    },
    "Forest": {
        "bg": "#0e1713",
        "panel": "#16241e",
        "panel_alt": "#1f332a",
        "fg": "#e6f4ea",
        "muted": "#8da396",
        "accent": "#2ecc71",
        "accent_hover": "#48d584",
    },
    "Light": {
        "bg": "#f8fafc",
        "panel": "#ffffff",
        "panel_alt": "#f1f5f9",
        "fg": "#0f172a",
        "muted": "#64748b",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
    },
}

def fmt(ms: int) -> str:
    """Format milliseconds into m:ss format."""
    s = max(ms, 0) // 1000
    return f"{s // 60}:{s % 60:02d}"

class Player(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Youtify")
        self.resize(1020, 660)
        self.setMinimumSize(800, 520)

        # Default configuration
        self.cfg = {
            "folder": get_default_music_dir(),
            "theme": "Midnight",
            "volume": 75,
            "playlists": {},
        }
        self.load_config()

        self.library = []
        self.queue = []
        self.idx = -1
        self.shown = []

        # Audio backend
        self.audio = QAudioOutput()
        self.media = QMediaPlayer()
        self.media.setAudioOutput(self.audio)
        self.audio.setVolume(self.cfg.get("volume", 75) / 100.0)

        self.media.positionChanged.connect(self.on_pos)
        self.media.durationChanged.connect(self.on_duration)
        self.media.mediaStatusChanged.connect(self.on_status)

        self.build_ui()
        self.apply_theme()
        self.scan()

    def load_config(self):
        if CFG_FILE.exists():
            try:
                data = json.loads(CFG_FILE.read_text(encoding="utf-8"))
                self.cfg.update(data)
            except Exception as e:
                print(f"[Youtify] Could not read config: {e}", file=sys.stderr)

    def save_config(self):
        try:
            CFG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CFG_FILE.write_text(json.dumps(self.cfg, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[Youtify] Could not save config: {e}", file=sys.stderr)

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Content splitter (Sidebar + Main list)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Sidebar ---
        side_widget = QWidget()
        side_layout = QVBoxLayout(side_widget)
        side_layout.setContentsMargins(0, 0, 8, 0)
        side_layout.setSpacing(8)

        # App Brand Header
        brand_label = QLabel("🎵 Youtify")
        brand_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 4px 0;")
        side_layout.addWidget(brand_label)

        # Navigation: Library, Queue, and Playlists
        self.nav = QListWidget()
        self.nav.addItem("📁 Library")
        self.nav.addItem("📑 Queue")
        self.nav.currentRowChanged.connect(self.show_view)
        side_layout.addWidget(self.nav)

        # Actions
        btn_folder = QPushButton("📂 Choose Folder…")
        btn_folder.clicked.connect(self.pick_folder)
        side_layout.addWidget(btn_folder)

        btn_playlist = QPushButton("➕ New Playlist…")
        btn_playlist.clicked.connect(self.new_playlist)
        side_layout.addWidget(btn_playlist)

        # Theme Selector
        theme_lbl = QLabel("Theme")
        theme_lbl.setStyleSheet("font-size: 11px; opacity: 0.8; margin-top: 6px;")
        side_layout.addWidget(theme_lbl)

        self.theme_box = QComboBox()
        self.theme_box.addItems(list(THEMES.keys()))
        if self.cfg["theme"] in THEMES:
            self.theme_box.setCurrentText(self.cfg["theme"])
        self.theme_box.currentTextChanged.connect(self.set_theme)
        side_layout.addWidget(self.theme_box)

        side_widget.setMaximumWidth(230)
        side_widget.setMinimumWidth(170)
        content_splitter.addWidget(side_widget)

        # --- Main Area ---
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(4, 0, 0, 0)
        main_layout.setSpacing(8)

        # Search box with clear button
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search tracks, artists, filenames…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.show_view)
        search_row.addWidget(self.search)
        main_layout.addLayout(search_row)

        # Track list view
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.play_item)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)
        main_layout.addWidget(self.list)

        # Status text (track count)
        self.status_bar_lbl = QLabel("0 tracks")
        self.status_bar_lbl.setStyleSheet("font-size: 11px; opacity: 0.7;")
        main_layout.addWidget(self.status_bar_lbl)

        content_splitter.addWidget(main_widget)
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)
        layout.addWidget(content_splitter, stretch=1)

        # --- Player Control Bar ---
        player_frame = QFrame()
        player_frame.setObjectName("PlayerBar")
        bar_layout = QHBoxLayout(player_frame)
        bar_layout.setContentsMargins(12, 10, 12, 10)
        bar_layout.setSpacing(10)

        # Controls: Prev, Play/Pause, Next
        self.btn = {}
        for k, icon_text, fn, tooltip in [
            ("prev", "⏮", self.prev, "Previous Track"),
            ("play", "▶", self.toggle, "Play / Pause"),
            ("next", "⏭", self.next, "Next Track"),
        ]:
            b = QPushButton(icon_text)
            b.setToolTip(tooltip)
            b.setFixedSize(38, 38)
            b.clicked.connect(fn)
            self.btn[k] = b
            bar_layout.addWidget(b)

        # Shuffle & Repeat toggles
        self.shuffle = QPushButton("🔀")
        self.shuffle.setCheckable(True)
        self.shuffle.setToolTip("Shuffle Queue")
        self.shuffle.setFixedSize(36, 36)
        bar_layout.addWidget(self.shuffle)

        self.repeat = QPushButton("🔁")
        self.repeat.setCheckable(True)
        self.repeat.setToolTip("Repeat Current Track")
        self.repeat.setFixedSize(36, 36)
        bar_layout.addWidget(self.repeat)

        # Currently Playing Info
        self.title = QLabel("Nothing playing")
        self.title.setMinimumWidth(180)
        self.title.setMaximumWidth(260)
        self.title.setStyleSheet("font-weight: 600;")
        bar_layout.addWidget(self.title)

        # Seek Slider & Time
        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.sliderMoved.connect(self.media.setPosition)
        bar_layout.addWidget(self.seek, stretch=1)

        self.time = QLabel("0:00 / 0:00")
        self.time.setMinimumWidth(90)
        self.time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_layout.addWidget(self.time)

        # Volume icon & Slider
        vol_icon = QLabel("🔊")
        bar_layout.addWidget(vol_icon)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self.cfg.get("volume", 75)))
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.setToolTip("Volume")
        self.vol_slider.valueChanged.connect(self.on_volume_changed)
        bar_layout.addWidget(self.vol_slider)

        layout.addWidget(player_frame)

    def on_volume_changed(self, v: int):
        self.audio.setVolume(v / 100.0)
        self.cfg["volume"] = v
        self.save_config()

    def apply_theme(self):
        tname = self.cfg.get("theme", "Midnight")
        t = THEMES.get(tname, THEMES["Midnight"])

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t['bg']};
                color: {t['fg']};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
                font-size: 13px;
            }}
            #PlayerBar {{
                background-color: {t['panel']};
                border-radius: 10px;
                border: 1px solid {t['panel_alt']};
            }}
            QListWidget, QLineEdit, QComboBox {{
                background-color: {t['panel']};
                border: 1px solid {t['panel_alt']};
                border-radius: 8px;
                padding: 6px 10px;
                color: {t['fg']};
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-radius: 6px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {t['accent']};
                color: #ffffff;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {t['panel_alt']};
            }}
            QPushButton {{
                background-color: {t['panel']};
                border: 1px solid {t['panel_alt']};
                border-radius: 8px;
                padding: 7px 12px;
                color: {t['fg']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {t['panel_alt']};
                border-color: {t['accent']};
            }}
            QPushButton:checked {{
                background-color: {t['accent']};
                color: #ffffff;
                border-color: {t['accent']};
            }}
            QSlider::groove:horizontal {{
                height: 4px;
                background: {t['panel_alt']};
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {t['accent']};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {t['accent']};
                border: 2px solid #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {t['accent_hover']};
            }}
            QMenu {{
                background-color: {t['panel']};
                color: {t['fg']};
                border: 1px solid {t['panel_alt']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {t['accent']};
                color: #ffffff;
            }}
        """)

    def set_theme(self, name: str):
        if name in THEMES:
            self.cfg["theme"] = name
            self.apply_theme()
            self.save_config()

    def scan(self):
        folder_str = self.cfg.get("folder", "")
        root = Path(folder_str) if folder_str else None
        tracks = []
        if root and root.exists() and root.is_dir():
            try:
                for p in root.rglob("*"):
                    if p.is_file() and p.suffix.lower() in EXTS:
                        tracks.append(str(p.resolve()))
            except Exception as e:
                print(f"[Youtify] Error scanning folder {root}: {e}", file=sys.stderr)

        self.library = sorted(tracks, key=lambda x: Path(x).stem.lower())
        self.refresh_nav()
        self.show_view()

    def refresh_nav(self):
        self.nav.blockSignals(True)
        cur = self.nav.currentRow()
        while self.nav.count() > 2:
            self.nav.takeItem(2)
        playlists = self.cfg.get("playlists", {})
        for name in playlists:
            self.nav.addItem(f"🎵 {name}")
        self.nav.setCurrentRow(max(cur, 0))
        self.nav.blockSignals(False)

    def view_tracks(self):
        r = self.nav.currentRow()
        if r <= 0:
            return self.library
        elif r == 1:
            return self.queue
        else:
            item = self.nav.item(r)
            if item:
                name = item.text()[2:].strip()
                return self.cfg.get("playlists", {}).get(name, [])
            return []

    def show_view(self, *_):
        q = self.search.text().lower().strip()
        tracks = self.view_tracks()
        if q:
            self.shown = [t for t in tracks if q in Path(t).stem.lower()]
        else:
            self.shown = list(tracks)

        self.list.clear()
        for t in self.shown:
            stem = Path(t).stem
            item = QListWidgetItem(stem)
            item.setToolTip(t)
            self.list.addItem(item)

        self.status_bar_lbl.setText(f"{len(self.shown)} tracks")

    def pick_folder(self):
        current = self.cfg.get("folder", str(Path.home()))
        d = QFileDialog.getExistingDirectory(self, "Select Music Folder", current)
        if d:
            self.cfg["folder"] = d
            self.save_config()
            self.scan()

    def new_playlist(self):
        name, ok = QInputDialog.getText(self, "New Playlist", "Enter playlist name:")
        if ok and name.strip():
            n = name.strip()
            self.cfg.setdefault("playlists", {})
            self.cfg["playlists"].setdefault(n, [])
            self.save_config()
            self.refresh_nav()

    def context_menu(self, pos):
        row = self.list.currentRow()
        if row < 0 or row >= len(self.shown):
            return

        track = self.shown[row]
        menu = QMenu(self)

        act_play_next = menu.addAction("⏭ Play Next")
        act_play_next.triggered.connect(lambda: self.queue.insert(self.idx + 1, track))

        act_add_queue = menu.addAction("📑 Add to Queue")
        act_add_queue.triggered.connect(lambda: self.queue.append(track))

        # Add to playlist submenu
        playlists = self.cfg.get("playlists", {})
        if playlists:
            pl_menu = menu.addMenu("🎵 Add to Playlist")
            for pl_name in playlists:
                action = pl_menu.addAction(pl_name)
                action.triggered.connect(lambda checked=False, p=pl_name, t=track: self.add_to_playlist(p, t))

        # If currently in Queue view, offer Remove from Queue
        if self.nav.currentRow() == 1:
            act_rm = menu.addAction("🗑 Remove from Queue")
            act_rm.triggered.connect(lambda: self.remove_from_queue(track))

        # If currently in a Playlist view, offer Remove from Playlist
        if self.nav.currentRow() > 1:
            act_rm_pl = menu.addAction("🗑 Remove from Playlist")
            act_rm_pl.triggered.connect(lambda: self.remove_from_current_playlist(track))

        menu.addSeparator()
        act_open_dir = menu.addAction("📂 Open File Location")
        act_open_dir.triggered.connect(lambda: self.open_file_location(track))

        menu.exec(self.list.mapToGlobal(pos))

    def add_to_playlist(self, playlist_name: str, track_path: str):
        pls = self.cfg.setdefault("playlists", {})
        if playlist_name in pls:
            if track_path not in pls[playlist_name]:
                pls[playlist_name].append(track_path)
                self.save_config()

    def remove_from_queue(self, track: str):
        if track in self.queue:
            self.queue.remove(track)
            self.show_view()

    def remove_from_current_playlist(self, track: str):
        r = self.nav.currentRow()
        if r > 1:
            name = self.nav.item(r).text()[2:].strip()
            pls = self.cfg.get("playlists", {})
            if name in pls and track in pls[name]:
                pls[name].remove(track)
                self.save_config()
                self.show_view()

    def open_file_location(self, track: str):
        path = Path(track)
        if not path.exists():
            return
        if sys.platform == "win32":
            os.system(f'explorer /select,"{path.resolve()}"')
        elif sys.platform == "darwin":
            os.system(f'open -R "{path.resolve()}"')
        else:
            os.system(f'xdg-open "{path.parent.resolve()}"')

    def play_item(self, item):
        row = self.list.row(item)
        if 0 <= row < len(self.shown):
            self.queue = list(self.shown)
            self.idx = row
            self.play()

    def play(self):
        if not (0 <= self.idx < len(self.queue)):
            return
        track = self.queue[self.idx]
        file_path = Path(track)
        if not file_path.exists():
            QMessageBox.warning(self, "File Not Found", f"Cannot find audio file:\n{track}")
            return
        self.media.setSource(QUrl.fromLocalFile(track))
        self.media.play()
        self.title.setText(file_path.stem[:40])
        self.btn["play"].setText("⏸")

    def toggle(self):
        if self.media.isPlaying():
            self.media.pause()
            self.btn["play"].setText("▶")
        elif self.queue:
            if self.media.source().isEmpty():
                self.idx = max(self.idx, 0)
                self.play()
            else:
                self.media.play()
                self.btn["play"].setText("⏸")

    def next(self):
        if not self.queue:
            return
        if self.shuffle.isChecked() and len(self.queue) > 1:
            self.idx = random.randrange(len(self.queue))
        else:
            self.idx = (self.idx + 1) % len(self.queue)
        self.play()

    def prev(self):
        if not self.queue:
            return
        self.idx = (self.idx - 1) % len(self.queue)
        self.play()

    def on_pos(self, p: int):
        self.seek.setValue(p)
        dur = self.media.duration()
        self.time.setText(f"{fmt(p)} / {fmt(dur)}")

    def on_duration(self, d: int):
        self.seek.setRange(0, d)
        self.time.setText(f"{fmt(self.media.position())} / {fmt(d)}")

    def on_status(self, s):
        if s == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.repeat.isChecked():
                self.play()
            elif self.idx < len(self.queue) - 1 or self.shuffle.isChecked():
                self.next()
            else:
                self.btn["play"].setText("▶")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Youtify")
    player = Player()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
