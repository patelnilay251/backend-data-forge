import io
import sys
import traceback
import pandas as pd
import plotly.express as px
import json
from fastapi import UploadFile
import uuid
import os
from typing import Dict, Any, Optional


# Dictionary to store uploaded datasets by session ID
datasets: Dict[str, pd.DataFrame] = {}
current_session_id: Optional[str] = None
# Store the latest result from code execution
latest_result: Any = None


async def process_csv_file(file: UploadFile) -> Dict[str, Any]:
    """
    Process uploaded CSV file and store the dataframe.
    
    Args:
        file: The uploaded CSV file
    
    Returns:
        Dictionary with dataset information (name, rows, columns, preview)
    """
    global current_session_id, latest_result
    
    # Read CSV content
    contents = await file.read()
    file.file.seek(0)  # Reset file pointer for potential reuse
    
    # Parse CSV into DataFrame
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Generate a new session ID and store the dataframe
    current_session_id = str(uuid.uuid4())
    datasets[current_session_id] = df
    latest_result = None
    
    # Build the response with dataset information
    dataset_info = {
        "name": file.filename,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "preview": df.head(5).to_dict(orient="records"),
        "session_id": current_session_id
    }
    
    return dataset_info


async def run_python_code(code: str) -> str:
    """
    Execute Python code with the current dataset available as 'df'.
    
    Args:
        code: Python code to execute
    
    Returns:
        String with execution output or error message
    """
    global datasets, current_session_id, latest_result
    
    if not current_session_id or current_session_id not in datasets:
        return "Error: No dataset has been uploaded yet."
    
    # Get the current dataset
    df = datasets[current_session_id]
    
    # Prepare environment with necessary variables
    env = {
        "df": df,
        "pd": pd,
        "px": px
    }
    
    # Redirect stdout to capture print outputs
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    try:
        # Execute the code
        exec(code, env)
        output = redirected_output.getvalue()
        
        # If there's no stdout output but there might be a return value
        # (which we can't capture directly with exec), check if there's
        # a result variable that might have been created
        if "result" in env:
            if isinstance(env["result"], pd.DataFrame):
                if not output:
                    output = str(env["result"].head())
                latest_result = env["result"]
            elif hasattr(env["result"], 'to_json'):  # For Plotly figures
                latest_result = env["result"]
                if not output:
                    output = "Visualization result generated."
            else:
                if not output:
                    output = str(env["result"])
                latest_result = env["result"]
        
        # Return empty output message if nothing was printed
        if not output:
            output = "Code executed successfully. No output generated."
            
        return output
    except Exception as e:
        # Get the full traceback
        error_traceback = traceback.format_exc()
        return f"Error: {str(e)}\n{error_traceback}"
    finally:
        # Restore stdout
        sys.stdout = old_stdout


async def create_visualization(chart_type: str) -> Dict[str, Any]:
    """
    Create a visualization based on the current dataset.
    
    Args:
        chart_type: Type of chart to create (bar, line, scatter, pie, histogram)
    
    Returns:
        Dictionary with Plotly chart data
    """
    global datasets, current_session_id, latest_result
    
    # If we have a result from code execution that's a Plotly figure,
    # use that instead of creating a new visualization
    if latest_result is not None and hasattr(latest_result, 'to_json'):
        try:
            # Return the figure directly from the latest result
            return json.loads(latest_result.to_json())
        except Exception as e:
            return {"error": f"Error processing visualization result: {str(e)}"}
    
    # Fall back to creating a visualization from the dataset
    if not current_session_id or current_session_id not in datasets:
        return {"error": "No dataset has been uploaded yet."}
    
    df = datasets[current_session_id]
    
    # Basic validation
    if df.empty:
        return {"error": "The dataset is empty."}
    
    try:
        # For simplicity, we'll use the first numeric column for y and first column for x
        # In a real app, this would be configurable
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # If there are no numeric columns initially, try to convert string columns that
        # may contain numeric values (like "123" or "-45.67")
        if not numeric_cols:
            for col in df.select_dtypes(include=['object']).columns:
                try:
                    # Try to convert to numeric
                    df[f"{col}_numeric"] = pd.to_numeric(df[col], errors='coerce')
                    # Keep only if at least 50% values are not NaN
                    if df[f"{col}_numeric"].notna().mean() >= 0.5:
                        numeric_cols.append(f"{col}_numeric")
                except:
                    continue
        
        if not numeric_cols:
            return {"error": "No numeric columns found for visualization. Try running code to transform your data first."}
        
        x_col = df.columns[0]
        y_col = numeric_cols[0]
        
        # Create visualization based on chart type
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=y_col)
        else:
            return {"error": f"Unsupported chart type: {chart_type}"}
        
        # Convert to JSON for frontend rendering
        return json.loads(fig.to_json())
    except Exception as e:
        return {"error": f"Visualization error: {str(e)}"} 