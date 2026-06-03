import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { perfil, logout } = useAuth();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const avatarRef = useRef(null);  // <- novo

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // <- novo: fecha o dropdown ao clicar fora
  useEffect(() => {
    function handleClickFora(e) {
      if (avatarRef.current && !avatarRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickFora);
    return () => document.removeEventListener('mousedown', handleClickFora);
  }, []);

  return (
    <nav className={`${styles.nav} ${scrolled ? styles.scrolled : ''}`}>
      <div className={styles.logo} onClick={() => navigate('/home')}>
        SERTÃO<span>FLIX</span>
      </div>

      <div className={styles.links}>
        <button className={styles.link} onClick={() => navigate('/home')}>Início</button>
        <button className={styles.link} onClick={() => navigate('/home')}>Filmes</button>
        <button className={styles.link} onClick={() => navigate('/home')}>Em Cartaz</button>
      </div>

      <div className={styles.right}>
        {perfil && (
          <div
            ref={avatarRef}  // <- novo
            className={styles.avatar}
            style={{ background: perfil.cor }}
            onClick={() => setMenuOpen(m => !m)}
          >
            {perfil.emoji}
            {menuOpen && (
              <div className={styles.dropdown}>
                <button onClick={() => navigate('/perfis')}>Trocar Perfil</button>
                <button onClick={() => { logout(); navigate('/'); }}>Sair</button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}