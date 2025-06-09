import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import FileSystem from './pages/FileSystem';
import Processes from './pages/Processes';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="system" element={<Dashboard />} />
          <Route path="files" element={<FileSystem />} />
          <Route path="processes" element={<Processes />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
