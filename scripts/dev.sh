#!/bin/bash
# Start both backend and frontend dev servers
trap 'kill 0' EXIT

cd "$(dirname "$0")/.."

echo "Starting backend..."
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

echo "Starting frontend..."
cd ../frontend && npm run dev &

wait
