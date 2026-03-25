import { Navigate } from 'react-router-dom';
import FullScreenLoader from '../components/FullScreenLoader';
import { useAuth } from './AuthProvider';

export default function PublicOnlyRoute({ children }) {
  const { initialized, signedIn } = useAuth();

  if (!initialized) {
    return <FullScreenLoader />;
  }

  if (signedIn) {
    return <Navigate to="/" replace />;
  }

  return children;
}
