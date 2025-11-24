# 💊 Medication Interaction Checker (DrugGuard AI)

A comprehensive, AI-powered system that analyzes patient medication lists and identifies potential dangerous drug-drug interactions. Built with FastAPI, React, and powered by DrugBank database and Llama 3.1 LLM for clinical analysis.

## 🎯 Overview

DrugGuard AI is a full-stack web application that helps healthcare professionals and patients identify potentially dangerous medication interactions in real-time. The system uses the DrugBank database for interaction detection and leverages AI (Llama 3.1) for severity classification, clinical recommendations, and patient-specific risk assessment.

## ✨ Key Features

### 🔍 **Intelligent Drug Resolution**
- Handles brand names, generic names, and synonyms
- Automatically resolves brand medications to their active ingredients
- Supports multi-ingredient medications (mixtures)
- Real-time autocomplete search with fuzzy matching

### 🤖 **AI-Powered Analysis**
- **Severity Classification**: Automatically categorizes interactions as High, Moderate, or Low risk
- **Clinical Summaries**: AI-generated explanations of interaction mechanisms
- **Personalized Recommendations**: Context-aware clinical recommendations based on drug pharmacology
- **Patient-Specific Risk Assessment**: Considers patient age and gender for personalized risk evaluation

### 📊 **Comprehensive Reporting**
- Color-coded severity indicators (Red/Orange/Yellow)
- Detailed interaction cards with clinical information
- Food and lifestyle interaction warnings
- Clinical references with PubMed links and external resources
- Structured analysis cards for easy review

### 🏗️ **Robust Architecture**
- Modular, maintainable codebase with clear separation of concerns
- RESTful API design
- Efficient SQLite database queries with proper indexing
- Modern React frontend with responsive design

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.121.3) - Modern Python web framework
- **Uvicorn** (0.38.0) - ASGI server
- **Pydantic** (2.12.4) - Data validation
- **SQLite** - DrugBank database storage
- **Ollama** - Local LLM inference (Llama 3.1:8b)
- **Requests** (2.32.5) - HTTP client for LLM API

### Frontend
- **React** (19.2.0) - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Data Processing
- **Pandas** (2.3.3) - Data manipulation
- **NumPy** (2.0.1) - Numerical computing

### Data Source
- **DrugBank Database** - Comprehensive drug interaction database

## 📐 System Architecture

### Flow Diagram

```
1. User Input (Medication List)
   ↓
2. Drug Resolution (DrugResolver)
   - Brand → Ingredients
   - Synonyms → Generic IDs
   - Name → DrugBank ID
   ↓
3. Interaction Detection (InteractionEngine)
   - Generate all pairs
   - Query database
   ↓
4. AI Analysis (ClinicalSummarizer)
   - Severity classification
   - Interaction summaries
   - Clinical recommendations
   - Patient-specific risk
   ↓
5. Alert Display (ReportView)
   - Severity badges
   - Clinical cards
   - Food warnings
   - References
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ SearchBar│  │Medication │  │ReportView│              │
│  │          │  │   List    │  │          │              │
│  └────┬─────┘  └─────┬─────┘  └─────┬────┘              │
│       │              │              │                   │
│       └──────────────┴──────────────┘                   │
│                        │                                │
└────────────────────────┼────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┼────────────────────────────────┐
│                    Backend (FastAPI)                    │
│  ┌──────────────────────────────────────────┐           │
│  │         API Endpoints (main.py)          │           │
│  └──────┬───────────────────────┬────────────┘          │
│         │                       │                       │
│  ┌──────▼──────┐      ┌────────▼─────────┐              │
│  │DrugResolver │      │InteractionEngine │              │
│  └──────┬──────┘      └────────┬─────────┘              │
│         │                       │                       │
│         └───────────┬───────────┘                       │
│                     │                                   │
│            ┌────────▼──────────┐                        │
│            │ClinicalSummarizer │                        │
│            │   (AI Analysis)   │                        │
│            └────────┬──────────┘                        │
│                     │                                   │
│            ┌────────▼──────────┐                        │
│            │  DatabaseManager  │                        │
│            └────────┬──────────┘                        │
│                     │                                   │
│            ┌────────▼──────────┐                        │
│            │  SQLite Database  │                        │
│            │   (DrugBank Data) │                        │
│            └───────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                         │
            ┌────────────▼────────────┐
            │   Ollama LLM Server     │
            │   (Llama 3.1:8b)        │
            └─────────────────────────┘
```

