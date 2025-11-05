import React, { useState } from 'react';
import QuestionSearch from './components/QuestionSearch';
import SubjectFilter from './components/SubjectFilter';
import UploadPanel from './components/UploadPanel';
import { BookOpen, Upload, Search } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [selectedSubject, setSelectedSubject] = useState('');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <BookOpen className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SSC Question RAG System</h1>
                <p className="text-sm text-gray-600">Find similar questions and practice for SSC exams</p>
              </div>
            </div>
            
            {/* Navigation Tabs */}
            <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('search')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'search'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Search className="h-4 w-4" />
                <span>Search Questions</span>
              </button>
              
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'upload'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Upload className="h-4 w-4" />
                <span>Upload Papers</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Subject Filter */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <SubjectFilter 
          selectedSubject={selectedSubject}
          onSubjectChange={setSelectedSubject}
        />
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'search' && (
          <QuestionSearch selectedSubject={selectedSubject} />
        )}
        
        {activeTab === 'upload' && (
          <UploadPanel />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>Built for SSC Exam Preparation • RAG-Powered Question Search</p>
            <p className="mt-1">Upload question papers and find similar questions instantly</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
