import xml.etree.ElementTree as ET
import pandas as pd
import os
from collections import defaultdict
import traceback

# Configuration
XML_FILE = 'DrugBank_data/drugbank_all_full_database/full_database.xml' # raw xml dataset
OUTPUT_DIR = 'drugbank_parsed_csvs'
NS = {'db': 'http://www.drugbank.ca'}

# Setup
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Global Buffer to store rows before writing to CSV
buffers = defaultdict(list)

# Helper Functions
def safe_get(elem, path, default=None):
    """
    Safely extracts text OR attribute from an XML element.
    - Use 'tag/child' to get text content.
    - Use 'tag/@attribute' to get an attribute value.
    """
    if elem is None: return default

    # Handle Attribute Request manually (ElementTree doesn't support @ in find)
    if '@' in path:
        try:
            parts = path.split('/@')
            tag_path = parts[0]
            attr_name = parts[1]
            
            # If the tag path is empty (e.g. '@id'), we look at the current element
            if not tag_path:
                return elem.get(attr_name, default)
            
            # Otherwise find the child element first
            found = elem.find(tag_path, NS)
            if found is not None:
                return found.get(attr_name, default)
            return default
        except Exception:
            return default

    # Handle Standard Text Request
    found = elem.find(path, NS)
    return found.text if found is not None else default

def get_primary_id(drug_elem):
    """Gets the primary DrugBank ID to use as the foreign key."""
    id_elem = drug_elem.find('db:drugbank-id[@primary="true"]', NS)
    return id_elem.text if id_elem is not None else None


# 1. DRUG LEVEL PARSERS
def parse_drug_general(drug_id, drug_elem):
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

def parse_drug_classification(drug_id, drug_elem):
    cl = drug_elem.find('db:classification', NS)
    if cl is not None:
        buffers['drug_classification_drugbank_drugs'].append({
            'drugbank_id': drug_id,
            'kingdom': safe_get(cl, 'db:kingdom'),
            'superclass': safe_get(cl, 'db:superclass'),
            'class': safe_get(cl, 'db:class'),
            'subclass': safe_get(cl, 'db:subclass'),
            'direct_parent': safe_get(cl, 'db:direct-parent')
        })

def parse_simple_list(drug_id, parent_elem, list_tag, item_tag, table_name, col_map):
    """
    Generic parser for simple one-level lists.
    """
    container = parent_elem.find(f'db:{list_tag}', NS)
    if container is not None:
        for item in container.findall(f'db:{item_tag}', NS):
            row = {'drugbank_id': drug_id}
            for xml_tag, csv_col in col_map.items():
                if xml_tag.startswith('@'):
                    # Attribute of the item itself
                    row[csv_col] = item.get(xml_tag[1:])
                elif xml_tag == 'text':
                    # Text of the item itself
                    row[csv_col] = item.text
                else:
                    # Child tag text or attribute
                    row[csv_col] = safe_get(item, f'db:{xml_tag}')
            buffers[table_name].append(row)


# 2. PATHWAYS & REACTIONS
def parse_pathways(drug_id, drug_elem):
    container = drug_elem.find('db:pathways', NS)
    if container is None: return
    for pw in container.findall('db:pathway', NS):
        smpdb_id = safe_get(pw, 'db:smpdb-id')
        
        # 1. General
        buffers['general_information_drugbank_drugs_pathway'].append({
            'drugbank_id': drug_id,
            'smpdb_id': smpdb_id,
            'name': safe_get(pw, 'db:name'),
            'category': safe_get(pw, 'db:category')
        })
        # 2. Drugs in Pathway
        for d in pw.findall('db:drugs/db:drug', NS):
            buffers['pathway_drugs_drugbank_drugs_pathway'].append({
                'drugbank_id': drug_id,
                'smpdb_id': smpdb_id,
                'pathway_drug_id': safe_get(d, 'db:drugbank-id'),
                'name': safe_get(d, 'db:name')
            })
        # 3. Enzymes in Pathway
        for e in pw.findall('db:enzymes/db:uniprot-id', NS):
            buffers['pathway_enzyme_drugbank_drugs_pathway'].append({
                'drugbank_id': drug_id,
                'smpdb_id': smpdb_id,
                'uniprot_id': e.text
            })

def parse_reactions(drug_id, drug_elem):
    container = drug_elem.find('db:reactions', NS)
    if container is None: return
    for idx, rxn in enumerate(container.findall('db:reaction', NS)):
        rxn_id = f"{drug_id}_rxn_{idx}" 
        
        buffers['general_information_drugbank_drugs_reactions'].append({
            'drugbank_id': drug_id,
            'reaction_id': rxn_id,
            'sequence': safe_get(rxn, 'db:sequence'),
            'left_element_drug_id': safe_get(rxn, 'db:left-element/db:drugbank-id'),
            'left_element_name': safe_get(rxn, 'db:left-element/db:name'),
            'right_element_drug_id': safe_get(rxn, 'db:right-element/db:drugbank-id'),
            'right_element_name': safe_get(rxn, 'db:right-element/db:name')
        })
        
        for enz in rxn.findall('db:enzymes/db:enzyme', NS):
            buffers['reaction_enzymes_drugbank_drugs_reactions'].append({
                'drugbank_id': drug_id,
                'reaction_id': rxn_id,
                'enzyme_drugbank_id': safe_get(enz, 'db:drugbank-id'),
                'uniprot_id': safe_get(enz, 'db:uniprot-id')
            })


