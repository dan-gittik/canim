#!/bin/bash

set -e
cd "$(dirname "$(dirname "$(realpath "${BASH_SOURCE[0]}" )" )" )"

sudo apt update
sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev ffmpeg portaudio19-dev sox libsox-fmt-all
python -m venv .env --prompt=canim
.env/bin/pip install -r requirements.txt
echo ../../../../ > .env/lib/python3.11/site-packages/self.pth