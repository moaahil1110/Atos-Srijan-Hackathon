import { Navigate, useLocation } from 'react-router-dom';
import FullScreenLoader from '../components/FullScreenLoader';
import { useAuth } from './AuthProvider';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const { initialized, signedIn } = useAuth();

  if (!initialized) {
    return <FullScreenLoader />;
  }

  if (!signedIn) {
    return <Navigate to="/signin" replace state={{ from: location }} />;
  }

  return children;
}