## 📁 Project Structure

```
Medication_Interaction_Checker/
│
├── app/
│   └── backend/
│       ├── main.py                 # FastAPI application & endpoints
│       ├── config.py               # Configuration (DB path, Ollama settings)
│       ├── database.py             # DatabaseManager class
│       ├── schemas.py              # Pydantic models for requests/responses
│       ├── req_10_sqlite_drugbank.db  # SQLite database
│       └── services/
│           ├── resolver.py         # Drug name resolution logic
│           ├── interaction.py     # Interaction detection engine
│           └── summarizer.py       # AI-powered clinical analysis
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main application component
│   │   ├── api.js                   # API client functions
│   │   ├── main.jsx                 # React entry point
│   │   └── components/
│   │       ├── SearchBar.jsx        # Drug search with autocomplete
│   │       ├── MedicationList.jsx    # Medication list display
│   │       ├── PatientForm.jsx      # Patient profile input
│   │       └── ReportView.jsx       # Interaction report display
│   ├── package.json
│   └── vite.config.js
│
├── sqlite_builder/
│   └── SQL_Builder.py              # Script to build SQLite DB from CSVs
│
├── drugbank_parsed_csvs_required_10/  # Parsed DrugBank CSV files
│   ├── drug_interactions_drugbank_drugs.csv
│   ├── food_interactions_drugbank_drugs_reactions.csv
│   ├── general_information_drugbank_drugs.csv
│   ├── mixtures_drugbank_drugs.csv
│   ├── pharmacology_drugbank_drugs.csv
│   ├── references_*.csv
│   └── synonyms_drugbank_drugs.csv
│
├── Raw_DrugBank_data/
│   └── drugbank_all_full_database/
│       ├── convert_xml2csv.py     # XML to CSV converter
│       └── full_database.xml       # Original DrugBank XML
│
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Ollama installed and running locally
- Llama 3.1:8b model downloaded in Ollama

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Medication_Interaction_Checker
```

### Step 2: Set Up Python Backend

1. Create and activate a conda environment:
```bash
conda create -n DDI python=3.10
conda activate DDI
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the SQLite database exists:
   - The database should be at `app/req_10_sqlite_drugbank.db`
   - If missing, run `sqlite_builder/SQL_Builder.py` to build it from CSV files

### Step 3: Set Up Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the required model:
```bash
ollama pull llama3.1:8b
```

3. Start Ollama server (usually runs automatically):
```bash
ollama serve
```

### Step 4: Set Up React Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Step 5: Configuration

Update `app/backend/config.py` if needed:
- `OLLAMA_URL`: Default is `http://localhost:11434/api/generate`
- `MODEL_NAME`: Default is `llama3.1:8b`
- `DB_FILE`: Path to SQLite database (auto-configured)

## 🎮 Usage

### Starting the Backend Server

```bash
# Activate conda environment
conda activate DDI

# Navigate to project root directory
cd Medication_Interaction_Checker

# Start FastAPI server (run from project root)
uvicorn app.backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Note**: Run uvicorn from the project root directory, not from `app/backend`. This ensures Python recognizes the package structure and relative imports work correctly.

The API will be available at `http://127.0.0.1:8000`

### Starting the Frontend Development Server

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### Using the Application

1. **Enter Patient Information**: Input patient age and gender
2. **Search and Add Medications**: Use the search bar to find medications (supports brand names, generics, synonyms)
3. **Add to List**: Click on a medication to add it (up to 5 medications)
4. **Analyze Interactions**: Click "Check Interactions" button
5. **Review Results**: 
   - View severity-classified interaction warnings
   - Read clinical recommendations
   - Check patient-specific risk assessments
   - Review food interaction warnings
   - Access clinical references

## 📡 API Endpoints

### Search
- **GET** `/search?q={query}` - Search for drugs (autocomplete)
  - Returns: List of drug search results with name, ID, and type

