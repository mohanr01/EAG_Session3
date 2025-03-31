# Weather Monitor Chrome Extension

This Chrome extension allows you to monitor weather using Google's Gemini AI and receive email notifications when the temperature reaches your specified target.

## Features

- Monitor weather different states using Gemini AI
- Set target rates for notifications
- Receive email notifications when target rate is reached
- Browser notifications for rate alerts
- Customizable check intervals
- Real-time rate display

## Prerequisites

1. Python 3.7 or higher
2. Google Gemini API key
3. Gmail account for sending notifications (or other SMTP server)

## Setup

### Python Backend

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key
   - Add your email credentials

4. Start the backend server:
```bash
python app.py
```

### Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right corner
3. Click "Load unpacked" and select the extension directory

## Usage

1. Make sure the Python backend server is running
2. Click the extension icon in your Chrome toolbar
3. Select your country from the dropdown
4. Enter your target gold rate
5. Enter your email address for notifications
6. Choose how often you want to check the rates
7. Click "Start Monitoring"

## Development

The project consists of:

### Backend (Python)
- `app.py`: Flask server with Gemini AI integration
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (create from .env.example)

### Chrome Extension
- `manifest.json`: Extension configuration
- `popup.html`: User interface
- `popup.js`: Popup logic
- `background.js`: Background monitoring script
- `styles.css`: Styling
- `icons/`: Extension icons

## API

The extension uses Google's Gemini AI to fetch current gold rates. Make sure you have:
1. A valid Gemini API key
2. A stable internet connection
3. The Python backend server running locally 
