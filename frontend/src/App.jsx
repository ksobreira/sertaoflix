import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './contexts/AuthContext';
import Login     from './pages/Login/Login';
import Perfis    from './pages/Perfis/Perfis';
import Home      from './pages/Home/Home';
import Dashboard from './pages/Dashboard/Dashboard';

function RotaProtegida({ children }) {
  const { usuario } = useAuth();
  return usuario ? children : <Navigate to="/" replace />;
}

function RotaAdmin({ children }) {
  const { usuario, isAdmin } = useAuth();
  if (!usuario) return <Navigate to="/" replace />;
  if (!isAdmin)  return <Navigate to="/home" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/perfis"    element={<RotaProtegida><Perfis /></RotaProtegida>} />
          <Route path="/home"      element={<RotaProtegida><Home /></RotaProtegida>} />
          <Route path="/dashboard" element={<RotaAdmin><Dashboard /></RotaAdmin>} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;