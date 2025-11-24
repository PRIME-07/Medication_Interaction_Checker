export default function PatientForm({ patient, onChange }) {
  
  const handleAgeChange = (e) => {
    const val = e.target.value;
    if (val === "") {
        onChange({...patient, age: ""});
        return;
    }
    const parsed = parseInt(val);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 120) {
        onChange({...patient, age: parsed});
    }
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Age</label>
        <input 
          type="number" 
          value={patient.age ?? ""} 
          onChange={handleAgeChange}
          className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm placeholder-gray-600 hover:border-dark-600"
          min="0"
          max="120"
          placeholder="Age"
        />
      </div>
      <div>
        <label className="block text-[10px] font-bold mb-1.5 text-gray-500 uppercase tracking-wider">Gender</label>
        <div className="relative">
          <select 
            value={patient.gender ?? ""}
            onChange={(e) => onChange({...patient, gender: e.target.value})}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-white text-sm appearance-none cursor-pointer hover:border-dark-600"
          >
            <option value="" disabled>Select gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
            <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}