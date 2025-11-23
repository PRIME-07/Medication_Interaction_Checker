import xml.etree.ElementTree as ET
import pandas as pd
import os
from collections import defaultdict
import traceback

# Configuration
XML_FILE = 'DrugBank_data/drugbank_all_full_database/full_database.xml'
OUTPUT_DIR = 'drugbank_parsed_csvs_required_10'
NS = {'db': 'http://www.drugbank.ca'}

# Setup
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Global Buffer
buffers = defaultdict(list)

# Helper Functions
def safe_get(elem, path, default=None):
    if elem is None: return default
    if '@' in path:
        try:
            parts = path.split('/@')
            tag_path = parts[0]
            attr_name = parts[1]
            if not tag_path:
                return elem.get(attr_name, default)
            found = elem.find(tag_path, NS)
            if found is not None:
                return found.get(attr_name, default)
            return default
        except Exception:
            return default
    found = elem.find(path, NS)
    return found.text if found is not None else default

def get_primary_id(drug_elem):
    id_elem = drug_elem.find('db:drugbank-id[@primary="true"]', NS)
    return id_elem.text if id_elem is not None else None

# Parsers
def parse_drug_general(drug_id, drug_elem):
    """Target: general_information_drugbank_drugs.csv"""
    buffers['general_information_drugbank_drugs'].append({
        'drugbank_id': drug_id,
        'name': safe_get(drug_elem, 'db:name'),
        'type': drug_elem.get('type'),
        'cas_number': safe_get(drug_elem, 'db:cas-number'),
        'unii': safe_get(drug_elem, 'db:unii'),
        'state': safe_get(drug_elem, 'db:state'),
        'average_mass': safe_get(drug_elem, 'db:average-mass'),
        'monoisotopic_mass': safe_get(drug_elem, 'db:monoisotopic-mass'),
        'created': drug_elem.get('created'),
        'updated': drug_elem.get('updated'),
        'description': safe_get(drug_elem, 'db:description')
    })

def parse_drug_pharmacology(drug_id, drug_elem):
    """Target: pharmacology_drugbank_drugs.csv"""
    buffers['pharmacology_drugbank_drugs'].append({
        'drugbank_id': drug_id,
        'indication': safe_get(drug_elem, 'db:indication'),
        'pharmacodynamics': safe_get(drug_elem, 'db:pharmacodynamics'),
        'mechanism_of_action': safe_get(drug_elem, 'db:mechanism-of-action'),
        'toxicity': safe_get(drug_elem, 'db:toxicity'),
        'metabolism': safe_get(drug_elem, 'db:metabolism'),
        'absorption': safe_get(drug_elem, 'db:absorption'),
        'half_life': safe_get(drug_elem, 'db:half-life'),
        'protein_binding': safe_get(drug_elem, 'db:protein-binding'),
        'route_of_elimination': safe_get(drug_elem, 'db:route-of-elimination'),
        'volume_of_distribution': safe_get(drug_elem, 'db:volume-of-distribution'),
        'clearance': safe_get(drug_elem, 'db:clearance'),
    })

def parse_drug_references(drug_id, drug_elem):
    """
    Targets: 
    - references_articles_drugbank_drugs.csv
    - references_books_drugbank_drugs.csv
    - references_links_drugbank_drugs.csv
    - references_attachments_drugbank_drugs.csv
    """
    container = drug_elem.find('db:general-references', NS)
    if container is None: return

    # 1. Articles
    for item in container.findall('db:articles/db:article', NS):
        buffers['references_articles_drugbank_drugs'].append({
            'drugbank_id': drug_id,
            'ref_id': item.get('id'),
            'pubmed_id': safe_get(item, 'db:pubmed-id'),
            'citation': safe_get(item, 'db:citation')
        })

    # 2. Books
    for item in container.findall('db:textbooks/db:textbook', NS):
        buffers['references_books_drugbank_drugs'].append({
            'drugbank_id': drug_id,
            'ref_id': item.get('id'),
            'isbn': safe_get(item, 'db:isbn'),
            'citation': safe_get(item, 'db:citation')
        })

    # 3. Links
    for item in container.findall('db:links/db:link', NS):
        buffers['references_links_drugbank_drugs'].append({
            'drugbank_id': drug_id,
            'ref_id': item.get('id'),
            'title': safe_get(item, 'db:title'),
            'url': safe_get(item, 'db:url')
        })

    # 4. Attachments
    for item in container.findall('db:attachments/db:attachment', NS):
        buffers['references_attachments_drugbank_drugs'].append({
            'drugbank_id': drug_id,
            'ref_id': item.get('id'),
            'title': safe_get(item, 'db:title'),
            'url': safe_get(item, 'db:url')
        })

