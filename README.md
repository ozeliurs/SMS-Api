# TL-MR6400 SMS API

A FastAPI-based REST API for sending SMS messages through the TP-Link TL-MR6400 router web interface using Selenium.

## Features

- RESTful API for sending SMS messages
- Secure API key authentication
- Background task processing
- Multi-platform Docker support (AMD64, ARM64, ARMv7, ARMv6)
- Automated retry mechanism on failure

## Prerequisites

- Python 3.9+
- Firefox browser
- Docker (optional)
- Docker Compose (optional)

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/TL-MR6400-SMS-Api
cd TL-MR6400-SMS-Api

# Create and configure your environment variables
cp .env.example .env
# Edit .env with your settings
nano .env

# Run with Docker Compose
docker-compose up -d
```

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the development server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file with the following variables:

```env
BASE_URL=http://192.168.1.1  # Your router's URL
PASSWORD=your_password       # Your router's password
API_KEY=your_api_key        # Your chosen API key for the REST API
```

## API Usage

Send an SMS:
```bash
curl -X POST "http://localhost:8000/send-sms" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
           "phone_number": "+1234567890",
           "message": "Hello, World!"
         }'
```

## Docker Support

The project includes multi-architecture Docker support:

```bash
# Pull the pre-built image
docker pull ghcr.io/yourusername/sms-api:latest

# Or build locally
docker build -t sms-api .

# Run the container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name sms-api \
  sms-api
```

### Supported Architectures
- AMD64 (x86_64)
- ARM64 (aarch64)
- ARMv7 (armhf)
- ARMv6 (Raspberry Pi Zero)

## Project Structure

```
TL-MR6400-SMS-Api/
├── app.py              # FastAPI application
├── sms_sender.py       # SMS sending logic
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── .env               # Environment variables (not in git)
```

## Development

For development work:

1. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black isort
```

2. Format code:
```bash
black .
isort .
```

3. Run tests:
```bash
pytest
```

## API Documentation

After starting the server, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI framework
- Selenium WebDriver
- TP-Link TL-MR6400 router
