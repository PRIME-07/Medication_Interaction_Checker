import sqlite3
import pandas as pd
import os
import numpy as np

# Configuration
CSV_DIR = './drugbank_parsed_csvs_required_10'
DB_FILE = 'req_10_sqlite_drugbank.db'

# Mapping csv file names to table
FILES_TO_PROCESS = {
    # 1. Core Drug Info
    "general_information_drugbank_drugs.csv": "general_info",
    "pharmacology_drugbank_drugs.csv": "pharmacology",
    
    # 2. Resolution & Mixtures
    "mixtures_drugbank_drugs.csv": "mixtures",
    "synonyms_drugbank_drugs.csv": "synonyms",
    
    # 3. Interactions
    "drug_interactions_drugbank_drugs.csv": "drug_interactions",
    "food_interactions_drugbank_drugs_reactions.csv": "food_interactions",
    
    # 4. References
    "references_articles_drugbank_drugs.csv": "ref_articles",
    "references_attachments_drugbank_drugs.csv": "ref_attachments",
    "references_books_drugbank_drugs.csv": "ref_books",
    "references_links_drugbank_drugs.csv": "ref_links"
}

def clean_and_load(csv_name, table_name, conn):
    file_path = os.path.join(CSV_DIR, csv_name)
    
    if not os.path.exists(file_path):
        print(f"CRITICAL: {csv_name} missing in {CSV_DIR}")
        return

    print(f"Processing {csv_name} -> Table: '{table_name}'")
    
    try:
        # Read everything. low_memory=False prevents type inference errors.
        df = pd.read_csv(file_path, low_memory=False)
        
        # Convert NaN to None (SQL NULL)
        df = df.replace({np.nan: None, "": None})
        
        # Force IDs to string to ensure 'DB001' doesn't become 1
        if 'drugbank_id' in df.columns:
            df['drugbank_id'] = df['drugbank_id'].astype(str)
            
        # Force Mixtures ingredients to string
        if table_name == 'mixtures' and 'ingredients' in df.columns:
            df['ingredients'] = df['ingredients'].astype(str)

        # Write to SQL (Replace ensures we start fresh)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"   -> Loaded {len(df)} rows.")
        print(f"   -> Columns: {list(df.columns)}") # Verify all columns are present
        
    except Exception as e:
        print(f"Error: {e}")

def add_indices(conn):
    print("\nOptimizing Database (Indexing)...")
    cursor = conn.cursor()
    
    # 1. Generic Indexing (drugbank_id)
    for _, table_name in FILES_TO_PROCESS.items():
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pk ON {table_name}(drugbank_id)")
        except Exception:
            pass # Table might not exist if CSV was missing

    # 2. Search Specific Indices
    try:
        # Interaction Lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inter_target ON drug_interactions(target_drugbank_id)")
        
        # Name Search (Generics, Synonyms, Mixtures)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gen_name ON general_info(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_syn_name ON synonyms(synonym)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mix_name ON mixtures(name)")
        
        print("   -> Indices created successfully.")
    except Exception as e:
        print(f"Indexing Warning: {e}")

    conn.commit()

# Execution
if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Deleted old database: {DB_FILE}")
        except PermissionError:
            print("Error: Close any app using the DB and try again.")
            exit()

    # 2. Build
    conn = sqlite3.connect(DB_FILE)
    print(f"Building new database from: {CSV_DIR}")
    print("-" * 40)

    for csv, table in FILES_TO_PROCESS.items():
        clean_and_load(csv, table, conn)
        
    add_indices(conn)
    
    conn.close()
    print("-" * 40)
    print(f"Complete. New database: {DB_FILE}")


