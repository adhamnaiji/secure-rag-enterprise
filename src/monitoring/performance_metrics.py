from typing import Dict

class PerformanceMonitor:
    def __init__(self):
        self.latencies = []
    
    def record_query_execution(self, execution_time: float, docs_retrieved: int):
        self.latencies.append(execution_time * 1000)
    
    def get_performance_report(self) -> Dict:
        if not self.latencies:
            return {'total_queries': 0, 'avg_latency_ms': 0, 'p95_latency_ms': 0, 'p99_latency_ms': 0}
        sorted_lat = sorted(self.latencies)
        return {'total_queries': len(self.latencies), 'avg_latency_ms': round(sum(self.latencies) / len(self.latencies), 2), 'p95_latency_ms': round(sorted_lat[int(len(sorted_lat)*0.95)], 2), 'p99_latency_ms': round(sorted_lat[int(len(sorted_lat)*0.99)], 2)}
