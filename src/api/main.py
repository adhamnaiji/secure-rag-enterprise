
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn
import sys
import logging
from collections import defaultdict
from src.rag.document_processor import SecureDocumentProcessor

sys.path.insert(0, '.')

from config.settings import settings
from src.core.llm_handler import PerplexityLLM
from src.core.vector_store_handler import VectorStoreHandler
from src.security.access_control import AccessController
from src.security.rate_limiter import RateLimiter
from src.security.adversarial_detection import AdversarialDetector
from src.security.input_validation import SecurityValidator
from src.compliance.audit_logger import AuditLogger
from src.compliance.explainability import ExplainabilityTracker
from src.monitoring.energy_tracker import EnergyMonitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Secure RAG System for Enterprise with Perplexity LLM"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== GLOBAL METRICS STORE (LIVE DATA) =====
security_metrics = {
    "blocked_queries": 0,
    "rate_limit_hits": 0,
    "invalid_queries": 0,
    "adversarial_attempts": 0,
    "total_queries": 0,
    "recent_events": []
}

# ===== INITIALIZE COMPONENTS =====
llm_handler = PerplexityLLM()
vector_store = VectorStoreHandler()
access_controller = AccessController(settings.ENCRYPTION_KEY)
rate_limiter = RateLimiter(max_requests=settings.MAX_REQUESTS_PER_MINUTE)
adversarial_detector = AdversarialDetector()
audit_logger = AuditLogger()
explainability_tracker = ExplainabilityTracker()
energy_monitor = EnergyMonitor()
security_validator = SecurityValidator()

# ===== MODELS =====
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    response: str
    sources: List[str]
    confidence: float
    execution_time_ms: float
    explanation: Dict

# ===== HELPER FUNCTIONS =====
def add_security_event(event_type: str, severity: str, details: Dict = None):
    """Add event to metrics"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "severity": severity,
        "details": details or {}
    }
    security_metrics["recent_events"].append(event)
    
    # Keep only last 50 events
    if len(security_metrics["recent_events"]) > 50:
        security_metrics["recent_events"] = security_metrics["recent_events"][-50:]

# ===== ENDPOINTS =====

@app.post("/query")
async def query_rag(request: QueryRequest, authorization: str = Header(...)):
    """Execute RAG query with security tracking"""
    
    start_time = time.time()
    user_id = "test_user"
    
    try:
        security_metrics["total_queries"] += 1
        logger.info(f"🔍 Query {security_metrics['total_queries']}: {request.query[:50]}...")
        
        # ===== 1. RATE LIMITING =====
        allowed, message = rate_limiter.is_allowed(user_id)
        if not allowed:
            security_metrics["rate_limit_hits"] += 1
            add_security_event("RATE_LIMIT_EXCEEDED", "MEDIUM", {"user": user_id})
            logger.warning(f"⏱️ Rate limit exceeded")
            raise HTTPException(status_code=429, detail=message)
        
        # ===== 2. VALIDATE QUERY =====
        is_valid, error = security_validator.validate_query(request.query)
        if not is_valid:
            security_metrics["invalid_queries"] += 1
            add_security_event("INVALID_QUERY", "LOW", {"reason": error})
            logger.warning(f"❌ Invalid query: {error}")
            raise HTTPException(status_code=400, detail=f"Invalid query: {error}")
        
        # ===== 3. DETECT ADVERSARIAL ATTEMPTS =====
        is_adversarial, attack_type, confidence = adversarial_detector.detect_adversarial_query(request.query)
        if is_adversarial:
            security_metrics["blocked_queries"] += 1
            security_metrics["adversarial_attempts"] += 1
            add_security_event("ADVERSARIAL_DETECTED", "HIGH", {"attack_type": attack_type, "confidence": confidence})
            logger.warning(f"🚨 ATTACK DETECTED: {attack_type}")
            raise HTTPException(status_code=400, detail=f"🚨 Security Alert: {attack_type} attack detected")
        
        # ===== 4. RETRIEVE DOCUMENTS =====
        retrieved_docs = vector_store.search(request.query, k=request.top_k)
        retrieved_text = [doc['content'] for doc in retrieved_docs] if retrieved_docs else []
        
        # ===== 5. GENERATE RESPONSE =====
        logger.info(f"🤖 Generating response with Perplexity LLM...")
        response = llm_handler.generate_response(request.query, retrieved_text)
        
        # ===== 6. GET EXPLANATION =====
        explanation = explainability_tracker.explain_retrieval(
            request.query,
            retrieved_docs,
            [doc.get('score', 0.8) for doc in retrieved_docs] if retrieved_docs else []
        )
        
        # ===== 7. LOG SUCCESS =====
        execution_time = time.time() - start_time
        add_security_event("QUERY_EXECUTED", "LOW", {"query": request.query[:50], "time_ms": execution_time * 1000})
        logger.info(f"✅ Query completed in {execution_time:.2f}s")
        
        return QueryResponse(
            response=response,
            sources=[doc['metadata'].get('source', 'unknown') for doc in retrieved_docs] if retrieved_docs else [],
            confidence=0.92,
            execution_time_ms=execution_time * 1000,
            explanation=explanation
        )
        
    except HTTPException as e:
        logger.error(f"❌ HTTP Exception: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Query error: {str(e)}", exc_info=True)
        add_security_event("QUERY_ERROR", "HIGH", {"error": str(e)[:100]})
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), authorization: str = Header(...)):
    """Upload and process PDF documents"""
    
    user_id = "test_user"
    
    try:
        logger.info(f"📤 Uploading file: {file.filename}")
        
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        
        # Save file
        file_path = f"uploads/{file.filename}"
        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)
        
        logger.info(f"✅ File saved: {file_path}")
        
        # Process document
        processor = SecureDocumentProcessor()
        documents = processor.load_documents("uploads")
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found in uploaded file")
        
        logger.info(f"✅ Processed {len(documents)} chunks")
        
        # Add to vector store
        vector_store.create_from_documents(documents)
        
        # Log event
        add_security_event("DOCUMENT_UPLOADED", "LOW", {"filename": file.filename, "chunks": len(documents)})
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": len(documents),
            "message": f"✅ Document processed: {len(documents)} chunks created"
        }
        
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        add_security_event("UPLOAD_ERROR", "HIGH", {"error": str(e)[:100]})
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": settings.API_VERSION,
        "llm_initialized": llm_handler.llm is not None
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "carbon_footprint": energy_monitor.get_carbon_report(),
        "version": settings.API_VERSION
    }

@app.get("/security-stats")
async def security_stats():
    """Get LIVE security statistics"""
    return {
        "status": "operational",
        "metrics": {
            "blocked_queries": security_metrics["blocked_queries"],
            "rate_limit_hits": security_metrics["rate_limit_hits"],
            "invalid_queries": security_metrics["invalid_queries"],
            "adversarial_attempts": security_metrics["adversarial_attempts"],
            "total_queries": security_metrics["total_queries"]
        },
        "recent_events": security_metrics["recent_events"][-20:],  # Last 20 events
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def status():
    """Get system status"""
    return {
        "api": "✅ Online",
        "llm": "✅ Ready" if llm_handler.llm else "❌ Error",
        "vector_store": "✅ Ready",
        "security": "✅ Active",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)