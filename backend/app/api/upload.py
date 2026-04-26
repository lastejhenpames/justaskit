from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import json
from datetime import datetime
from app.core.database import get_db, Dataset, init_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize database on startup
init_db()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload CSV or Excel file for analysis"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Read file into pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
        
        # Generate table name
        table_name = f"data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Detect schema
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            schema[col] = {
                "type": dtype,
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            }
        
        # Store in SQLite
        from app.core.config import settings
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        # Save metadata
        dataset = Dataset(
            filename=file.filename,
            row_count=len(df),
            column_count=len(df.columns),
            schema_json=json.dumps(schema),
            table_name=table_name
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        logger.info(f"Uploaded dataset: {file.filename} ({len(df)} rows, {len(df.columns)} cols)")
        
        return {
            "dataset_id": dataset.id,
            "filename": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "schema": schema,
            "preview": df.head(5).to_dict(orient='records')
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/datasets")
async def list_datasets(db: Session = Depends(get_db)):
    """List all uploaded datasets"""
    datasets = db.query(Dataset).order_by(Dataset.upload_date.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "upload_date": d.upload_date.isoformat(),
            "row_count": d.row_count,
            "column_count": d.column_count
        }
        for d in datasets
    ]
