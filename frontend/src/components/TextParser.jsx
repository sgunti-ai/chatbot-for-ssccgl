import React, { useState } from 'react';
import { useParseAPI } from '../hooks/useParseAPI';

// Simple text parser UI that calls the /parse-text endpoint via the hook
const TextParser = () => {
  const [text, setText] = useState('');
  const { parseText, loading, error, results, clearResults } = useParseAPI();

  const handleParse = async () => {
    if (!text.trim()) return;
    await parseText(text);
  };

  return (
    <section aria-labelledby="text-parser-heading" className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <h3 id="text-parser-heading" className="text-sm font-medium text-gray-900 mb-2">Quick Parse (paste text)</h3>

      <label htmlFor="text-parser-input" className="sr-only">Paste question text</label>
      <textarea
        id="text-parser-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste question text or a block of text from a PDF here..."
        className="w-full min-h-[120px] p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
        disabled={loading}
        aria-label="Paste question text to parse"
      />

      <div className="flex items-center space-x-2 mt-3">
        <button
          onClick={handleParse}
          disabled={loading || !text.trim()}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          aria-pressed={loading}
        >
          {loading ? 'Parsing...' : 'Parse Text'}
        </button>
        <button
          onClick={() => { setText(''); clearResults(); }}
          type="button"
          className="px-3 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          aria-label="Clear text and results"
        >
          Clear
        </button>
      </div>

      {error && (
        <div role="alert" className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">Error: {error}</div>
      )}

      {results && (
        <div className="mt-3" aria-live="polite">
          <div className="text-sm text-gray-600 mb-2">Found {results.total} questions</div>
          <div className="space-y-3">
            {results.questions.map((q) => (
              <article key={q.question_id} className="p-3 border rounded-md bg-white">
                <div className="font-medium text-gray-900">{q.text}</div>
                <ul className="mt-2 list-disc list-inside text-sm text-gray-700">
                  {q.options.map((opt, i) => (
                    <li key={i}>{opt}</li>
                  ))}
                </ul>
                {q.correct_answer && (
                  <div className="mt-2 text-sm text-green-700">Answer: {q.correct_answer}</div>
                )}
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default TextParser;
