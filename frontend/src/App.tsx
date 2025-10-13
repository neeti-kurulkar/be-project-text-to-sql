import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import AskQuestionPage from './pages/AskQuestionPage';
import SummaryPage from './pages/SummaryPage';
import DocumentsPage from './pages/DocumentsPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/ask" element={<AskQuestionPage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;