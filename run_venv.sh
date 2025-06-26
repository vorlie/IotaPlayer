#!/usr/bin/env bash
# Set up a new venv, install dependencies, and run IotaPlayer

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt --ignore-requires-python
python3 main.py
