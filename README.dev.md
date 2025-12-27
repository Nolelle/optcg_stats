# Development Setup with Hot Reload

This project includes a development Docker Compose setup with hot reload for both frontend and backend.

## Quick Start

```bash
# Start development environment with hot reload
docker-compose -f docker-compose.dev.yml up --build

# Or run in detached mode
docker-compose -f docker-compose.dev.yml up --build -d

# Stop the development environment
docker-compose -f docker-compose.dev.yml down
```

## Features

- **Frontend Hot Reload**: Changes to React/TypeScript files automatically reload in the browser
- **Backend Hot Reload**: Changes to Python files automatically restart the FastAPI server
- **Volume Mounts**: Source code is mounted into containers, so changes are immediately visible

## Ports

- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Production Build

For production builds, use the regular docker-compose:

```bash
docker-compose up --build
```

## Troubleshooting

If changes aren't showing up:
1. Make sure you're using `docker-compose.dev.yml` (not the regular `docker-compose.yml`)
2. Check that volumes are mounted correctly: `docker-compose -f docker-compose.dev.yml ps`
3. Restart the containers: `docker-compose -f docker-compose.dev.yml restart`
