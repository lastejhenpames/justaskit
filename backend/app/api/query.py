from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import pandas as pd
import json
import time
import uuid
from app.core.database import get_db, Dataset, QueryLog
from app.core.config import settings
from app.agents.orchestrator import MultiAgentOrchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize multi-agent orchestrator
orchestrator = MultiAgentOrchestrator()

class QueryRequest(BaseModel):
    dataset_id: int
    query: str

@router.post("/query")
async def query_data(request: QueryRequest, db: Session = Depends(get_db)):
    """Query dataset with natural language using AI agent"""
    query_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Get dataset
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Load data
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL)
        df = pd.read_sql_table(dataset.table_name, engine)
        
        # Use multi-agent orchestrator (Week 3 - Multi-agent system)
        result = orchestrator.execute(df, request.query)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Log query
        query_log = QueryLog(
            query_id=query_id,
            user_query=request.query,
            dataset_id=request.dataset_id,
            agents_executed=json.dumps(result.get("agents_executed", [])),
            execution_time_ms=execution_time,
            result_json=json.dumps(result, default=str)
        )
        db.add(query_log)
        db.commit()
        
        logger.info(f"Query executed: {request.query[:50]}... ({execution_time:.2f}ms)")
        
        return {
            "query_id": query_id,
            "result": result,
            "execution_time_ms": execution_time
        }
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        
        # Log error
        query_log = QueryLog(
            query_id=query_id,
            user_query=request.query,
            dataset_id=request.dataset_id,
            agents_executed=json.dumps([]),
            execution_time_ms=(time.time() - start_time) * 1000,
            error=str(e)
        )
        db.add(query_log)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")
