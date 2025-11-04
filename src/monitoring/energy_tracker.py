from typing import Dict

class EnergyMonitor:
    def __init__(self):
        self.metrics = {'total_queries': 0, 'total_emissions': 0.0}
    
    def track_query_energy(self, query: str, model_used: str, embedding_model: str) -> Dict:
        self.metrics['total_queries'] += 1
        return {'query': query[:50], 'model': model_used, 'embedding_model': embedding_model, 'emissions_kg_co2': 0.001}
    
    def get_carbon_report(self) -> Dict:
        return {'total_queries': self.metrics['total_queries'], 'total_emissions_kg_co2': round(self.metrics['total_emissions'], 4), 'equivalent_to': {'km_driven': 0, 'trees_needed': 0}}
