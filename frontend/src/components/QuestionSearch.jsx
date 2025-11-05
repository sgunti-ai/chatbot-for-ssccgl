import React, { useState } from 'react';
import QuestionCard from './QuestionCard';
import LoadingSpinner from './LoadingSpinner';
import { useSSCAPI } from '../hooks/useSSCAPI';
import { Search, AlertCircle } from 'lucide-react';

const QuestionSearch = ({ selectedSubject }) => {
  const [query, setQuery] = useState('');
  const { queryQuestions, loading, error, results } = useSSCAPI();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    await queryQuestions(query, selectedSubject);
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  const exampleQueries = [
    "profit and loss calculation",
    "trigonometry identities",
    "synonyms for difficult words",
    "number series patterns",
    "geometry triangle problems"
  ];

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Questions
            </label>
            <div className="flex space-x-4">
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a question or topic to find similar questions..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {loading ? <LoadingSpinner size="sm" /> : <Search className="h-4 w-4" />}
                <span>Search</span>
              </button>
            </div>
          </div>
        </form>

        {/* Example Queries */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error: {error}</span>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="space-y-4">
        {results && (
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Found {results.total_matches} similar questions
            </h2>
            {selectedSubject && (
              <span className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm rounded-full">
                Subject: {selectedSubject}
              </span>
            )}
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {results && results.matches.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-1">
            {results.matches.map((match, index) => (
              <QuestionCard
                key={match.question_id || index}
                question={match.question}
                options={match.options}
                correctAnswer={match.correct_answer}
                subject={match.subject}
                similarityScore={match.similarity_score}
              />
            ))}
          </div>
        )}

        {results && results.matches.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No similar questions found</p>
              <p className="mt-1">Try adjusting your search terms or browse different subjects</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionSearch;
