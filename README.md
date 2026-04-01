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
- **Global Hotkeys**: Hold `Alt+Shift` to record, release to transcribe & copy to clipboard.
- **Multi-Model Support**: Switch between **Cohere Transcribe** (high quality) and **Faster Whisper** (fast/offline).
- **Visual Feedback**: visual overlays and terminal notifications.
- **Low Latency**: Optimized for quick transcription.
- **Privacy-focused**: Runs locally.

## Model Configuration
You can switch between transcription models in the configuration menu:
1. Press **Ctrl+Alt+I** (or run the app and press **i** in the terminal).
2. Press **M** to toggle between **Cohere** and **Whisper** backends.
3. The setting is saved persistently in your configuration.

### Model Details
- **Cohere Transcribe**: Uses `CohereLabs/cohere-transcribe-03-2026`. Requires a Hugging Face token and access to the gated model.
- **Faster Whisper**: Uses the Whisper `small` model. Fully local and does not require authentication.


## Codebase Context 

This section provides a high-level overview of the project's architecture and technology stack to help AI models and developers understand the codebase quickly.

- **Purpose**: Low-latency, privacy-focused voice transcription for Linux desktops (Wayland/X11).
- **Tech Stack**: 
  - **Core**: Python 3.x
  - **Transcription Engines**:
    - **Cohere**: `CohereLabs/cohere-transcribe-03-2026` via `transformers` (Higher quality, requires gating access).
    - **Faster Whisper**: Using `faster-whisper` (Fast, fully local/offline).
  - **Global Hotkeys**: `evdev` + `uinput` for Wayland-compatible global keyboard interception.
  - **Audio Engine**: `sounddevice` / `PortAudio`.
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
