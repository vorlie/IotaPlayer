@echo off
REM Run IotaPlayer from source (Windows)

if exist .venv (
    call .venv\Scripts\activate
)

python main.py
