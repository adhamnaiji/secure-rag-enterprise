from codecarbon import EmissionsTracker
from typing import Dict
import time

class EnergyMonitor:
    """Track energy consumption for frugal AI"""
    
    def __init__(self):
        self.tracker = EmissionsTracker()
        self.metrics = {
            'total_queries': 0,
            'total_energy_kwh': 0,
            'total_emissions_kg_co2': 0,
            'avg_energy_per_query': 0
        }
    
    def track_query_energy(self, query: str, model_used: str,
                          embedding_model: str) -> Dict:
        """Track energy for single query"""
        
        self.tracker.start()
        start_time = time.time()
        
        # Simulate query execution
        time.sleep(0.1)  # Replace with actual query
        
        emissions = self.tracker.stop()
        query_time = time.time() - start_time
        
        energy_metrics = {
            'query': query[:50],
            'model': model_used,
            'embedding_model': embedding_model,
            'duration_seconds': query_time,
            'emissions_kg_co2': emissions,
            'energy_kwh': emissions / 0.4  # Approximate conversion
        }
        
        # Update totals
        self.metrics['total_queries'] += 1
        self.metrics['total_emissions_kg_co2'] += emissions
        self.metrics['avg_energy_per_query'] = (
            self.metrics['total_emissions_kg_co2'] / self.metrics['total_queries']
        )
        
        return energy_metrics
    
    def get_carbon_report(self) -> Dict:
        """Generate carbon footprint report"""
        return {
            'total_queries': self.metrics['total_queries'],
            'total_emissions_kg_co2': round(self.metrics['total_emissions_kg_co2'], 4),
            'avg_emissions_per_query': round(self.metrics['avg_energy_per_query'], 4),
            'equivalent_to': {
                'km_driven': round(self.metrics['total_emissions_kg_co2'] / 0.2, 2),
                'trees_needed': round(self.metrics['total_emissions_kg_co2'] / 0.02, 2)
            }
        }