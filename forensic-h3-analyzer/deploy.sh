#!/bin/bash
pip install -r requirements.txt
chmod +x fh3_cli.py
echo "🚀 FH3 deployed! Run: ./fh3_cli.py --help"
echo "🌐 For web SaaS demo, run: docker build -t forengeo . && docker run --rm -p 5000:5000 forengeo"