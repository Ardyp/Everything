# Everything App - Local POC

A modular FastAPI application that demonstrates collaboration between three AI agents: Smart Home Orchestrator, Life Organizer, and Inventory Manager.

## Features

### 🏠 Smart Home Orchestrator
- Simulates home automation and monitoring
- Welcomes users with TTS (Text-to-Speech)
- Monitors home status (temperature, security, plants)

### 📅 Life Organizer
- Manages reminders and appointments
- Provides task summaries
- (Future) Google Calendar integration

### 📦 Inventory Manager
- Tracks household inventory
- Processes receipts (simulated OCR)
- Monitors low-stock items

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables like `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY` and `GOOGLE_MAPS_API_KEY`.
4. Run the application:
```bash
python main.py
```
This command runs Uvicorn via the script. You can also call `uvicorn main:app --reload` directly.

5. Access the API documentation:
- OpenAPI UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

Some endpoints require a valid JWT token. Default credentials can be provided
through environment variables:

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=admin
export SECRET_KEY=mysecret
```

1. Obtain a token by sending a POST request to `/token` with `username` and
   `password` form fields:

```bash
curl -X POST -F "username=$ADMIN_USERNAME" -F "password=$ADMIN_PASSWORD" \
     http://localhost:8000/token
```

2. Use the returned `access_token` in the `Authorization` header to access
   protected routes (`/process/*` and `/files/*`):

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/process/list
```

## API Endpoints

### Smart Home (`/smart-home`)
- `POST /arrive` - Handle user arrival
- `GET /status` - Get home status

### Life Organizer (`/organizer`)
- `POST /reminder` - Create reminder
- `GET /reminder` - List reminders
- `POST /appointment` - Book appointment
- `GET /summary` - Get task summary

### Inventory Manager (`/inventory`)
- `POST /upload` - Process receipt
- `GET /snacks` - List snacks
- `POST /inventory/update` - Update inventory
- `GET /inventory/low` - List low-stock items

## Project Structure
```
everything-app/
├── main.py                   # FastAPI app entry point
├── agents/                   # Agent modules
│   ├── smart_home/          # Smart home orchestration
│   ├── life_organizer/      # Task and calendar management
│   └── inventory_manager/   # Inventory tracking
├── shared/                  # Shared utilities
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (create from template)
└── mock_data/              # Mock data for development
```

## Development

- Each agent is implemented as a separate FastAPI router
- Mock data is used for demonstration
- TTS uses pyttsx3 for welcome messages
- In-memory storage is used for POC

## Client Configuration

The client applications read the FastAPI endpoint from environment variables.
Create a `.env` file in the project root (see `.env.example`) and define
`EXPO_PUBLIC_API_URL` to point to your API server. This works for both the web
app (Expo web) and the native mobile build.

## Running the Mobile App

The Expo project lives in the `os-manager-mobile` directory. To start the mobile
client, run:

```bash
cd os-manager-mobile
npx expo start
```


## Future Enhancements

- OpenAI integration for natural language processing
- Google Calendar integration
- Amazon Shopping API integration
- Real OCR processing
- Barcode scanning
- Voice command processing
- Commute monitoring with NJ Transit + Google Maps APIs 