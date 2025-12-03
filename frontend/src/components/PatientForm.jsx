import { useState, useEffect, useRef } from 'react';
import { Check, ChevronDown, X } from 'lucide-react';

const COMMON_CONDITIONS = [
  "Diabetes", "Hypertension", "Pregnancy", "Asthma",
  "Kidney Disease", "Liver Disease", "Heart Disease",
  "Bleeding Disorders", "Ulcers", "Epilepsy"
];

export default function PatientForm({ patient, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleNumberChange = (field, val) => {
    if (val === "") {
      onChange({ ...patient, [field]: "" });
      return;
    }
    const parsed = parseFloat(val);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 300) {
      onChange({ ...patient, [field]: parsed });
    }
  };

  const toggleCondition = (condition) => {
    const current = patient.conditions || [];
    if (current.includes(condition)) {
      onChange({ ...patient, conditions: current.filter(c => c !== condition) });
    } else {
      onChange({ ...patient, conditions: [...current, condition] });
    }
  };

  const removeCondition = (condition) => {
    const current = patient.conditions || [];
    onChange({ ...patient, conditions: current.filter(c => c !== condition) });
  };

  const isConditionDisabled = (condition) => {
    if (condition === "Pregnancy" && patient.gender === "Male") return true;
    return false;
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Age */}
        <div>
          <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Age</label>
          <input
            type="number"
            value={patient.age ?? ""}
            onChange={(e) => handleNumberChange('age', e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm placeholder-gray-600 hover:border-dark-600"
            min="0"
            max="120"
            placeholder="Age"
          />
        </div>
        {/* Gender */}
        <div>
          <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Gender</label>
          <div className="relative">
            <select
              value={patient.gender ?? ""}
              onChange={(e) => {
                const newGender = e.target.value;
                let newConditions = patient.conditions || [];
                if (newGender === "Male" && newConditions.includes("Pregnancy")) {
                  newConditions = newConditions.filter(c => c !== "Pregnancy");
                }
                onChange({ ...patient, gender: newGender, conditions: newConditions });
              }}
              className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm appearance-none cursor-pointer hover:border-dark-600"
            >
              <option value="" disabled>Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
              <ChevronDown className="h-4 w-4" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Weight */}
        <div>
          <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Weight (kg)</label>
          <input
            type="number"
            value={patient.weight ?? ""}
            onChange={(e) => handleNumberChange('weight', e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm placeholder-gray-600 hover:border-dark-600"
            min="0"
            max="300"
            placeholder="kg"
          />
        </div>
        {/* Height */}
        <div>
          <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Height (cm)</label>
          <input
            type="number"
            value={patient.height ?? ""}
            onChange={(e) => handleNumberChange('height', e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm placeholder-gray-600 hover:border-dark-600"
            min="0"
            max="300"
            placeholder="cm"
          />
        </div>
      </div>

      {/* Conditions Dropdown */}
      <div className="relative" ref={dropdownRef}>
        <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Medical Conditions</label>

        <div
          className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 min-h-[42px] cursor-pointer hover:border-dark-600 flex flex-wrap gap-2 items-center"
          onClick={() => setIsOpen(!isOpen)}
        >
          {(!patient.conditions || patient.conditions.length === 0) && (
            <span className="text-gray-600 text-sm">Select conditions...</span>
          )}

          {patient.conditions?.map(c => (
            <span key={c} className="bg-dark-700 text-gray-200 text-xs px-2 py-0.5 rounded-md flex items-center gap-1 border border-dark-600">
              {c}
              <X
                className="h-3 w-3 cursor-pointer hover:text-white"
                onClick={(e) => { e.stopPropagation(); removeCondition(c); }}
              />
            </span>
          ))}

          <div className="ml-auto pointer-events-none text-gray-500">
            <ChevronDown className="h-4 w-4" />
          </div>
        </div>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-dark-800 border border-dark-700 rounded-lg shadow-xl max-h-60 overflow-y-auto">
            {COMMON_CONDITIONS.map(condition => {
              const disabled = isConditionDisabled(condition);
              const selected = patient.conditions?.includes(condition);

              return (
                <div
                  key={condition}
                  className={`px-3 py-2 flex items-center justify-between text-sm transition-colors ${disabled
                      ? 'opacity-50 cursor-not-allowed text-gray-600'
                      : 'cursor-pointer hover:bg-dark-700 text-gray-200'
                    }`}
                  onClick={() => !disabled && toggleCondition(condition)}
                >
                  <span>{condition}</span>
                  {selected && <Check className="h-4 w-4 text-primary" />}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}