import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';

// ==========================================
// 1. TIPOS DE DOMINIO PROPIOS (AGNÓSTICOS)
// ==========================================
export interface User {
  id: string;
  email: string;
  name?: string;
  avatarUrl?: string;
  // Campos futuros extraídos de TiDB
  role?: string; 
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ==========================================
// 2. PROVEEDOR DE CONTEXTO
// ==========================================
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Validación inicial de sesión contra FastAPI
  const checkSession = useCallback(async () => {
    try {
      // El backend leerá la cookie HTTP-Only segura o el token de cabecera
      const response = await fetch('/api/auth/me', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error validando la sesión del usuario:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  // ==========================================
  // 3. FLUJOS DE AUTENTICACIÓN DELEGADOS
  // ==========================================
  const signInWithGoogle = () => {
    // Redirección directa al backend. FastAPI negocia con Google y crea la sesión en TiDB.
    window.location.href = '/api/auth/google/login';
  };

  const signOut = async () => {
    try {
      setLoading(true);
      // Petición destructiva al servidor para purgar la cookie/token
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      setUser(null);
      setLoading(false);
      // Redirección limpia al home para purgar vistas protegidas
      window.location.href = '/';
    }
  };

  const value = {
    user,
    loading,
    signInWithGoogle,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ==========================================
// 4. CUSTOM HOOK
// ==========================================
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado estrictamente dentro de un AuthProvider');
  }
  return context;
};