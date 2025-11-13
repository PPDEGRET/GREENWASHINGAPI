# GreenCheck - AI Greenwashing Detector

GreenCheck is a powerful tool for analyzing ad creatives for potential greenwashing claims. This repository contains the full source code for the GreenCheck application, which features a modern, single-page frontend and a robust FastAPI backend.

## Architecture

The application is divided into two main components:

-   **/web**: A static single-page application built with vanilla HTML, CSS, and JavaScript. It provides a clean, modern user interface for uploading ads and viewing analysis results.
-   **/src/app**: A Python-based backend powered by FastAPI. It exposes a simple API for analyzing ad creatives and generating PDF reports. The backend is designed with a modular, service-oriented architecture for clarity and maintainability.

## Running Locally

To run GreenCheck locally, you will need to have Python and Tesseract OCR installed. You will also need to set up a virtual environment and install the required dependencies.

**1. Set up the environment:**

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

**2. Configure your API keys:**

Create a `.env` file in the root of the project and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

**3. Run the application:**

You will need to run the backend and frontend servers in separate terminals.

**Backend:**

```bash
# From the root of the project
./run_api.sh
```

**Frontend:**

```bash
# From the root of the project, in a separate terminal
python -m http.server 5500 -d web
```

Once both servers are running, you can access the application at `http://localhost:5500`.
