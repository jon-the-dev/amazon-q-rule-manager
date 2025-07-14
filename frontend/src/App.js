import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import RuleDetail from './pages/RuleDetail';
import './App.css';

function App() {
  return (
    <Router basename="/amazonq-rules">
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/rule/:ruleName" element={<RuleDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
