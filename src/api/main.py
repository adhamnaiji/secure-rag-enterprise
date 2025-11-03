# src/api/main.py
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn



from config.settings import settings
from src.core.document_processor import SecureDocumentProcessor
from src.core.retrieval import IntelligentRetriever
from src.security.access_control import AccessController
from src.security.rate_limiter import RateLimiter
from src.security.adversarial_detection import AdversarialDetector
from src.security.input_validation import SecurityValidator  # ✓ Added import
from src.compliance.audit_logger import AuditLogger
from src.compliance.explainability import ExplainabilityTracker
from src.monitoring.energy_tracker import EnergyMonitor


# Initialize
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Secure RAG System for Enterprise"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Components
access_controller = AccessController(settings.ENCRYPTION_KEY)
rate_limiter = RateLimiter(max_requests=settings.MAX_REQUESTS_PER_MINUTE)
adversarial_detector = AdversarialDetector()
audit_logger = AuditLogger()
explainability_tracker = ExplainabilityTracker()
energy_monitor = EnergyMonitor()
security_validator = SecurityValidator()  # ✓ Added


# Models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    response: str
    sources: List[str]
    confidence: float
    execution_time_ms: float
    explanation: Dict


# Endpoints


@app.post("/query")
async def query_rag(request: QueryRequest, 
                   authorization: str = Header(...)):
    """Execute RAG query with security checks"""
    
    start_time = time.time()
    
    # 1. Authenticate
    user_id = access_controller.verify_token(authorization.replace("Bearer ", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Rate limit
    allowed, message = rate_limiter.is_allowed(user_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=message)
    
    # 3. Validate query ✓ Fixed
    is_valid, error = security_validator.validate_query(request.query)
    if not is_valid:
        audit_logger.log_security_event(user_id, "INVALID_QUERY", {"reason": error}, severity="LOW")
        raise HTTPException(status_code=400, detail=error)
    
    # 4. Detect adversarial attempts
    is_adversarial, attack_type, confidence = adversarial_detector.detect_adversarial_query(request.query)
    if is_adversarial:
        audit_logger.log_security_event(
            user_id, 
            "ADVERSARIAL_DETECTED",
            {"attack_type": attack_type, "confidence": confidence},
            severity="HIGH"
        )
        raise HTTPException(status_code=400, detail="Query blocked: potential attack")
    
    # 5. Execute query
    try:
        # Track energy
        energy_metrics = energy_monitor.track_query_energy(
            request.query,
            settings.OPENAI_MODEL,
            "sentence-transformers/all-miniLM-L6-v2"
        )
        
        # Get documents (simulated)
        retrieved_docs = []  # Would retrieve from vector store
        
        # Generate response (simulated)
        response = "Generated response based on retrieved documents"
        
        # Get explanation
        explanation = explainability_tracker.explain_retrieval(
            request.query,
            retrieved_docs,
            [0.95, 0.87, 0.82]
        )
        
        # Log query
        execution_time = time.time() - start_time
        audit_logger.log_query(
            user_id,
            request.query,
            len(retrieved_docs),
            execution_time * 1000,
            settings.OPENAI_MODEL
        )
        
        return QueryResponse(
            response=response,
            sources=[doc.metadata.get('source') for doc in retrieved_docs] if retrieved_docs else [],
            confidence=0.92,
            execution_time_ms=execution_time * 1000,
            explanation=explanation
        )
        
    except Exception as e:
        audit_logger.log_security_event(user_id, "QUERY_ERROR", {"error": str(e)}, severity="HIGH")
        raise HTTPException(status_code=500, detail="Query execution failed")


@app.post("/upload")
async def upload_document(file: UploadFile = File(...),
                         authorization: str = Header(...)):
    """Upload and process document securely"""
    
    # Authenticate
    user_id = access_controller.verify_token(authorization.replace("Bearer ", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    temp_path = None
    try:
        # Validate ✓ Fixed
        is_valid, error = security_validator.validate_document(file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Save file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Process
        processor = SecureDocumentProcessor(settings.ENCRYPTION_KEY)
        documents = processor.process_pdf_secure(temp_path)
        
        # Log
        audit_logger.log_data_access(user_id, [temp_path], "DOCUMENT_UPLOAD")
        
        return {
            "status": "success",
            "documents_processed": len(documents),
            "message": "Document uploaded and processed"
        }
        
    finally:
        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": settings.API_VERSION
    }


@app.get("/metrics")
async def get_metrics(authorization: str = Header(...)):
    """Get system metrics"""
    
    # Authenticate
    user_id = access_controller.verify_token(authorization.replace("Bearer ", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "carbon_footprint": energy_monitor.get_carbon_report(),
        "rate_limit_remaining": rate_limiter.get_remaining_requests(user_id)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