# 3. CETT (Targets, Enzymes, Carriers, Transporters)
def parse_polypeptide(drug_id, interactant_id, polypeptide_elem, file_suffix):
    """Parses the nested Polypeptide structure (Deepest Level)."""
    poly_id = polypeptide_elem.get('id') 
    
    # A. General Polypeptide Info
    # Note: We use the new safe_get logic here to handle the @ syntax
    buffers[f'general_information_{file_suffix}'].append({
        'drugbank_id': drug_id,
        'interactant_id': interactant_id,
        'polypeptide_id': poly_id,
        'name': safe_get(polypeptide_elem, 'db:name'),
        'general_function': safe_get(polypeptide_elem, 'db:general-function'),
        'specific_function': safe_get(polypeptide_elem, 'db:specific-function'),
        'gene_name': safe_get(polypeptide_elem, 'db:gene-name'),
        'locus': safe_get(polypeptide_elem, 'db:locus'),
        'molecular_weight': safe_get(polypeptide_elem, 'db:molecular-weight'),
        # This line caused the error before. Now safe_get handles the /@ split.
        'organism_id': safe_get(polypeptide_elem, 'db:organism/@ncbi-taxonomy-id'), 
        'organism_name': safe_get(polypeptide_elem, 'db:organism')
    })

    # B. Polypeptide Sub-tables
    for ext in polypeptide_elem.findall('db:external-identifiers/db:external-identifier', NS):
        buffers[f'external_identity_{file_suffix}'].append({
            'drugbank_id': drug_id,
            'interactant_id': interactant_id,
            'polypeptide_id': poly_id,
            'resource': safe_get(ext, 'db:resource'),
            'identifier': safe_get(ext, 'db:identifier')
        })
    
    for syn in polypeptide_elem.findall('db:synonyms/db:synonym', NS):
        buffers[f'synonyms_{file_suffix}'].append({
            'drugbank_id': drug_id,
            'interactant_id': interactant_id,
            'polypeptide_id': poly_id,
            'synonym': syn.text
        })

    for pfam in polypeptide_elem.findall('db:pfams/db:pfam', NS):
        buffers[f'pfams_{file_suffix}'].append({
            'drugbank_id': drug_id,
            'interactant_id': interactant_id,
            'polypeptide_id': poly_id,
            'identifier': safe_get(pfam, 'db:identifier'),
            'name': safe_get(pfam, 'db:name')
        })

    for go in polypeptide_elem.findall('db:go-classifiers/db:go-classifier', NS):
        buffers[f'go_{file_suffix}'].append({
            'drugbank_id': drug_id,
            'interactant_id': interactant_id,
            'polypeptide_id': poly_id,
            'category': safe_get(go, 'db:category'),
            'description': safe_get(go, 'db:description')
        })

def parse_interactant_group(drug_id, drug_elem, xml_tag, file_suffix):
    """
    Generic parser for Targets, Enzymes, Carriers, Transporters.
    """
    container = drug_elem.find(f'db:{xml_tag}', NS)
    if container is None: return
    
    child_tag = xml_tag[:-1] # targets -> target

    for item in container.findall(f'db:{child_tag}', NS):
        interactant_id = safe_get(item, 'db:id')
        if not interactant_id: continue
        
        # 1. General Info
        buffers[f'general_information_{file_suffix}'].append({
            'drugbank_id': drug_id,
            'interactant_id': interactant_id,
            'name': safe_get(item, 'db:name'),
            'organism': safe_get(item, 'db:organism'),
            'known_action': safe_get(item, 'db:known-action')
        })

        # 2. Actions
        actions_container = item.find('db:actions', NS)
        if actions_container:
            for act in actions_container.findall('db:action', NS):
                buffers[f'actions_{file_suffix}'].append({
                    'drugbank_id': drug_id,
                    'interactant_id': interactant_id,
                    'action': act.text
                })
        
        # 3. Polypeptides
        polypeptides = item.findall('db:polypeptide', NS)
        if polypeptides:
            for poly_elem in polypeptides:
                parse_polypeptide(drug_id, interactant_id, poly_elem, f'{file_suffix}_polypeptides')


