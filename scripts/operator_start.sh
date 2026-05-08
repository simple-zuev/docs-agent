#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

python agent_cli.py doctor-lite
