from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.data_service import process_csv_file, run_python_code, create_visualization, datasets, current_session_id
import pandas as pd

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
        if "error" in dataset_info:
            raise HTTPException(status_code=500, detail=dataset_info["error"])
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


@router.get("/dataset/info")
async def get_dataset_info():
    """
    Diagnostic endpoint to get information about the current dataset.
    Helps with debugging CSV parsing issues.
    """
    if not current_session_id or current_session_id not in datasets:
        return {"error": "No dataset has been uploaded yet."}
    
    df = datasets[current_session_id]
    
    # Get column info
    column_info = []
    for col in df.columns:
        column_info.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "is_numeric": pd.api.types.is_numeric_dtype(df[col].dtype),
            "sample_values": df[col].head(3).tolist(),
            "null_count": df[col].isna().sum(),
            "null_percent": round(df[col].isna().mean() * 100, 2)
        })
    
    return {
        "session_id": current_session_id,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_info": column_info,
        "dtypes_summary": df.dtypes.astype(str).value_counts().to_dict(),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    } 