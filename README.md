# FastAPI Caching Service

## 📌 Overview
This project is a FastAPI-based web service that caches transformed string inputs to optimize repeated computations. It includes:
- FastAPI as the web framework
- SQLite as the database
- SQLModel for ORM
- Hash-based caching mechanism to avoid redundant transformations
- Unit tests for API validation
- Docker setup for easy deployment

## 🚀 Features
- Accepts two lists of strings, applies a transformation, and caches the results.
- Generates a unique identifier for interleaved transformed data.
- Allows retrieving stored results via the identifier.
- Uses SQLite for lightweight storage.

## 📂 Project Structure
```
project-root/
│── caching-service/       # Main project directory
│   │── cache_fastapi/     # FastAPI application
│   │   │── fast_api.py    # FastAPI setup and endpoints
│   │   │── main.py        # Entry point
│   │   │── test_api.py    # Unit tests for API endpoints
│   │── screenshots/       # Screenshots and assets
│── .dockerignore          # Excludes unnecessary files from Docker image
│── Dockerfile             # Docker configuration
│── README.md              # Documentation
│── requirements.txt       # Dependencies
```

## 🛠️ Installation
### Prerequisites
- Python 3.9+
- Docker (optional for containerized deployment)

### Install Dependencies
```sh
pip install -r requirements.txt
```

## ▶️ Running the Application
### Locally
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```
API is accessible at: [http://localhost:8000/docs](http://localhost:8000/docs)

### With Docker
1. **Build the Docker image**
   ```sh
   docker build -t fastapi-caching-service .
   ```
2. **Run the container**
   ```sh
   docker run -p 8000:8000 fastapi-caching-service
   ```

## 🔍 API Endpoints
### **1️⃣ Store and Retrieve Transformed Data**
#### `POST /payload`
- **Request Body:**
  ```json
  {
    "list_1": ["hello", "world"],
    "list_2": ["fast", "api"]
  }
  ```
- **Response:**
  ```json
  {
    "identifier": "some-unique-hash"
  }
  ```

#### `GET /payload/{identifier}`
- **Response:**
  ```json
  {
    "output": "HELLO, FAST, WORLD, API"
  }
  ```

## 🧪 Running Tests
```sh
pytest test_main.py
```

## 📦 Deployment
For production, use:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

🚀 **Happy Coding!**

