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
    
    try:
        # Parse CSV into DataFrame - try to automatically convert numeric columns
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Clean column names - strip whitespace and special characters
        df.columns = df.columns.str.strip()
        
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
    except Exception as e:
        error_message = f"Error processing CSV file: {str(e)}"
        print(error_message)
        return {
            "error": error_message,
            "name": file.filename,
            "rows": 0,
            "columns": 0,
            "preview": []
        }


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
    df = datasets[current_session_id].copy()
    
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
        
        # If code modified the dataframe, update the stored version
        if "df" in env and id(env["df"]) != id(df):
            datasets[current_session_id] = env["df"]
        
        # If there's a result variable that might have been created
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
    
    df = datasets[current_session_id].copy()
    
    # Basic validation
    if df.empty:
        return {"error": "The dataset is empty."}
    
    try:
        # Find numeric columns for visualization
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # If no numeric columns, try to intelligently convert string columns
        # without creating new columns with _numeric suffix
        if not numeric_cols:
            numeric_candidate_cols = []
            for col in df.columns:
                # Skip columns that are clearly non-numeric (long text)
                if df[col].astype(str).str.len().mean() > 20:
                    continue
                    
                # Try to convert the column to numeric
                try:
                    # Use a temporary series to test conversion without modifying df
                    temp_series = pd.to_numeric(df[col], errors='coerce')
                    # If more than 50% values converted successfully, consider it numeric
                    if temp_series.notna().mean() >= 0.5:
                        numeric_candidate_cols.append(col)
                except:
                    continue
            
            # If we found numeric candidates, use the first one for y
            if numeric_candidate_cols:
                # Convert the actual column in place
                for col in numeric_candidate_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                numeric_cols = numeric_candidate_cols
        
        if not numeric_cols:
            return {"error": "No numeric columns found for visualization. Try running code to transform your data first."}
        
        # Choose columns for visualization
        if len(df.columns) > 1:
            # Use the first non-numeric column for x if available
            non_numeric_cols = [col for col in df.columns if col not in numeric_cols]
            if non_numeric_cols:
                x_col = non_numeric_cols[0]
            else:
                x_col = df.columns[0]
        else:
            # If only one column, use it for both x and y
            x_col = df.columns[0]
            
        # Use the first numeric column for y
        y_col = numeric_cols[0]
        
        # Create visualization based on chart type
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        elif chart_type == "pie":
            # For pie charts, we need categorical values for names
            fig = px.pie(df, names=x_col, values=y_col, title=f"Distribution of {y_col}")
        elif chart_type == "histogram":
            fig = px.histogram(df, x=y_col, title=f"Distribution of {y_col}")
        else:
            return {"error": f"Unsupported chart type: {chart_type}"}
        
        # Improve layout
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis_title=x_col,
            yaxis_title=y_col
        )
        
        # Convert to JSON for frontend rendering
        return json.loads(fig.to_json())
    except Exception as e:
        return {"error": f"Visualization error: {str(e)}"} 