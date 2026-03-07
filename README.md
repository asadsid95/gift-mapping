# Flask Group Gifting App

## Overview
This Flask application helps friends and families plan thoughtful, non-repetitive group gifts with minimal effort. It includes features for event management, group gifting, recipient profiles, and gift history.

## Features
- Event and reminder management
- Recipient profiles
- Group gifting with voting and budget setting
- Gift history logging
- User authentication
- Dashboard for key information
- JSON API endpoints under `/api/*`
- OpenAPI specification in `api.yaml`

## Project Structure (MVC Style)
```
.
├── app.py
├── api.yaml
├── mvc_app/
│   ├── __init__.py
│   ├── models.py
│   └── controllers/
│       ├── web.py
│       └── api.py
├── templates/
└── static/
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- AWS CLI (for deployment with Zappa)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd flask-group-gifting-app
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   ```

### Running the Application
1. Start the Flask development server:
   ```bash
   flask run
   ```
2. Open your browser and navigate to `http://127.0.0.1:5000`.

### Deployment
1. Configure AWS credentials:
   ```bash
   aws configure
   ```
2. Deploy the application using Zappa:
   ```bash
   zappa deploy dev
   ```

## Testing
Run the unit tests:
```bash
python3 -m unittest test_app.py
```

## License
This project is licensed under the MIT License.
