import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { confirmPasswordReset, verifyPasswordResetCode } from 'firebase/auth';
import AuthShell from '../components/AuthShell';
import { auth } from '../firebase/config';
import { validatePasswordStrength } from '../firebase/authService';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [email, setEmail] = useState('');
  const [validCode, setValidCode] = useState(false);
  const [showPasswordRules, setShowPasswordRules] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState({
    minLength: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  });

  const oobCode = searchParams.get('oobCode');
  const mode = searchParams.get('mode');

  useEffect(() => {
    const verifyCode = async () => {
      if (!oobCode || mode !== 'resetPassword') {
        setError('Invalid or expired password reset link.');
        setVerifying(false);
        return;
      }

      try {
        const userEmail = await verifyPasswordResetCode(auth, oobCode);
        setEmail(userEmail);
        setValidCode(true);
      } catch (err) {
        console.error('Code verification error:', err);
        setError('This password reset link is invalid or has expired.');
      } finally {
        setVerifying(false);
      }
    };

    verifyCode();
  }, [mode, oobCode]);

  useEffect(() => {
    if (!password) {
      setPasswordValidation({
        minLength: false,
        uppercase: false,
        lowercase: false,
        number: false,
        special: false,
      });
      return;
    }

    setPasswordValidation({
      minLength: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^a-zA-Z0-9]/.test(password),
    });
  }, [password]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    if (!password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    const missingRequirements = [];

    if (password.length < 8) {
      missingRequirements.push('minimum 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
      missingRequirements.push('at least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      missingRequirements.push('at least one lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
      missingRequirements.push('at least one number');
    }
    if (!/[^a-zA-Z0-9]/.test(password)) {
      missingRequirements.push('at least one special character');
    }

    if (missingRequirements.length > 0) {
      setError(`Password requirements not met: ${missingRequirements.join(', ')}`);
      setShowPasswordRules(true);
      return;
    }

    const validation = await validatePasswordStrength(password);

    if (!validation.isValid) {
      setError(`Password requirements not met: ${validation.missingRequirements.join(', ')}`);
      setShowPasswordRules(true);
      return;
    }

    setLoading(true);

    try {
      await confirmPasswordReset(auth, oobCode, password);
      setSuccess(true);

      setTimeout(() => {
        navigate('/signin', { replace: true });
      }, 3000);
    } catch (err) {
      console.error('Password reset error:', err);

      let errorMessage = 'Failed to reset password. Please try again.';

      if (err.code === 'auth/expired-action-code') {
        errorMessage = 'This password reset link has expired. Please request a new one.';
      } else if (err.code === 'auth/invalid-action-code') {
        errorMessage = 'This password reset link is invalid. Please request a new one.';
      } else if (err.code === 'auth/weak-password') {
        errorMessage = 'Password is too weak. Please choose a stronger password.';
        setShowPasswordRules(true);
      }

      setError(errorMessage);
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <AuthShell
        title="Checking your reset link"
        description="Nimbus is verifying the recovery request before showing the password form."
      >
        <div className="py-12 text-center">
          <div className="mx-auto mb-4 h-12 w-12 rounded-full border-b-2 border-primary animate-spin" />
          <p className="text-sm text-gray-400">Verifying reset link...</p>
        </div>
      </AuthShell>
    );
  }

  if (success) {
    return (
      <AuthShell
        title="Password reset successful"
        description="Your Nimbus password has been updated and your workspace is almost ready."
      >
        <div className="text-center">
          <div className="mb-6">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border-2 border-green-600 bg-green-900/30">
              <svg className="h-10 w-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          <p className="mb-6 text-base text-gray-400">
            Your password has been successfully updated. You can now sign in with your new password.
          </p>

          <div className="mb-6 rounded-lg border border-green-800 bg-green-900/30 p-3 text-sm text-green-200">
            Redirecting to sign in page in 3 seconds...
          </div>

          <Link
            to="/signin"
            className="inline-flex items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-black transition-all duration-200 hover:bg-yellow-400"
          >
            Sign In Now
          </Link>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Reset your Nimbus password"
      description={
        validCode
          ? `Choose a strong password for ${email}.`
          : 'Choose a strong password for your account.'
      }
      heroTitle="Recovery that still feels polished."
      heroCopy="Nimbus keeps the same visual language and auth flow across sign-in, email actions, and the main workspace."
    >
      {error ? (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {!validCode ? (
        <div className="mb-6">
          <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 p-4 text-sm text-red-200">
            <p className="mb-2 font-semibold">Password reset link is invalid or expired.</p>
            <p>Please request a new password reset link.</p>
          </div>
          <Link
            to="/forgot-password"
            className="flex h-12 w-full items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-black transition-all duration-200 hover:bg-yellow-400"
          >
            Request New Link
          </Link>
        </div>
      ) : null}

      {validCode ? (
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="password" className="mb-1.5 block text-sm font-semibold text-gray-300">
              New password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError('');
              }}
              onFocus={() => setShowPasswordRules(true)}
              className="block h-12 w-full rounded-xl border-0 bg-gray-900/50 px-4 py-3.5 text-sm text-white ring-1 ring-inset ring-gray-800 backdrop-blur-sm transition-all duration-200 placeholder:text-gray-500 focus:bg-gray-900/70 focus:ring-2 focus:ring-primary"
              placeholder="  Enter new password"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-semibold text-gray-300">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(event) => {
                setConfirmPassword(event.target.value);
                setError('');
              }}
              className="block h-12 w-full rounded-xl border-0 bg-gray-900/50 px-4 py-3.5 text-sm text-white ring-1 ring-inset ring-gray-800 backdrop-blur-sm transition-all duration-200 placeholder:text-gray-500 focus:bg-gray-900/70 focus:ring-2 focus:ring-primary"
              placeholder="  Confirm new password"
            />
          </div>

          <div className="relative">
            <button
              type="button"
              onClick={() => setShowPasswordRules((current) => !current)}
              className="flex w-full cursor-pointer items-center justify-between rounded-xl border border-gray-800 bg-gray-900/50 px-4 py-3 text-left transition-all duration-200 hover:border-primary/30 hover:bg-gray-900/70 focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <div className="flex items-center gap-2.5">
                <svg className="h-4 w-4 flex-shrink-0 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium text-gray-300">Password requirements</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">{showPasswordRules ? 'Hide' : 'Show'}</span>
                <svg
                  className={`h-4 w-4 flex-shrink-0 text-gray-400 transition-transform duration-200 ${
                    showPasswordRules ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {showPasswordRules ? (
              <div className="absolute z-10 mt-2 w-full rounded-xl border border-gray-800 bg-gray-900 p-4 shadow-2xl">
                <p className="mb-3 text-sm font-medium text-gray-300">Your password must include:</p>
                <ul className="space-y-2">
                  {[
                    ['Minimum 8 characters in length', passwordValidation.minLength],
                    ['At least one uppercase letter (A-Z)', passwordValidation.uppercase],
                    ['At least one lowercase letter (a-z)', passwordValidation.lowercase],
                    ['At least one number (0-9)', passwordValidation.number],
                    ['At least one special character (!@#$%^&*)', passwordValidation.special],
                  ].map(([label, passed]) => (
                    <li
                      key={label}
                      className={`flex items-center gap-2.5 text-xs transition-colors ${
                        passed ? 'text-green-400' : 'text-gray-400'
                      }`}
                    >
                      <svg
                        className={`h-4 w-4 flex-shrink-0 ${passed ? 'text-green-500' : 'text-gray-600'}`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <span>{label}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group flex h-12 w-full items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-black transition-all duration-200 hover:bg-yellow-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? 'Resetting Password...' : 'Reset Password'}
              {!loading ? (
                <svg
                  className="ml-3 h-5 w-5 transition-transform group-hover:translate-x-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              ) : null}
            </button>
          </div>
        </form>
      ) : null}

      <p className="mt-8 text-center text-sm text-gray-400">
        Remember your password?{' '}
        <Link
          to="/signin"
          className="font-semibold text-primary underline-offset-4 transition-colors hover:text-yellow-400 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}
