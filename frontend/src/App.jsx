import { useState } from 'react';
import { Activity, AlertTriangle } from 'lucide-react';
import SearchBar from './components/SearchBar';
import ReportView from './components/ReportView';
import MedicationList from './components/MedicationList';
import PatientForm from './components/PatientForm';
import { analyzeInteractions } from './api';

function App() {
  const [meds, setMeds] = useState([]);
  const [patient, setPatient] = useState({ age: 65, gender: 'Male' });
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addMed = (med) => {
    if (meds.find(m => m.id === med.id)) return;
    if (meds.length >= 5) return;

    setMeds([...meds, med]);
    setReportData(null);
    setError(null);
  };

  const removeMed = (id) => {
    setMeds(meds.filter(m => m.id !== id));
    setReportData(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (meds.length < 2) return;
    
    setLoading(true);
    setError(null);
    setReportData(null);

    try {
      const medNames = meds.map(m => m.name);
      const data = await analyzeInteractions(medNames, patient);
      setReportData(data);
    } catch (err) {
      console.error("Analysis failed:", err);
      setError("Failed to connect to the analysis server. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 selection:bg-primary selection:text-white font-sans pb-20">
      
      {/* Header */}
      <nav className="border-b border-dark-700 bg-dark-800/50 backdrop-blur-md sticky top-0 z-40 mb-10">
        <div className="max-w-6xl mx-auto px-4 md:px-6 h-16 flex items-center gap-3">
          <div className="bg-gradient-to-tr from-primary to-red-500 p-2 rounded-lg shadow-lg shadow-primary/20">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">
            Drug<span className="text-primary">Guard</span> AI
          </h1>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 md:px-6">
        
        {/* Hero */}
        <div className="text-center mb-12 animate-fade-in-down">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-4 bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
            Medication Safety Check
          </h2>
          <p className="text-gray-400 max-w-lg mx-auto text-lg">
            Real-time interaction analysis powered by DrugBank & Llama.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Sidebar */}
          <div className="lg:col-span-4 space-y-6 sticky top-24">
            
            <div className="bg-dark-800 p-6 rounded-2xl border border-dark-700 shadow-xl shadow-black/20">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-5 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary"></span>
                1. Patient Profile
              </h3>
              <PatientForm patient={patient} onChange={setPatient} />
            </div>

            <div className="bg-dark-800 p-6 rounded-2xl border border-dark-700 shadow-xl shadow-black/20">
              <div className="flex justify-between items-center mb-5">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  2. Medication List
                </h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  meds.length === 5 
                    ? 'bg-red-500/10 text-red-400 border-red-500/20' 
                    : 'bg-dark-900 text-gray-400 border-dark-600'
                }`}>
                  {meds.length}/5
                </span>
              </div>
              
              <MedicationList meds={meds} onRemove={removeMed} />

              <button
                onClick={handleAnalyze}
                disabled={meds.length < 2 || loading}
                className={`w-full mt-6 py-3.5 rounded-xl font-bold text-sm uppercase tracking-wide transition-all duration-300 flex items-center justify-center gap-2 shadow-lg ${
                  meds.length < 2 || loading
                    ? 'bg-dark-700 text-gray-500 cursor-not-allowed border border-dark-600' 
                    : 'bg-primary hover:bg-secondary text-white shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5 active:translate-y-0 border border-primary'
                }`}
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  "Check Interactions"
                )}
              </button>
            </div>
          </div>

          {/* Right Content */}
          <div className="lg:col-span-8 space-y-6">
            
            <SearchBar onAdd={addMed} />
            
            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-center gap-3 animate-shake">
                <AlertTriangle className="h-5 w-5 shrink-0" />
                <div>
                    <p className="font-bold text-sm">Error</p>
                    <p className="text-sm opacity-90">{error}</p>
                </div>
              </div>
            )}

            {loading && !reportData && (
              <div className="flex flex-col items-center justify-center py-24 space-y-6 bg-dark-800/30 rounded-2xl border border-dark-700/50 animate-pulse backdrop-blur-sm">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Activity className="h-6 w-6 text-primary/50" />
                  </div>
                </div>
                <div className="text-center space-y-2">
                  <p className="text-xl font-semibold text-white">Consulting AI Pharmacist...</p>
                  <p className="text-sm text-gray-500">Analyzing pharmacological mechanisms & risk factors</p>
                </div>
              </div>
            )}

            {!loading && reportData && (
              <div className="animate-fade-in-up">
                <ReportView data={reportData} />
              </div>
            )}
            
            {!loading && !reportData && !error && (
              <div className="flex flex-col items-center justify-center py-32 text-center border-2 border-dashed border-dark-700 rounded-2xl opacity-40 hover:opacity-60 transition-opacity">
                <div className="bg-dark-800 p-4 rounded-full mb-4">
                  <Activity className="h-8 w-8 text-gray-500" />
                </div>
                <h3 className="text-lg font-medium text-gray-300">Ready to Analyze</h3>
                <p className="text-sm text-gray-500 mt-1 max-w-xs mx-auto">
                  Add medications from the search bar to see interactions here.
                </p>
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}

export default App;