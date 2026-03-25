import { Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './auth/ProtectedRoute';
import PublicOnlyRoute from './auth/PublicOnlyRoute';
import DemoWorkspace from './pages/DemoWorkspace';
import EmailActionHandler from './pages/EmailActionHandler';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DemoWorkspace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DemoWorkspace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/signin"
        element={
          <PublicOnlyRoute>
            <SignIn />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicOnlyRoute>
            <SignUp />
          </PublicOnlyRoute>
        }
      />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/auth/action" element={<EmailActionHandler />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
