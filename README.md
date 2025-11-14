# GreenCheck - AI Greenwashing Detector

GreenCheck is a powerful tool for analyzing ad creatives for potential greenwashing claims. This repository contains the full source code for the GreenCheck application, which features a modern, single-page frontend and a robust FastAPI backend.

## Architecture

The application is divided into two main components:

-   **/web**: A static single-page application built with vanilla HTML, CSS, and JavaScript. It provides a clean, modern user interface for uploading ads and viewing analysis results.
-   **/src/app**: A Python-based backend powered by FastAPI. It exposes a simple API for analyzing ad creatives and generating PDF reports. The backend is designed with a modular, service-oriented architecture for clarity and maintainability.

## User System & Premium Features

GreenCheck now includes a full user system with support for premium features.

### User Accounts

-   **Registration & Login:** Users can create an account and log in to access the application.
-   **Onboarding:** New users are guided through a brief onboarding process to personalize their experience.
-   **Analysis History:** All analyses are saved to the user's account and can be viewed in the "History" section.

### Premium vs. Non-Premium

-   **Non-Premium:** Standard users have a limit of **3 analyses per day**.
-   **Premium:** Premium users have access to unlimited analyses and other advanced features.

To make a user a premium member, you can manually set the `is_premium` flag to `true` for the user in the database.

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

Create a `.env` file in the root of the project and add your OpenAI API key and a secret key for signing JWTs:

```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=a_long_random_secret_string
```

**3. Run the application:**

I have created a convenient script that starts both the backend and frontend servers for you.

**On macOS/Linux:**
```bash
# From the root of the project
./run_dev.sh
```

**On Windows:**
```batch
# From the root of the project
.\run_dev.bat
```

Once the script is running, you can access the application at `http://localhost:5500`.

## Testing

The project includes a suite of tests for the backend. To run the tests, use `pytest`:

```bash
pytest
```

The tests for the authentication system are located in `tests/test_auth.py`.
