#!/bin/sh
set -e

if [ ! -f /app/.fh3.db ]; then
  echo "🔧 Initializing ForenGeo database..."
  python fh3_cli.py init
fi

echo "🚀 Starting ForenGeo SaaS server..."
exec "$@"
