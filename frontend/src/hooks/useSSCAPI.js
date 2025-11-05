import { useState } from 'react';
import { queryQuestions } from '../services/api';

export const useSSCAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const queryQuestionsAPI = async (question, subject = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await queryQuestions(question, subject);
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
    queryQuestions: queryQuestionsAPI,
    loading,
    error,
    results,
    clearResults
  };
};
