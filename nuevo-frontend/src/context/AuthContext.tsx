import { createContext, useContext, useState, ReactNode } from 'react';

// Contexto de autenticación simulado (Mock) temporal tras la migración a TiDB
const AuthContext = createContext<any>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    // Simulamos que siempre hay un usuario logueado para no bloquear el desarrollo
    const [session] = useState({ user: { email: 'admin@evaluate.local' } });

    const signInWithGoogle = async () => console.log('Login simulado (Migrando sistema)');
    const signOut = async () => console.log('Logout simulado');

    return (
        <AuthContext.Provider value={{ session, signInWithGoogle, signOut }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);