import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Storefront from './Storefront';
import AdminDashboard from './AdminDashboard';
import './index.css'; // Make sure your CSS is imported here

function App() {
  return (
    <Router>
      {/* Simple Navigation Bar */}
      <nav style={{ 
          padding: '15px 40px', 
          background: '#2c3e50', 
          color: 'white', 
          display: 'flex', 
          gap: '20px',
          alignItems: 'center'
      }}>
        <h2 style={{ margin: 0, marginRight: 'auto' }}>TrendThread</h2>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>Shop</Link>
        <Link to="/admin" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>Admin Panel</Link>
      </nav>

      {/* Page Routing Logic */}
      <Routes>
        <Route path="/" element={<Storefront />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;