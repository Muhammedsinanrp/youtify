# 🎵 Youtify - Cross-Platform Music Player

An elegant, modern, local music player built with Python & PyQt6. Designed to run seamlessly across **Windows**, **macOS**, and **Linux**.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![OS: Windows | macOS | Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

---

## ✨ Features

- 🎧 **Plays All Common Formats**: `.mp3`, `.flac`, `.ogg`, `.wav`, `.m4a`, `.opus`, `.aac`, `.wma`
- 🖥️ **Universal Cross-Platform**: Native look and feel on Windows 10/11, macOS (Intel & Apple Silicon), and all Linux distributions.
- 🎨 **Gorgeous Built-in Themes**:
  - **Midnight** (Sleek dark violet)
  - **Cyberpunk** (High-contrast neon cyan & dark blue)
  - **Sunset** (Warm ember & rose)
  - **Forest** (Natural emerald green)
  - **Light** (Crisp modern light mode)
- 📂 **Auto-Scan & Library Management**: Automatically scans your Music folder or any directory you choose with recursive search.
- 📑 **Custom Playlists & Queue**:
  - Add tracks to queue, play next, reorder, and save into custom playlists.
- 🔍 **Instant Search Filter**: Quickly find any song by title or file name in real-time.
- 🔀 **Shuffle & Repeat**: Full playback control including shuffle, repeat single track, and loop queue.
- 🎚️ **Smooth Seeking & Volume Control**: Interactive position slider with duration timer.
- ⚙️ **Native OS Integration**:
  - Right-click "Open File Location" in native file manager (Windows Explorer, macOS Finder, Linux file managers).
  - Automatically stores preferences in standard OS config directories (`%APPDATA%`, `Application Support`, or `~/.config`).

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Muhammedsinanrp/youtify.git
cd youtify
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Youtify
```bash
python main.py
```

---

## 💻 OS-Specific Instructions

### 🪟 Windows
1. Open PowerShell or Command Prompt.
2. Ensure Python is installed (from [python.org](https://www.python.org/) or Microsoft Store).
3. Run:
   ```powershell
   pip install -r requirements.txt
   python main.py
   ```
4. *(Optional)* Create a standalone `.exe`:
   ```powershell
   pip install pyinstaller
   pyinstaller --noconsole --onefile main.py --name Youtify
   ```

### 🍎 macOS
1. Open Terminal.
2. Install Python via Homebrew if needed:
   ```bash
   brew install python
   ```
3. Install dependencies and run:
   ```bash
   pip3 install -r requirements.txt
   python3 main.py
   ```

### 🐧 Linux (Ubuntu, Debian, Fedora, Arch, etc.)
1. Ensure Python, pip, and Qt audio plugins are installed:
   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip libpulse0 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
     pip install -r requirements.txt
     python3 main.py
     ```
   - **Arch Linux**:
     ```bash
     sudo pacman -S python python-pip qt6-multimedia
     pip install -r requirements.txt
     python3 main.py
     ```
   - **Fedora**:
     ```bash
     sudo dnf install python3 python3-pip
     pip install -r requirements.txt
     python3 main.py
     ```

---

## 🗂️ Configuration & Storage Locations

Settings and playlists are automatically saved in your operating system's standard configuration path:
- **Windows**: `%APPDATA%\Youtify\youtify-config.json`
- **macOS**: `~/Library/Application Support/Youtify/youtify-config.json`
- **Linux**: `~/.config/youtify/youtify-config.json`

---

## 🛠️ Project Structure

```text
youtify/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── setup.py             # Packaging and installation metadata
├── .gitignore           # Git ignore file
└── README.md            # Documentation and instructions
```

---

## 📜 License

This project is licensed under the MIT License - feel free to use, modify, and distribute!
