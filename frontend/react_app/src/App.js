import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import EvaluateForm from './components/EvaluateForm';
import BatchUpload from './components/BatchUpload';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<EvaluateForm />} />
            <Route path="/batch" element={<BatchUpload />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>Agentic Evaluation System © 2024</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
