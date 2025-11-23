import itertools
from typing import List, Dict
from ..database import db_manager

class InteractionEngine:
    """Checks Database for Pairs"""
    
    def __init__(self):
        self.db = db_manager

    def check_interactions(self, drug_ids: List[str]) -> List[Dict]:
        interactions_found = []
        # Generate unique pairs only once (A, B)
        pairs = list(itertools.combinations(drug_ids, 2))
        
        for id_a, id_b in pairs:
            # Query checks for A->B OR B->A
            sql = """
                SELECT * FROM drug_interactions 
                WHERE (drugbank_id = ? AND target_drugbank_id = ?)
                OR (drugbank_id = ? AND target_drugbank_id = ?)
            """
            results = self.db.query(sql, (id_a, id_b, id_b, id_a))
            
            # If results exist, just take the first one.
            if results:
                row = results[0] 
                interactions_found.append({
                    "drug_a": row['drugbank_id'],
                    "drug_b": row['target_drugbank_id'],
                    "description": row['description']
                })
                
        return interactions_found