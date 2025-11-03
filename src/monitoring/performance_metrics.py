import time
from typing import Dict
from prometheus_client import Counter, Histogram, Gauge

class PerformanceMonitor:
    """Track system performance metrics"""
    
    def __init__(self):
        # Prometheus metrics
        self.query_counter = Counter('rag_queries_total', 'Total RAG queries')
        self.query_latency = Histogram('rag_query_latency_seconds', 'Query latency')
        self.retrieval_count = Histogram('rag_documents_retrieved', 'Documents retrieved')
        self.cache_hits = Gauge('rag_cache_hits', 'Cache hit rate')
    
    def record_query_execution(self, execution_time: float, docs_retrieved: int):
        """Record query metrics"""
        
        self.query_counter.inc()
        self.query_latency.observe(execution_time)
        self.retrieval_count.observe(docs_retrieved)
    
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        return {
            'total_queries': self.query_counter._value.get(),
            'avg_latency_ms': 0,  # Calculate from histogram
            'p95_latency_ms': 0,
            'p99_latency_ms': 0
        }
