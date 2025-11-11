import { useState } from 'react';
import { parseText } from '../services/api';

export const useParseAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const parseTextAPI = async (text) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await parseText(text);
      setResults(response);
      return response;
    } catch (err) {
      setError(err.message);
      setResults(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults(null);
    setError(null);
  };

  return {
    parseText: parseTextAPI,
    loading,
    error,
    results,
    clearResults
  };
};
