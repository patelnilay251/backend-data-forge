from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.data_service import process_csv_file, run_python_code, create_visualization

router = APIRouter()


# Model for code execution request
class CodeRequest(BaseModel):
    code: str


# Model for visualization request
class VisualizationRequest(BaseModel):
    chart_type: str


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload and process a CSV file.
    Returns dataset information including name, rows, columns, and a preview.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        dataset_info = await process_csv_file(file)
        return dataset_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_code(request: CodeRequest):
    """
    Endpoint to execute Python code.
    Receives code as a string and returns the execution output.
    """
    try:
        output = await run_python_code(request.code)
        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visualize")
async def generate_visualization(request: VisualizationRequest):
    """
    Endpoint to generate visualizations.
    Receives chart type and returns chart data for rendering.
    """
    try:
        chart_data = await create_visualization(request.chart_type)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 