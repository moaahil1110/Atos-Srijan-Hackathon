import { createContext, useContext, useEffect, useState } from 'react';
import { setupAuthObserver } from '../firebase/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({
    initialized: false,
    signedIn: false,
    user: null,
  });

  useEffect(() => {
    const unsubscribe = setupAuthObserver((authState) => {
      setState({
        initialized: true,
        signedIn: authState.signedIn,
        user: authState.user,
      });
    });

    return unsubscribe;
  }, []);

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