# Main Loop
def process_drug(elem):
    drug_id = get_primary_id(elem)
    if not drug_id: return

    # 1. Drug Tables
    parse_drug_general(drug_id, elem)
    parse_drug_pharmacology(drug_id, elem)
    parse_drug_classification(drug_id, elem)
    
    # Simple Lists
    parse_simple_list(drug_id, elem, 'synonyms', 'synonym', 'synonyms_drugbank_drugs', 
                      {'text': 'synonym', '@language': 'language', '@coder': 'coder'})
    
    parse_simple_list(drug_id, elem, 'international-brands', 'international-brand', 'international_brands_drugbank_drugs', 
                      {'name': 'name', 'company': 'company'})
    
    parse_simple_list(drug_id, elem, 'mixtures', 'mixture', 'mixtures_drugbank_drugs', 
                      {'name': 'name', 'ingredients': 'ingredients'})
    
    parse_simple_list(drug_id, elem, 'categories', 'category', 'categories_drugbank_drugs', 
                      {'category': 'category', 'mesh-id': 'mesh_id'})
    
    parse_simple_list(drug_id, elem, 'dosages', 'dosage', 'dosages_drugbank_drugs', 
                      {'form': 'form', 'route': 'route', 'strength': 'strength'})
    
    parse_simple_list(drug_id, elem, 'drug-interactions', 'drug-interaction', 'drug_interactions_drugbank_drugs', 
                      {'drugbank-id': 'target_drugbank_id', 'name': 'name', 'description': 'description'})
    
    parse_simple_list(drug_id, elem, 'sequences', 'sequence', 'sequences_drugbank_drugs', 
                      {'text': 'sequence', '@format': 'format'})
    
    parse_simple_list(drug_id, elem, 'calculated-properties', 'property', 'calculated_properties_drugbank_drugs', 
                      {'kind': 'kind', 'value': 'value', 'source': 'source'})
    
    parse_simple_list(drug_id, elem, 'experimental-properties', 'property', 'experimental_properties_drugbank_drugs', 
                      {'kind': 'kind', 'value': 'value', 'source': 'source'})
    
    parse_simple_list(drug_id, elem, 'external-identifiers', 'external-identifier', 'external_identifiers_drugbank_drugs', 
                      {'resource': 'resource', 'identifier': 'identifier'})

    # Special Children Lists
    parse_simple_list(drug_id, elem, 'salts', 'salt', 'salts_drugbank', 
                      {'name': 'name', 'cas-number': 'cas_number', 'unii': 'unii'})
    
    parse_simple_list(drug_id, elem, 'snp-effects', 'effect', 'snp_effects_drugbank_drugs_reactions', 
                      {'protein-name': 'protein_name', 'gene-symbol': 'gene_symbol', 'description': 'description'})
    
    parse_simple_list(drug_id, elem, 'snp-adverse-drug-reactions', 'reaction', 'snp_adverse_reactions_drugbank_drugs_reactions', 
                      {'protein-name': 'protein_name', 'adverse-reaction': 'adverse_reaction'})
    
    parse_simple_list(drug_id, elem, 'food-interactions', 'food-interaction', 'food_interactions_drugbank_drugs_reactions', 
                      {'text': 'interaction'})
    
    parse_simple_list(drug_id, elem, 'pdb-entries', 'pdb-entry', 'pdb_entries_drugbank_drugs_reactions', 
                      {'text': 'pdb_entry'})

    # 2. Complex Structures
    parse_pathways(drug_id, elem)
    parse_reactions(drug_id, elem)

    # 3. Interactant Groups
    parse_interactant_group(drug_id, elem, 'targets', 'drugbank_cett_targets')
    parse_interactant_group(drug_id, elem, 'enzymes', 'drugbank_cett_enzymes')
    parse_interactant_group(drug_id, elem, 'carriers', 'drugbank_cett_carriers')
    parse_interactant_group(drug_id, elem, 'transporters', 'drugbank_cett_transporters')

# Run
if __name__ == "__main__":
    print(f"Streaming and Parsing {XML_FILE}...")
    print("This may take a few minutes depending on file size...")
    
    try:
        count = 0
        for event, elem in ET.iterparse(XML_FILE, events=("end",)):
            if event == 'end' and elem.tag.endswith('}drug'):
                try:
                    process_drug(elem)
                except Exception as e:
                    print(f"Error processing drug index {count}: {e}")
                    # traceback.print_exc() # Uncomment to see full trace for a specific drug error (DEBUGGING)
                
                elem.clear() 
                count += 1
                if count % 1000 == 0:
                    print(f"Parsed {count} drugs...")

        print(f"\nParsing complete. Writing CSV files to '{OUTPUT_DIR}'...")
        
        saved_count = 0
        for filename, rows in buffers.items():
            if rows:
                df = pd.DataFrame(rows)
                cols = df.columns.tolist()
                priority_cols = ['drugbank_id', 'interactant_id', 'polypeptide_id']
                new_order = [c for c in priority_cols if c in cols] + [c for c in cols if c not in priority_cols]
                df = df[new_order]
                
                file_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
                df.to_csv(file_path, index=False)
                print(f"-> Saved {filename}.csv ({len(df)} rows)")
                saved_count += 1
        
        if saved_count == 0:
            print("Warning: No data was extracted. Check XML namespace or file path.")
        else:
            print(f"\nSuccessfully generated {saved_count} CSV files.")

    except FileNotFoundError:
        print(f"Error: XML File not found at '{XML_FILE}'. Check the path.")
    except Exception as e:
        print(f"Critical Error: {e}")
        traceback.print_exc()