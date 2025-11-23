import { Pill, Trash2 } from 'lucide-react';

export default function MedicationList({ meds, onRemove }) {
  return (
    <div className="space-y-2 min-h-[100px]">
      {meds.length === 0 && (
        <div className="h-full flex flex-col items-center justify-center text-gray-600 py-8 border-2 border-dashed border-dark-700 rounded-lg opacity-50">
            <p className="text-sm italic">No medications added.</p>
        </div>
      )}
      {meds.map((med) => (
        <div key={med.id} className="flex justify-between items-center bg-dark-900 p-3 rounded-lg border border-dark-700 group hover:border-gray-600 transition-all duration-200 hover:shadow-md">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-dark-800 rounded-md text-gray-400 group-hover:text-primary transition-colors">
                <Pill className="h-4 w-4" />
            </div>
            <div>
                <p className="text-sm font-medium text-white">{med.name}</p>
                <p className="text-xs text-gray-500">{med.id}</p>
            </div>
          </div>
          <button 
            onClick={() => onRemove(med.id)} 
            className="text-gray-500 hover:text-red-400 p-2 rounded-md hover:bg-dark-800 transition-colors"
            aria-label={`Remove ${med.name}`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}