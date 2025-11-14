#!/bin/bash
# This script starts both the backend and frontend servers for local development.

# Apply database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the backend server in the background
echo "Starting backend server..."
./run_api.sh &

# Start the frontend server in the background
echo "Starting frontend server..."
python -m http.server 5500 -d web &

# Wait for both servers to start
sleep 2

echo "GreenCheck is now running."
echo "Frontend: http://localhost:5500"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop both servers."

# Wait for user to exit
wait
