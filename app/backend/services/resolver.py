from ..database import db_manager
from typing import List, Dict

class DrugResolver:
    def __init__(self):
        self.db = db_manager

    def _get_id_from_name(self, name: str) -> str:
        # Exact match only
        res = self.db.query("SELECT drugbank_id FROM general_info WHERE name = ? AND type != 'brand' LIMIT 1", (name,))
        if res: return res[0]['drugbank_id']
        return None # type: ignore

    def resolve_input(self, user_inputs: List[str]) -> Dict[str, str]:
        resolved_map = {}
        for item in user_inputs:
            # 1. Check if it's a mixture/brand
            res = self.db.query("SELECT ingredients FROM mixtures WHERE name = ?", (item,))
            
            if res:
                # It's a brand from the dropdown -> Split ingredients
                ingredients = [i.strip() for i in res[0]['ingredients'].split('+')]
                for ing in ingredients:
                    did = self._get_id_from_name(ing)
                    if did: 
                        resolved_map[f"{item} ({ing})"] = did
            else:
                # It's a generic/synonym from the dropdown
                did = self._get_id_from_name(item)
                if did: resolved_map[item] = did
                
        return resolved_map