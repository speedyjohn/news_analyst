import { Route, Routes, useSearchParams } from 'react-router-dom';
import Footer from './components/Footer';
import Header from './components/Header';
import AuthPage from './pages/AuthPage';
import Feed from './pages/Feed';
import Legal from './pages/Legal';
import MyQuestions from './pages/MyQuestions';
import NewsPage from './pages/NewsPage';
import QuestionPage from './pages/QuestionPage';
import Sources from './pages/Sources';

export default function App() {
  const [params] = useSearchParams();

  return (
    <div style={{ minHeight: '100vh', background: '#f5f6f7', display: 'flex', flexDirection: 'column' }}>
      <Header date={params.get('date')} />
      <div style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/news/:id" element={<NewsPage />} />
          <Route path="/questions/mine" element={<MyQuestions />} />
          <Route path="/questions/:id" element={<QuestionPage />} />
          <Route path="/legal" element={<Legal />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/auth" element={<AuthPage />} />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}
