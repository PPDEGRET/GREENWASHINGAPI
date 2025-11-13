@echo off
ECHO Starting servers...

ECHO Starting backend server in a new window...
start "Backend" cmd /c python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

ECHO Starting frontend server in a new window...
start "Frontend" cmd /c python -m http.server 5500 -d web

ECHO.
ECHO GreenCheck is now running in two separate command prompt windows.
ECHO.
ECHO Frontend: http://localhost:5500
ECHO Backend:  http://localhost:8000
ECHO.
ECHO To stop the servers, simply close the two new windows that opened.
