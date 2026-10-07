import { useState } from 'react';
import { AppLayout, PageId } from './layouts/AppLayout';
import { useAnalysis } from './hooks/useAnalysis';
import Dashboard from './pages/Dashboard';
import SignalAnalysis from './pages/SignalAnalysis';
import { ConstellationPage, Spectrum, WaterfallPage } from './pages/Visuals';
import { BitStream, Fec, Modulation } from './pages/Decode';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

export default function App() {
  const [page, setPage] = useState<PageId>('Dashboard');
  const a = useAnalysis();
  const pages: Record<PageId, JSX.Element> = {
    Dashboard: <Dashboard a={a} />,
    'Signal Analysis': <SignalAnalysis a={a} />,
    Spectrum: <Spectrum a={a} />,
    Waterfall: <WaterfallPage a={a} />,
    Constellation: <ConstellationPage a={a} />,
    Modulation: <Modulation a={a} />,
    'Bit Stream': <BitStream a={a} />,
    'FEC / Interleaving': <Fec a={a} />,
    'Signal Profile': <Profile a={a} />,
    Settings: <Settings />,
  };

  return (
    <div className="min-h-screen bg-bg text-main flex flex-col font-sans">
      <AppLayout page={page} setPage={setPage} a={a}>
        {pages[page]}
      </AppLayout>
    </div>
  );
}
