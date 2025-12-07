# FastAPI Calculator - BREAD Operations

A FastAPI calculator application implementing BREAD (Browse, Read, Edit, Add, Delete) operations for mathematical calculations with user authentication.

## 🚀 How to Run the Application

### Using Docker (Recommended)
```bash
git clone <repository-url>
cd assignmentlm
docker-compose up --build
```

### Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:5050 (admin@example.com / admin)

### Without Docker
```bash
pip install -r requirements.txt
python app/main.py
```

## 🧪 Execute Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests  
pytest tests/e2e/         # End-to-end tests
```

## 🐳 Docker Hub Repository

**Repository**: [shivajiburle/assignmentlm](https://hub.docker.com/r/shivajiburle/assignmentlm)

```bash
# Pull and run from Docker Hub
docker pull shivajiburle/assignmentlm:latest
docker run -p 8000:8000 shivajiburle/assignmentlm:latest
```

## 📋 BREAD Operations

- **Browse** (`GET /calculations`): List user calculations
- **Read** (`GET /calculations/{id}`): Get specific calculation
- **Edit** (`PUT /calculations/{id}`): Update calculation
- **Add** (`POST /calculations`): Create new calculation  
- **Delete** (`DELETE /calculations/{id}`): Remove calculation
