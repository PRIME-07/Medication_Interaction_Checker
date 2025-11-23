import { AlertTriangle, ShieldAlert, CheckCircle, Info, BookOpen, Apple } from 'lucide-react';

export default function ReportView({ data }) {
  if (!data) return null;

  // Data structure coming from API
  const { report, food, references } = data;
  const cards = report.analysis_cards || [];
  const interactionCount = cards.length;

  // Helper for dynamic severity styling
  const getSeverityStyles = (severity) => {
    const s = severity ? severity.toLowerCase() : 'unknown';
    if (s.includes('high') || s.includes('severe') || s.includes('major')) {
      return {
        bg: 'bg-red-500/10',
        border: 'border-red-500/30',
        text: 'text-red-400',
        badge: 'bg-red-500 text-white'
      };
    }
    if (s.includes('mod')) {
      return {
        bg: 'bg-orange-500/10',
        border: 'border-orange-500/30',
        text: 'text-orange-400',
        badge: 'bg-orange-500 text-white'
      };
    }
    return {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      text: 'text-yellow-400',
      badge: 'bg-yellow-500 text-black'
    };
  };

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* 1. Summary Status Header */}
      <div className={`p-6 rounded-xl border flex items-start gap-4 ${
        interactionCount > 0 
          ? 'bg-red-500/5 border-red-500/20' 
          : 'bg-green-500/5 border-green-500/20'
      }`}>
        <div className={`p-3 rounded-full ${interactionCount > 0 ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
          {interactionCount > 0 ? <AlertTriangle size={24} /> : <CheckCircle size={24} />}
        </div>
        <div>
          <h2 className={`text-xl font-bold mb-1 ${interactionCount > 0 ? "text-red-400" : "text-green-400"}`}>
            {interactionCount > 0 
              ? `${interactionCount} Interaction${interactionCount > 1 ? 's' : ''} Detected` 
              : "No Known Drug-Drug Interactions Found"}
          </h2>
          <p className="text-sm text-gray-400">
            {interactionCount > 0 
              ? "Review the clinical analysis cards below for detailed management strategies." 
              : "No known interactions were found between the selected medications in the database."}
          </p>
        </div>
      </div>

      {/* 2. Clinical Analysis Cards*/}
      {interactionCount > 0 && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 mb-2">
            <ShieldAlert className="text-primary w-5 h-5" />
            <h3 className="text-lg font-bold text-white">Clinical Analysis</h3>
          </div>
          
          {cards.map((card, idx) => {
            const styles = getSeverityStyles(card.severity);
            
            return (
              <div key={idx} className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden shadow-lg hover:border-dark-600 transition-all">
                
                {/* Card Header */}
                <div className={`px-6 py-4 border-b border-dark-700 flex justify-between items-center ${styles.bg}`}>
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="text-lg font-bold text-white">{card.drug_a}</span>
                    <span className="text-gray-500 font-light">↔</span>
                    <span className="text-lg font-bold text-white">{card.drug_b}</span>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm ${styles.badge}`}>
                    {card.severity}
                  </span>
                </div>

                {/* Card Body */}
                <div className="p-6 space-y-5">
                  
                  {/* Interaction Summary*/}
                  <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <Info size={14} /> Interaction Summary
                    </h4>
                    <p className="text-gray-300 text-sm leading-relaxed bg-dark-900/50 p-3 rounded-lg border border-dark-700/50">
                      {/* Check both fields for backward compatibility */}
                      {card.interaction_summary || card.mechanism}
                    </p>
                  </div>

                  {/* Grid for Actionable Info */}
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Recommendation */}
                    <div className="bg-blue-500/5 p-4 rounded-lg border border-blue-500/10">
                      <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">
                        Clinical Recommendation
                      </h4>
                      <p className="text-sm text-gray-300">
                        {card.recommendation}
                      </p>
                    </div>

                    {/* Patient Risk */}
                    <div className="bg-orange-500/5 p-4 rounded-lg border border-orange-500/10">
                      <h4 className="text-xs font-bold text-orange-400 uppercase tracking-wider mb-2">
                        Patient Specific Risk
                      </h4>
                      <p className="text-sm text-gray-300">
                        {card.patient_risk}
                      </p>
                    </div>
                  </div>

                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 3. Food Interactions */}
      {Object.keys(food.food_warnings).length > 0 && (
        <div className="bg-dark-800 rounded-xl border border-dark-700 overflow-hidden">
          <div className="bg-dark-900/50 px-6 py-4 border-b border-dark-700 flex items-center gap-2">
            <Apple className="text-yellow-500 w-5 h-5" />
            <h3 className="font-semibold text-white">Food & Lifestyle Interactions</h3>
          </div>
          <div className="p-6 grid gap-6 md:grid-cols-2">
            {Object.entries(food.food_warnings).map(([drug, warnings]) => (
              <div key={drug} className="bg-dark-900 p-4 rounded-lg border border-dark-700">
                <div className="flex items-center gap-2 mb-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-yellow-500"></div>
                    <h4 className="font-medium text-white text-sm uppercase tracking-wider">{drug}</h4>
                </div>
                <ul className="space-y-2">
                  {warnings.map((w, i) => (
                    <li key={i} className="text-sm text-gray-400 flex items-start gap-2">
                        <span className="text-dark-600 mt-1">•</span>
                        {w}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. References */}
      <div className="bg-dark-800/30 rounded-xl border border-dark-700/50">
        <div className="px-6 py-4 border-b border-dark-700/50 flex items-center gap-2">
          <BookOpen className="text-blue-400 w-5 h-5" />
          <h3 className="font-semibold text-gray-300">Clinical References</h3>
        </div>
        <div className="p-6 space-y-6">
            {Object.entries(references.references).map(([drug, refs]) => (
            <div key={drug} className="relative pl-4 border-l-2 border-dark-700 hover:border-blue-500/50 transition-colors">
                <h4 className="font-bold text-white mb-2 text-sm">{drug}</h4>
                
                <div className="space-y-3">
                    {/* Articles */}
                    {refs.articles.length > 0 && (
                        <div className="text-xs">
                            <span className="text-gray-500 font-semibold uppercase tracking-wider block mb-1">Articles</span>
                            <div className="space-y-1">
                                {refs.articles.slice(0, 2).map((art, i) => (
                                    <p key={i} className="text-gray-400 truncate hover:text-white transition-colors">📄 {art}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Links */}
                    {refs.links.length > 0 && (
                        <div className="text-xs">
                            <span className="text-gray-500 font-semibold uppercase tracking-wider block mb-1">External Resources</span>
                            <div className="space-y-1">
                                {refs.links.slice(0, 2).map((link, i) => (
                                    <a key={i} href={link.split(': ')[1]} target="_blank" rel="noopener noreferrer" className="block text-blue-400/80 hover:text-blue-300 truncate hover:underline">
                                        🔗 {link.split(': ')[0]}
                                    </a>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
            ))}
        </div>
      </div>
    </div>
  );
}