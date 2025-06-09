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

3. Create a `.env` file in the repository root with any required configuration values. Each service automatically loads environment variables from this file on startup.

4. Run the application:
```bash
uvicorn main:app --reload
```

5. Access the API documentation:
- OpenAPI UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

## Future Enhancements

- OpenAI integration for natural language processing
- Google Calendar integration
- Amazon Shopping API integration
- Real OCR processing
- Barcode scanning
- Voice command processing
- Commute monitoring with NJ Transit + Google Maps APIs 