import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario]   = useState(null); // { email }
  const [perfil, setPerfil]     = useState(null); // { id, nome, emoji, cor }
  const [isAdmin, setIsAdmin]   = useState(false);

  function login(email, senha) {
    // TODO: chamar POST /api/auth/login quando backend estiver pronto
    if (email === 'admin@sertaoflix.com') {
      setIsAdmin(true);
      setUsuario({ email });
      return 'admin';
    }
    setIsAdmin(false);
    setUsuario({ email });
    return 'perfis';
  }

  function logout() {
    setUsuario(null);
    setPerfil(null);
    setIsAdmin(false);
  }

  return (
    <AuthContext.Provider value={{ usuario, perfil, setPerfil, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
