import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { TierList } from './pages/TierList';
import { DeckBrowser } from './pages/DeckBrowser';
import { DeckViewer } from './pages/DeckViewer';
import { Matchups } from './pages/Matchups';
import { Market } from './pages/Market';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<TierList />} />
            <Route path="/decks" element={<DeckBrowser />} />
            <Route path="/decks/:deckId" element={<DeckViewer />} />
            <Route path="/matchups" element={<Matchups />} />
            <Route path="/market" element={<Market />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
