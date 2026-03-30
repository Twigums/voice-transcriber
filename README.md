# VT (Voice Transcriber)

A robust, modular voice transcription tool for Linux (Wayland/X11).

## Installation & Usage (Nix)

This project uses Nix Flakes for reproducible environments.

### Running Immediately
```bash
# add your user to the input group 
# then run this: 
nix run github:jjamesmartiin/voice-transcriber

# or just run as root (bad practice)
sudo nix run github:jjamesmartiin/voice-transcriber
```

### Hugging Face API Token (for first run)
To download the necessary models from Hugging Face, you need to provide your API token. Create a file named `HF_TOKEN` in the project root directory and paste your token into it. This file is in `.gitignore` and will not be committed. This is only required for the initial download.

**TODO**: Remove this requirement once the model is fully public and does not require access-based authentication.

## Features
- **Global Hotkeys**: Hold `Alt+Shift` to record, release to transcribe.
- **Visual Feedback**: visual overlays and terminal notifications.
- **Low Latency**: Optimized for quick transcription.
- **Privacy-focused**: Runs locally using Faster Whisper.


## Codebase Context 

This section provides a high-level overview of the project's architecture and technology stack to help AI models and developers understand the codebase quickly.

- **Purpose**: Low-latency, privacy-focused voice transcription for Linux desktops (Wayland/X11).
- **Tech Stack**: 
  - **Core**: Python 3.x
  - **Transcription Engine**: `Faster Whisper` (using `CohereLabs/cohere-transcribe-03-2026`).
  - **Global Hotkeys**: `evdev` + `uinput` for Wayland-compatible global keyboard interception.
  - **Audio Engine**: `PyAudio` / `sounddevice`.
  - **Visuals**: `Tkinter` (overlays) or `zenity` (fallback) for desktop notifications.
  - **Packaging**: `Nix` (Flakes) for reproducible builds and environments.
- **Main Entry Points**:
  - `src/main.py`: The main application loop and orchestration.
  - `src/t2.py`: Optimized CLI-based recording and transcription script (standalone).
- **Core Logic**:
  - `src/transcribe2.py`: Model loading, pre-loading, and transcription execution.
  - `src/hotkeys.py`: Low-level keyboard event handling and virtual keyboard device creation.
  - `src/notifications.py`: Multi-platform notification logic (terminal + GUI).

## Contributing

We welcome contributions from everyone and of any type! Whether you're fixing a bug, adding a feature, improving documentation, or just sharing an idea, your help is appreciated.

### How to Contribute
1. **Fork** the repository.
2. **Create a branch** for your feature or fix.
3. **Make your changes**.
4. **Run tests** to ensure everything is working correctly (`nix run .#test`).
5. **Submit a Pull Request** with a clear description of what you've done.

We value all types of contributions, including:
- **Code**: Bug fixes, new features, or performance improvements.
- **Documentation**: Fixing typos, improving clarity, or adding examples.
- **Feedback**: Reporting bugs or suggesting new features via Issues.
- **Design**: Improving visual notifications or UI elements.

## Requirements
- Linux (Wayland or X11)
- Nix package manager
- User must be in `input` group for global hotkeys (or run as root).

### Development Environment
To enter a shell with all dependencies (including Python environment):
```bash
nix develop
```

Then inside the shell:
- Run app: `python src/main.py`

### Testing
- Run all tests: `python -m pytest tests/` (or `nix run .#test`)
- Run specific tests or pass arguments to pytest:
```bash
# Filter tests by keyword
nix run .#test -- -k transcription

# Run with verbose output
nix run .#test -- -v
```
