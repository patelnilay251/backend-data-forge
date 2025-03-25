# DataForge Backend

A FastAPI-based backend for the DataForge application that handles:
- CSV file uploads and processing
- Python code execution
- Data visualization generation

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

3. Run the server:
```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

- `POST /upload` - Upload and process a CSV file
- `POST /execute` - Execute Python code with access to the uploaded dataset
- `POST /visualize` - Generate visualizations based on the uploaded dataset

## Documentation

Once the server is running, you can access the API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Security Note

The code execution endpoint uses Python's `exec()` function, which can execute arbitrary code. This is suitable for development but should be secured for production use, preferably by:
- Running in a container or sandbox
- Limiting available libraries and functions
- Adding timeout limits for execution 