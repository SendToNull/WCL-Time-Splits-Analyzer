# WCL Time Splits Analyzer

A Flask web application for analyzing and comparing Warcraft Logs (WCL) combat reports. Provides detailed timing analysis with multiple run comparisons and timeline visualization.

## Features

- **Multi-Run Comparison**: Compare timing data across multiple WarcraftLogs reports
- **Best Segments Analysis**: Calculate theoretical best run times using individual boss segments
- **Timeline Visualization**: Interactive timeline showing fight progression
- **Zone Support**: Supports multiple WoW Classic raid zones including Naxxramas, AQ40, BWL, and more
- **Wing Analysis**: Special Naxxramas wing timing calculations
- **Delta Calculations**: Compare performance differences between runs

## Project Structure

```
├── src/                    # Source code
│   ├── app.py             # Main Flask application
│   └── config.py          # Configuration management
├── templates/             # HTML templates
├── tests/                 # Test files
├── scripts/               # Deployment and utility scripts
├── debug/                 # Debug files (excluded from git)
├── docs/                  # Documentation
├── wsgi.py               # WSGI entry point for deployment
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── .env.example          # Environment variables template
```

## Installation

### Prerequisites

- Python 3.8+
- WarcraftLogs API key (get from https://www.warcraftlogs.com/profile)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SendToNull/WCL-Time-Splits-Analyzer.git
   cd WCL-Time-Splits-Analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your WCL_API_KEY
   ```

4. **Run the application**:
   ```bash
   python wsgi.py
   ```

The application will be available at `http://localhost:8080`

## Configuration

### Environment Variables

- `WCL_API_KEY`: Your WarcraftLogs API key (required)
- `SECRET_KEY`: Flask secret key (required for production)
- `FLASK_ENV`: Environment mode (`development`, `production`, `testing`)
- `PORT`: Server port (default: 8080)
- `HOST`: Server host (default: 0.0.0.0)
- `REQUEST_TIMEOUT`: API request timeout in seconds (default: 30)

### Production Configuration

For production deployment, ensure these environment variables are set:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export WCL_API_KEY=your-wcl-api-key
```

## Deployment

### Docker Deployment

Build and run with Docker:

```bash
docker build -t wcl-analyzer .
docker run -p 8080:8080 -e WCL_API_KEY=your-api-key -e SECRET_KEY=your-secret-key wcl-analyzer
```

### Google Cloud Run Deployment

Deploy to Google Cloud Run using the following command:

```bash
gcloud run deploy wcl-analyzer \
  --source . \
  --region us-central1 \
  --set-env-vars "WCL_API_KEY=your-wcl-api-key,SECRET_KEY=your-secret-key" \
  --allow-unauthenticated
```

**Prerequisites for Cloud Run deployment:**
- Google Cloud SDK installed and configured
- Docker installed (for building the container)
- Valid WarcraftLogs API key
- Google Cloud project with Cloud Run API enabled

**Important Notes:**
- The application uses `wsgi.py` as the WSGI entry point to avoid circular import issues
- Both `WCL_API_KEY` and `SECRET_KEY` environment variables are required for production deployment
- The Dockerfile is configured to run with gunicorn for production-ready performance

### Environment Variables for Production

When deploying to production environments, ensure these variables are set:

```bash
# Required
WCL_API_KEY=your-warcraftlogs-api-key
SECRET_KEY=your-secure-random-secret-key

# Optional
FLASK_ENV=production
PORT=8080
HOST=0.0.0.0
REQUEST_TIMEOUT=30
```

## API Endpoints

### `POST /api/analyze`

Analyze WarcraftLogs reports.

**Request Body**:
```json
{
  "reports": ["report_id_1", "report_id_2"]
}
```

**Response**:
```json
{
  "results": [
    {
      "title": "Raid Title",
      "zone": "Naxxramas",
      "date": "January 15, 2024",
      "total_duration": 3600000,
      "fights": [...],
      "timeline_data": [...]
    }
  ]
}
```

### `GET /health`

Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00.000Z"
}
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_timing.py
```

### Project Structure Guidelines

- **src/**: Main application code
- **tests/**: All test files
- **templates/**: Jinja2 HTML templates
- **scripts/**: Deployment and utility scripts
- **debug/**: Debug files (git-ignored)

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions with docstrings
- Keep configuration in `src/config.py`

## Supported Zones

- **Classic**: Molten Core, Blackwing Lair, Temple of Ahn'Qiraj, Naxxramas
- **Season of Discovery**: Blackfathom Deeps, Gnomeregan, BWL, AQ40, Naxx
- **Era**: Temple of Ahn'Qiraj, Naxxramas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- WarcraftLogs for providing the API
- Original Google Apps Script implementation for timing logic reference
