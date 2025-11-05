import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, XCircle, BookOpen } from 'lucide-react';

const QuestionCard = ({ 
  question, 
  options, 
  correctAnswer, 
  subject, 
  similarityScore 
}) => {
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    setShowAnswer(true);
  };

  const isCorrect = (option) => {
    if (!showAnswer) return null;
    const optionText = typeof option === 'string' ? option.split('. ')[1] || option : option;
    return optionText === correctAnswer;
  };

  const formatOption = (option) => {
    if (typeof option === 'string') {
      return option;
    }
    return Array.isArray(option) ? option.join(', ') : String(option);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
      {/* Question Header */}
      <div className="p-6 border-b">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <p className="text-gray-900 font-medium leading-relaxed">{question}</p>
          </div>
          <div className="flex items-center space-x-3 ml-4">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              {Math.round(similarityScore * 100)}% match
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <BookOpen className="h-4 w-4" />
            <span>{subject}</span>
          </div>
        </div>
      </div>

      {/* Options */}
      <div className="p-6">
        <div className="space-y-3">
          {options && options.map((option, index) => {
            const optionText = formatOption(option);
            const correct = isCorrect(optionText);
            
            return (
              <div
                key={index}
                onClick={() => !showAnswer && handleOptionSelect(optionText)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  !showAnswer
                    ? 'hover:bg-gray-50 border-gray-200'
                    : correct
                    ? 'bg-green-50 border-green-200'
                    : selectedOption === optionText
                    ? 'bg-red-50 border-red-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-gray-900">{optionText}</span>
                  
                  {showAnswer && (
                    <div>
                      {correct ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : selectedOption === optionText ? (
                        <XCircle className="h-5 w-5 text-red-600" />
                      ) : null}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Answer Toggle */}
        {correctAnswer && (
          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => setShowAnswer(!showAnswer)}
              className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 text-sm font-medium"
            >
              {showAnswer ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  <span>Hide Answer</span>
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  <span>Show Answer</span>
                </>
              )}
            </button>

            {showAnswer && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Correct Answer:</strong> {correctAnswer}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;
