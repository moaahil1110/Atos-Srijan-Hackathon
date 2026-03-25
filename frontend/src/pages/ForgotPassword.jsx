import { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthShell from '../components/AuthShell';
import { resetPassword } from '../firebase/authService';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      const result = await resetPassword(email);

      if (result.success) {
        setSuccess('Password reset link sent. Check your email inbox and spam folder for instructions.');
        setEmail('');
      } else {
        setError(result.error || 'Failed to send reset email. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Password reset error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      title="Reset your Nimbus password"
      description="No worries. We will send reset instructions so you can get back into the workspace."
      heroTitle="Keep access smooth, even when passwords are not."
      heroCopy="Nimbus keeps sign-in, reset, verification, and OAuth under one consistent experience so access never feels bolted on."
    >
      {error ? (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      {success ? (
        <div className="mb-4 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-700">
          {success}
        </div>
      ) : null}

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-semibold text-[#3d5d74]">
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
              setError('');
            }}
            className="block h-12 w-full rounded-xl border-0 bg-white/82 px-4 py-3.5 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] backdrop-blur-sm transition-all duration-200 placeholder:text-[#6f8ea3] focus:bg-white focus:ring-2 focus:ring-primary"
            placeholder="  you@example.com"
            aria-label="email"
          />
        </div>

        <div>
          <button
            type="submit"
            disabled={loading}
            className="group flex h-12 w-full items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-[#08304d] transition-all duration-200 hover:bg-[#7dcaff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
            {!loading ? (
              <svg
                className="ml-3 h-5 w-5 transition-transform group-hover:translate-x-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            ) : null}
          </button>
        </div>
      </form>

      <p className="mt-8 text-center text-sm text-[#6a8aa1]">
        Remembered your password?{' '}
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
