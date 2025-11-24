import { useState, useEffect, useRef } from 'react';
import { Search, Plus, Loader2 } from 'lucide-react';
import { searchDrugs } from '../api';

export default function SearchBar({ onAdd }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length >= 2) {
        setLoading(true);
        try {
          const data = await searchDrugs(query);
          // Ensure data is an array before setting results
          if (Array.isArray(data)) {
            setResults(data);
            setShowDropdown(true);
          } else {
            console.error("Search returned non-array data:", data);
            setResults([]);
            setShowDropdown(false);
          }
        } catch (e) {
          console.error("Search error:", e);
          setResults([]);
          setShowDropdown(false);
        } finally {
          setLoading(false);
        }
      } else {
        setResults([]);
        setShowDropdown(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (item) => {
    onAdd(item);
    setQuery('');
    setResults([]);
    setShowDropdown(false);
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-xl mx-auto mb-8 z-50">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowDropdown(true);
          }}
          placeholder="Search medication (e.g., Tylenol)..."
          className="w-full bg-dark-800 border border-dark-700 rounded-lg py-3 pl-10 pr-10 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-white placeholder-gray-500 shadow-lg"
        />
        <Search className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" />
        
        {loading && (
            <div className="absolute right-3 top-3.5">
                <Loader2 className="h-5 w-5 text-primary animate-spin" />
            </div>
        )}
      </div>

      {/* Dropdown Results */}
      {showDropdown && Array.isArray(results) && results.length > 0 && (
        <div className="absolute w-full mt-2 bg-dark-800 border border-dark-700 rounded-lg shadow-2xl max-h-60 overflow-y-auto overflow-x-hidden z-[100]">
          {results.map((item, idx) => (
            <button
              key={`${item.id}-${idx}`}
              onClick={() => handleSelect(item)}
              className="w-full text-left px-4 py-3 hover:bg-dark-700 flex justify-between items-center group border-b border-dark-700/50 last:border-0 transition-colors cursor-pointer"
            >
              <div className="flex flex-col">
                <span className="font-medium text-white text-sm">{item.name}</span>
                {/* Show generic name if it's a brand, or ID for context */}
                <span className="text-[10px] text-gray-500">{item.id}</span>
              </div>
              
              <span className={`ml-2 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded border font-bold ${
                  item.type === 'Brand' ? 'border-blue-500/30 text-blue-400 bg-blue-500/10' : 
                  item.type === 'Generic' ? 'border-green-500/30 text-green-400 bg-green-500/10' :
                  'border-gray-600 text-gray-400'
              }`}>
                {item.type}
              </span>
            </button>
          ))}
        </div>
      )}
      
      {showDropdown && query.length >= 2 && !loading && results.length === 0 && (
         <div className="absolute w-full mt-2 bg-dark-800 border border-dark-700 rounded-lg shadow-xl p-4 text-center text-gray-500 text-sm z-[100]">
            No matches found for "{query}"
         </div>
      )}
    </div>
  );
}