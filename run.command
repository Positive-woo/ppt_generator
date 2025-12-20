#!/bin/bash

cd "$(dirname "$0")"

uv run streamlit run app.py \
  --server.port 8502 \
  --server.headless true &

sleep 2
open http://localhost:8502
