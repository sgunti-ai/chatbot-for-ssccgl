import React from 'react';
import { BookOpen } from 'lucide-react';

const subjects = [
  { value: '', label: 'All Subjects' },
  { value: 'General Intelligence and Reasoning', label: 'General Intelligence & Reasoning' },
  { value: 'Quantitative Aptitude', label: 'Quantitative Aptitude' },
  { value: 'English Comprehension', label: 'English Comprehension' },
  { value: 'General Awareness', label: 'General Awareness' },
  { value: 'Mathematics', label: 'Mathematics' },
  { value: 'Reasoning', label: 'Reasoning' },
  { value: 'English', label: 'English' },
  { value: 'GK', label: 'General Knowledge' }
];

const SubjectFilter = ({ selectedSubject, onSubjectChange }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <div className="flex items-center space-x-3 mb-3">
        <BookOpen className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-medium text-gray-900">Filter by Subject</h3>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {subjects.map((subject) => (
          <button
            key={subject.value}
            onClick={() => onSubjectChange(subject.value)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedSubject === subject.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {subject.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SubjectFilter;
