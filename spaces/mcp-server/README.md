---
title: MCP Server STT TTS
emoji: 🎙️
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
app_port: 7860
---

# MCP Server - STT & TTS

Model Context Protocol Server providing Speech-to-Text and Text-to-Speech capabilities.

## Features

- **STT (Speech-to-Text)**: Whisper Tiny model (39M params) - Fast, lightweight, CPU-friendly
- **TTS (Text-to-Speech)**: ESPnet VITS model - Natural-sounding speech generation

## Endpoints

- `POST /stt` - Convert audio to text
- `POST /tts` - Convert text to audio
- `GET /health` - Check service status

## Models

- STT: `openai/whisper-tiny` (39M parameters)
- TTS: `espnet/kan-bayashi_ljspeech_vits`

Both models optimized for CPU inference.
