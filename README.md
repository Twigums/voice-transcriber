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


## Features
- **Global Hotkeys**: Hold `Alt+Shift` to record, release to transcribe.
- **Visual Feedback**: visual overlays and terminal notifications.
- **Low Latency**: Optimized for quick transcription.
- **Privacy-focused**: Runs locally using Faster Whisper.

## Project Structure
- `src/`: Source code
  - `main.py`: Entry point and orchestration.
  - `notifications.py`: Visual notification system.
  - `hotkeys.py`: Global hotkey handling.
  - `t2.py` / `transcribe2.py`: Audio recording and transcription logic.
- `tests/`: Feature parity tests.

## Requirements
- Linux (Wayland or X11)
- Nix package manager
- User must be in `input` group for global hotkeys (or run as root).

## Troubleshooting

### Clipboard Issues (Wayland)
If `wl-clipboard` fails to copy text or seems stuck:
- The app now includes a retry mechanism (3 attempts).
- You can manually reset clipboard processes by pressing `r` in the terminal menu after a recording (if prompted) to reset both the terminal and clipboard.
- Alternatively, run:
  ```bash
  pkill wl-copy
  pkill wl-paste
  ```
- Ensure `wl-clipboard` is installed (it is included in the Nix flake).

### Hotkey Issues
- Ensure you have permissions to `/dev/input/`. Add your user to the `input` group:
  ```bash
  sudo usermod -a -G input $USER
  ```
- Then reboot or log out and back in.

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
