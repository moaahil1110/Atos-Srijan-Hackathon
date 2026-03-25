import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthShell from '../components/AuthShell';
import {
  signInWithGitHubPopup,
  signInWithGooglePopup,
  signUpEmail,
} from '../firebase/authService';

export default function SignUp() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.fullName.trim()) {
      setError('Please enter your full name');
      return;
    }

    if (!formData.email.trim()) {
      setError('Please enter your email address');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    const hasUpperCase = /[A-Z]/.test(formData.password);
    const hasLowerCase = /[a-z]/.test(formData.password);
    const hasNumber = /[0-9]/.test(formData.password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(formData.password);

    if (!hasUpperCase || !hasLowerCase || !hasNumber || !hasSpecialChar) {
      setError(
        'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character',
      );
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const result = await signUpEmail(formData.email, formData.password, formData.fullName);

      if (result.success) {
        setSuccess('Account created successfully. Opening your Nimbus workspace...');
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 900);
      } else {
        setError(result.error || 'Failed to create account. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Sign up error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await signInWithGooglePopup();

      if (result.success) {
        setSuccess('Signed up with Google. Opening your Nimbus workspace...');
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 600);
      } else if (result.needsLinking) {
        setError(result.error || 'Account already exists with this email. Please sign in with your existing method.');
      } else {
        setError(result.error || 'Failed to sign up with Google. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred with Google sign-up.');
      console.error('Google sign-up error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubSignUp = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await signInWithGitHubPopup();

      if (result.success) {
        setSuccess('Signed up with GitHub. Opening your Nimbus workspace...');
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 600);
      } else if (result.needsLinking) {
        setError(result.error || 'Account already exists with this email. Please sign in with your existing method.');
      } else {
        setError(result.error || 'Failed to sign up with GitHub. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred with GitHub sign-up.');
      console.error('GitHub sign-up error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      title="Create your Nimbus account"
      description="Start with a polished OAuth-ready onboarding flow, then land directly inside the demo workspace."
      heroTitle="From first sign-in to first architecture pass."
      heroCopy="Nimbus keeps onboarding simple so teams can get straight to refining infrastructure intent, security guardrails, and deployment-ready output."
    >
      {error ? (
        <div className="mb-3 rounded-lg border border-red-300 bg-red-50 p-2.5 text-xs text-red-700">
          {error}
        </div>
      ) : null}
      {success ? (
        <div className="mb-3 rounded-lg border border-emerald-300 bg-emerald-50 p-2.5 text-xs text-emerald-700">
          {success}
        </div>
      ) : null}

      <form className="space-y-3" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fullName" className="mb-1 block text-xs font-semibold text-[#3d5d74]">
            Full name
          </label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            required
            value={formData.fullName}
            onChange={handleInputChange}
            className="block h-10 w-full rounded-lg border-0 bg-white/82 px-3.5 py-2.5 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] backdrop-blur-sm transition-all duration-200 placeholder:text-[#6f8ea3] focus:bg-white focus:ring-2 focus:ring-primary"
            placeholder="  Your name"
            aria-label="full name"
          />
        </div>

        <div>
          <label htmlFor="email" className="mb-1 block text-xs font-semibold text-[#3d5d74]">
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={formData.email}
            onChange={handleInputChange}
            className="block h-10 w-full rounded-lg border-0 bg-white/82 px-3.5 py-2.5 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] backdrop-blur-sm transition-all duration-200 placeholder:text-[#6f8ea3] focus:bg-white focus:ring-2 focus:ring-primary"
            placeholder="  you@example.com"
            aria-label="email"
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1 block text-xs font-semibold text-[#3d5d74]">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={passwordVisible ? 'text' : 'password'}
              required
              value={formData.password}
              onChange={handleInputChange}
              className="block h-10 w-full rounded-lg border-0 bg-white/82 px-3.5 py-2.5 pr-10 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] backdrop-blur-sm transition-all duration-200 placeholder:text-[#6f8ea3] focus:bg-white focus:ring-2 focus:ring-primary"
              placeholder="  Min 8 chars"
              aria-label="password"
            />
            <button
              type="button"
              onClick={() => setPasswordVisible((current) => !current)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#7a97ab] transition-colors hover:text-[#2a84c9]"
              aria-label={passwordVisible ? 'Hide password' : 'Show password'}
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {passwordVisible ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="mb-1 block text-xs font-semibold text-[#3d5d74]">
            Confirm password
          </label>
          <div className="relative">
            <input
              id="confirmPassword"
              name="confirmPassword"
              type={confirmPasswordVisible ? 'text' : 'password'}
              required
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className="block h-10 w-full rounded-lg border-0 bg-white/82 px-3.5 py-2.5 pr-10 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] backdrop-blur-sm transition-all duration-200 placeholder:text-[#6f8ea3] focus:bg-white focus:ring-2 focus:ring-primary"
              placeholder="  Confirm password"
              aria-label="confirm password"
            />
            <button
              type="button"
              onClick={() => setConfirmPasswordVisible((current) => !current)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#7a97ab] transition-colors hover:text-[#2a84c9]"
              aria-label={confirmPasswordVisible ? 'Hide password' : 'Show password'}
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {confirmPasswordVisible ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        <div className="pt-1">
          <button
            type="submit"
            disabled={loading}
            className="group flex h-10 w-full items-center justify-center rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-[#08304d] transition-all duration-200 hover:bg-[#7dcaff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
            {!loading ? (
              <svg
                className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            ) : null}
          </button>
        </div>
      </form>

      <div className="my-4 flex items-center justify-center">
        <div className="flex-grow border-t border-[#c5deee]" />
        <span className="mx-4 text-[10px] font-medium uppercase tracking-wider text-[#6f8ea3]">
          Or continue with
        </span>
        <div className="flex-grow border-t border-[#c5deee]" />
      </div>

      <div className="space-y-2.5">
        <button
          onClick={handleGoogleSignUp}
          disabled={loading}
          className="group flex h-10 w-full items-center justify-center gap-3 rounded-lg bg-white/80 px-5 py-2.5 text-xs font-semibold text-[#35556d] ring-1 ring-inset ring-[#c3dced] backdrop-blur-sm transition-all duration-200 hover:bg-white hover:ring-[#9ac9e7] disabled:cursor-not-allowed disabled:opacity-50"
        >
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            alt="Google"
            className="h-4 w-4"
          />
          <span className="transition-colors group-hover:text-[#16364d]">Continue with Google</span>
        </button>

        <button
          onClick={handleGitHubSignUp}
          disabled={loading}
          className="group flex h-10 w-full items-center justify-center gap-3 rounded-lg bg-white/80 px-5 py-2.5 text-xs font-semibold text-[#35556d] ring-1 ring-inset ring-[#c3dced] backdrop-blur-sm transition-all duration-200 hover:bg-white hover:ring-[#9ac9e7] disabled:cursor-not-allowed disabled:opacity-50"
        >
          <img
            src="https://www.svgrepo.com/show/512317/github-142.svg"
            alt="GitHub"
            className="h-4 w-4 invert"
          />
          <span className="transition-colors group-hover:text-[#16364d]">Continue with GitHub</span>
        </button>
      </div>

      <p className="mt-5 text-center text-xs text-[#6a8aa1]">
        Already have an account?{' '}
        <Link
          to="/signin"
          className="font-semibold text-primary underline-offset-4 transition-colors hover:text-[#0d75be] hover:underline"
        >
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}