def parse_simple_list(drug_id, parent_elem, list_tag, item_tag, table_name, col_map):
    """Generic parser used for Synonyms, Mixtures, Interactions."""
    container = parent_elem.find(f'db:{list_tag}', NS)
    if container is not None:
        for item in container.findall(f'db:{item_tag}', NS):
            row = {'drugbank_id': drug_id}
            for xml_tag, csv_col in col_map.items():
                if xml_tag.startswith('@'):
                    row[csv_col] = item.get(xml_tag[1:])
                elif xml_tag == 'text':
                    row[csv_col] = item.text
                else:
                    row[csv_col] = safe_get(item, f'db:{xml_tag}')
            buffers[table_name].append(row)

# Main Loop
def process_drug(elem):
    drug_id = get_primary_id(elem)
    if not drug_id: return

    # 1. Core Data
    parse_drug_general(drug_id, elem)
    parse_drug_pharmacology(drug_id, elem)
    parse_drug_references(drug_id, elem)
    
    # 2. Lists (Synonyms, Mixtures, Interactions)
    
    # Target: synonyms_drugbank_drugs.csv
    parse_simple_list(drug_id, elem, 'synonyms', 'synonym', 'synonyms_drugbank_drugs', 
                      {'text': 'synonym', '@language': 'language', '@coder': 'coder'})
    
    # Target: mixtures_drugbank_drugs.csv
    parse_simple_list(drug_id, elem, 'mixtures', 'mixture', 'mixtures_drugbank_drugs', 
                      {'name': 'name', 'ingredients': 'ingredients'})
    
    # Target: drug_interactions_drugbank_drugs.csv
    parse_simple_list(drug_id, elem, 'drug-interactions', 'drug-interaction', 'drug_interactions_drugbank_drugs', 
                      {'drugbank-id': 'target_drugbank_id', 'name': 'name', 'description': 'description'})
    
    # Target: food_interactions_drugbank_drugs_reactions.csv
    parse_simple_list(drug_id, elem, 'food-interactions', 'food-interaction', 'food_interactions_drugbank_drugs_reactions', 
                      {'text': 'interaction'})

# Run
if __name__ == "__main__":
    print(f"Streaming and Parsing {XML_FILE} (Restricted Mode)...")
    
    try:
        count = 0
        for event, elem in ET.iterparse(XML_FILE, events=("end",)):
            if event == 'end' and elem.tag.endswith('}drug'):
                try:
                    process_drug(elem)
                except Exception as e:
                    print(f"Error processing drug index {count}: {e}")
                
                elem.clear() 
                count += 1
                if count % 1000 == 0:
                    print(f"Parsed {count} drugs...")

        print(f"\nParsing complete. Writing CSV files to '{OUTPUT_DIR}'...")
        
        saved_count = 0
        for filename, rows in buffers.items():
            if rows:
                df = pd.DataFrame(rows)
                # Basic column reordering logic
                cols = df.columns.tolist()
                if 'drugbank_id' in cols:
                    cols.insert(0, cols.pop(cols.index('drugbank_id')))
                df = df[cols]
                
                file_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
                df.to_csv(file_path, index=False)
                print(f"-> Saved {filename}.csv ({len(df)} rows)")
                saved_count += 1
        
        print(f"\nSuccessfully generated {saved_count} CSV files.")

    except FileNotFoundError:
        print(f"Error: XML File not found at '{XML_FILE}'. Check the path.")
    except Exception as e:
        print(f"Critical Error: {e}")
        traceback.print_exc()