import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  checkPendingCredential,
  linkPendingCredential,
  signInEmail,
  signInWithGitHubPopup,
  signInWithGooglePopup,
} from '../firebase/authService';

const SIGN_IN_WORDS = ['Secure.', 'Design.', 'Deploy.', 'With', 'Nimbus.'];

export default function SignIn() {
  const navigate = useNavigate();
  const location = useLocation();
  const destination = location.state?.from?.pathname || '/';

  const [displayedWords, setDisplayedWords] = useState([]);
  const [phase, setPhase] = useState('typing');
  const [index, setIndex] = useState(0);
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    let timer;

    if (phase === 'typing' && index < SIGN_IN_WORDS.length) {
      timer = setTimeout(() => {
        setDisplayedWords((current) => [...current, SIGN_IN_WORDS[index]]);
        setIndex((current) => current + 1);
      }, 380);
    } else if (phase === 'typing' && index === SIGN_IN_WORDS.length) {
      timer = setTimeout(() => setPhase('deleting'), 1100);
    } else if (phase === 'deleting' && displayedWords.length > 0) {
      timer = setTimeout(() => {
        setDisplayedWords((current) => current.slice(0, -1));
      }, 220);
    } else if (phase === 'deleting' && displayedWords.length === 0) {
      timer = setTimeout(() => {
        setIndex(0);
        setPhase('typing');
      }, 400);
    }

    return () => clearTimeout(timer);
  }, [displayedWords, index, phase]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
    setError('');
  };

  const finalizeSignIn = async () => {
    const pending = checkPendingCredential();

    if (!pending.hasPending) {
      navigate(destination, { replace: true });
      return;
    }

    const linkResult = await linkPendingCredential();

    if (!linkResult.success) {
      setError(linkResult.error || 'Signed in, but Nimbus could not link your existing provider yet.');
      return;
    }

    navigate(destination, { replace: true });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.email.trim()) {
      setError('Please enter your email address');
      return;
    }

    if (!formData.password.trim()) {
      setError('Please enter your password');
      return;
    }

    setLoading(true);

    try {
      const result = await signInEmail(formData.email, formData.password);

      if (result.success) {
        setSuccess('Signed in successfully. Opening your Nimbus workspace...');
        await finalizeSignIn();
      } else {
        setError(result.error || 'Failed to sign in. Please check your credentials.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Sign in error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await signInWithGooglePopup();

      if (result.success) {
        setSuccess('Signed in with Google. Opening your Nimbus workspace...');
        navigate(destination, { replace: true });
      } else if (result.needsLinking) {
        setError(result.error || 'Account linking required. Please sign in with your existing method first.');
      } else {
        setError(result.error || 'Failed to sign in with Google. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred with Google sign-in.');
      console.error('Google sign-in error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubSignIn = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await signInWithGitHubPopup();

      if (result.success) {
        setSuccess('Signed in with GitHub. Opening your Nimbus workspace...');
        navigate(destination, { replace: true });
      } else if (result.needsLinking) {
        setError(result.error || 'Account linking required. Please sign in with your existing method first.');
      } else {
        setError(result.error || 'Failed to sign in with GitHub. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred with GitHub sign-in.');
      console.error('GitHub sign-in error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen font-display bg-[#0E0C09] text-gray-300">
      <div className="flex w-full items-center justify-center bg-[#0E0C09] p-7 md:p-9 lg:w-1/2 lg:p-14">
        <div className="w-full max-w-md lg:max-w-lg">
          <div className="mb-6">
            <h2 className="min-h-[3.5rem] text-2xl font-bold leading-tight text-white sm:min-h-[4rem] sm:text-3xl lg:text-4xl">
              <div className="inline-flex flex-wrap items-center gap-x-4">
                {SIGN_IN_WORDS.map((word, wordIndex) => {
                  const visible = wordIndex < displayedWords.length;

                  return (
                    <span
                      key={word}
                      className={
                        'inline-block align-middle transform transition-all duration-300 ' +
                        (visible
                          ? 'opacity-100 translate-y-0 scale-100'
                          : 'opacity-0 -translate-y-2 scale-95')
                      }
                      aria-hidden={!visible}
                    >
                      {wordIndex === 0 ? (
                        <span
                          className="inline-block h-4 w-4 rounded-full bg-primary mr-2 align-middle"
                          aria-hidden
                        />
                      ) : null}
                      {word}
                    </span>
                  );
                })}
              </div>
            </h2>
          </div>

          {error ? (
            <div className="mb-4 rounded-lg border border-red-800 bg-red-900/30 p-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}
          {success ? (
            <div className="mb-4 rounded-lg border border-green-800 bg-green-900/30 p-3 text-sm text-green-200">
              {success}
            </div>
          ) : null}

          <form className="space-y-2" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-300 mb-1.5">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="block w-full rounded-xl border-0 py-3.5 px-4 bg-gray-900/50 text-white ring-1 ring-inset ring-gray-800 placeholder:text-gray-500 focus:ring-2 focus:ring-primary focus:bg-gray-900/70 text-sm transition-all duration-200 h-12 backdrop-blur-sm"
                placeholder="  your@email.com"
                aria-label="email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-300 mb-1.5">
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
                  className="block w-full rounded-xl border-0 py-3.5 px-4 pr-12 bg-gray-900/50 text-white ring-1 ring-inset ring-gray-800 placeholder:text-gray-500 focus:ring-2 focus:ring-primary focus:bg-gray-900/70 text-sm transition-all duration-200 h-12 backdrop-blur-sm"
                  placeholder="  Enter password"
                  aria-label="password"
                />
                <button
                  type="button"
                  onClick={() => setPasswordVisible((current) => !current)}
                  className="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 hover:text-gray-200 transition-colors"
                  aria-label={passwordVisible ? 'Hide password' : 'Show password'}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
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
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    )}
                  </svg>
                </button>
              </div>
            </div>

            <div className="flex items-center justify-end">
              <Link
                to="/forgot-password"
                className="text-sm font-semibold text-primary hover:text-yellow-400 transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group flex w-full justify-center items-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-black hover:bg-yellow-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary transition-all duration-200 h-12 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Signing In...' : 'Sign In'}
                {!loading ? (
                  <svg
                    className="ml-3 w-5 h-5 group-hover:translate-x-1 transition-transform"
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

          <div className="my-6 flex items-center justify-center">
            <div className="flex-grow border-t border-gray-800"></div>
            <span className="mx-5 text-xs font-medium text-gray-500 uppercase tracking-wider">
              Or continue with
            </span>
            <div className="flex-grow border-t border-gray-800"></div>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="group flex w-full items-center justify-center gap-[18px] rounded-xl bg-gray-900/50 backdrop-blur-sm px-[28px] py-[14px] text-sm font-semibold text-gray-200 ring-1 ring-inset ring-gray-800 hover:bg-gray-900/70 hover:ring-gray-700 transition-all duration-200 h-12 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="h-5 w-5"
              />
              <span className="group-hover:text-white transition-colors">Continue with Google</span>
            </button>

            <button
              onClick={handleGitHubSignIn}
              disabled={loading}
              className="group flex w-full items-center justify-center gap-[18px] rounded-xl bg-gray-900/50 backdrop-blur-sm px-[28px] py-[14px] text-sm font-semibold text-gray-200 ring-1 ring-inset ring-gray-800 hover:bg-gray-900/70 hover:ring-gray-700 transition-all duration-200 h-12 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <img
                src="https://www.svgrepo.com/show/512317/github-142.svg"
                alt="GitHub"
                className="h-5 w-5 invert"
              />
              <span className="group-hover:text-white transition-colors">Continue with GitHub</span>
            </button>
          </div>

          <p className="mt-6 text-center text-sm text-gray-400">
            New to Nimbus?{' '}
            <Link
              to="/signup"
              className="font-semibold text-primary hover:text-yellow-400 transition-colors underline-offset-4 hover:underline"
            >
              Create an account
            </Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:block lg:w-1/2 relative overflow-hidden">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 h-full w-full object-cover"
        >
          <source src="/hero.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="absolute inset-0 bg-gradient-to-br from-[#0E0C09]/90 via-black/40 to-transparent"></div>
        <div className="absolute top-8 right-8 w-20 h-20 rounded-full bg-yellow-400/10 blur-2xl"></div>
        <div className="absolute bottom-12 left-12 w-32 h-32 rounded-full bg-primary/5 blur-3xl"></div>
      </div>
    </div>
  );
}