### Analysis
- **POST** `/analyze/interactions` - Detect drug-drug interactions
  - Body: `{ "medications": ["drug1", "drug2", ...] }`
  - Returns: Resolved medications and found interactions

- **POST** `/analyze/food` - Get food interaction warnings
  - Body: `{ "drug_ids": ["DB001", "DB002", ...] }`
  - Returns: Food warnings per drug

- **POST** `/analyze/references` - Get clinical references
  - Body: `{ "drug_ids": ["DB001", "DB002", ...] }`
  - Returns: Articles, links, books, attachments per drug

- **POST** `/analyze/severity` - Classify interaction severity
  - Body: `{ "interactions": [...], "patient": {...} }`
  - Returns: Severity classification for each interaction

- **POST** `/analyze/mechanism` - Get interaction mechanism explanation
  - Body: `{ "interactions": [...], "patient": {...} }`
  - Returns: AI-generated interaction summaries

- **POST** `/analyze/recommendation` - Get clinical recommendations
  - Body: `{ "interactions": [...], "patient": {...} }`
  - Returns: Clinical recommendations per interaction

- **POST** `/analyze/risk` - Get patient-specific risk assessment
  - Body: `{ "interactions": [...], "patient": {...} }`
  - Returns: Patient-specific risk per interaction

- **POST** `/analyze/report` - Get complete AI-generated report
  - Body: `{ "interactions": [...], "patient": {...}, "drug_ids": [...] }`
  - Returns: Complete structured analysis with all components

## 🗄️ Database Schema

The SQLite database contains the following tables:

- **general_info**: Drug names, descriptions, types
- **pharmacology**: Mechanism of action, toxicity, metabolism, clearance
- **drug_interactions**: Drug-drug interaction pairs with descriptions
- **food_interactions**: Food and lifestyle interaction warnings
- **mixtures**: Brand name medications and their ingredients
- **synonyms**: Alternative drug names
- **ref_articles**: PubMed articles and citations
- **ref_links**: External resource links
- **ref_books**: Textbook references
- **ref_attachments**: Document attachments

## 🔧 Dependencies

### Python (requirements.txt)
```
fastapi==0.121.3
uvicorn==0.38.0
pydantic==2.12.4
requests==2.32.5
pandas==2.3.3
numpy==2.0.1
```

### Node.js (frontend/package.json)
- react: ^19.2.0
- axios: ^1.13.2
- tailwindcss: ^3.4.1
- vite: ^7.2.4
- lucide-react: ^0.554.0

## 🎨 Features in Detail

### Drug Resolution System
- **Brand Name Resolution**: Automatically breaks down brand medications (e.g., "Tylenol PM") into active ingredients
- **Synonym Matching**: Handles alternative names and common misspellings
- **Multi-Ingredient Support**: Correctly processes combination medications

### AI-Powered Analysis
- **Severity Classification**: Uses LLM to classify interactions based on clinical descriptions
- **Context-Aware Summaries**: Generates explanations using drug pharmacology data
- **Personalized Risk**: Adjusts risk assessment based on patient demographics
- **Clinical Recommendations**: Provides actionable guidance for healthcare providers

### User Experience
- **Real-time Search**: Fast autocomplete with fuzzy matching
- **Visual Feedback**: Color-coded severity indicators
- **Comprehensive Reports**: All relevant information in one place
- **Responsive Design**: Works on desktop and tablet devices

## 📝 Notes

- The system supports up to 5 medications per analysis
- Ollama must be running locally for AI features to work
- The DrugBank database is a subset (10 required tables) for performance
- All AI analysis is performed locally (no external API calls)

## 🤝 Contributing

This is a portfolio project. For questions or suggestions, please open an issue.

## 📄 License

This project uses the DrugBank database, which has its own licensing terms. Please refer to DrugBank's license agreement for database usage.

## 🙏 Acknowledgments

- **DrugBank**: For providing the comprehensive drug interaction database
- **Ollama**: For the local LLM inference framework
- **FastAPI**: For the excellent Python web framework
- **React & Vite**: For the modern frontend tooling

---

**Built with ❤️ for safer medication management**
