import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  checkPendingCredential,
  linkPendingCredential,
  signInEmail,
  signInWithGitHubPopup,
  signInWithGooglePopup,
} from '../firebase/authService';

const SIGN_IN_WORDS = ['Secure.', 'Design.', 'Deploy.'];

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
    <div className="flex min-h-screen font-display bg-transparent text-[#49697f]">
      <div className="flex w-full items-center justify-center bg-[linear-gradient(180deg,rgba(255,255,255,0.74),rgba(241,250,255,0.96))] p-7 md:p-9 lg:w-1/2 lg:p-14">
        <div className="w-full max-w-md lg:max-w-lg">
          <div className="mb-6">
            <h2 className="min-h-[3.5rem] text-2xl font-bold leading-tight text-[#14324a] sm:min-h-[4rem] sm:text-3xl lg:text-4xl">
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
            <div className="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}
          {success ? (
            <div className="mb-4 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-700">
              {success}
            </div>
          ) : null}

          <form className="space-y-2" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-semibold text-[#3d5d74]">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="block h-12 w-full rounded-xl border-0 bg-white/82 px-4 py-3.5 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] placeholder:text-[#6f8ea3] backdrop-blur-sm transition-all duration-200 focus:bg-white focus:ring-2 focus:ring-primary"
                placeholder="  your@email.com"
                aria-label="email"
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-semibold text-[#3d5d74]">
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
                  className="block h-12 w-full rounded-xl border-0 bg-white/82 px-4 py-3.5 pr-12 text-sm text-[#14324a] ring-1 ring-inset ring-[#b9d8ea] placeholder:text-[#6f8ea3] backdrop-blur-sm transition-all duration-200 focus:bg-white focus:ring-2 focus:ring-primary"
                  placeholder="  Enter password"
                  aria-label="password"
                />
                <button
                  type="button"
                  onClick={() => setPasswordVisible((current) => !current)}
                  className="absolute inset-y-0 right-0 flex items-center pr-4 text-[#7a97ab] transition-colors hover:text-[#2a84c9]"
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
                className="text-sm font-semibold text-primary transition-colors hover:text-[#0d75be]"
              >
                Forgot password?
              </Link>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group flex h-12 w-full items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-[#08304d] transition-all duration-200 hover:bg-[#7dcaff] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50"
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
            <div className="flex-grow border-t border-[#c5deee]"></div>
            <span className="mx-5 text-xs font-medium uppercase tracking-wider text-[#6f8ea3]">
              Or continue with
            </span>
            <div className="flex-grow border-t border-[#c5deee]"></div>
          </div>

          <div className="space-y-3">
            <button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="group flex h-12 w-full items-center justify-center gap-[18px] rounded-xl bg-white/80 px-[28px] py-[14px] text-sm font-semibold text-[#35556d] ring-1 ring-inset ring-[#c3dced] backdrop-blur-sm transition-all duration-200 hover:bg-white hover:ring-[#9ac9e7] disabled:cursor-not-allowed disabled:opacity-50"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="h-5 w-5"
              />
              <span className="transition-colors group-hover:text-[#16364d]">Continue with Google</span>
            </button>

            <button
              onClick={handleGitHubSignIn}
              disabled={loading}
              className="group flex h-12 w-full items-center justify-center gap-[18px] rounded-xl bg-white/80 px-[28px] py-[14px] text-sm font-semibold text-[#35556d] ring-1 ring-inset ring-[#c3dced] backdrop-blur-sm transition-all duration-200 hover:bg-white hover:ring-[#9ac9e7] disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              <span className="transition-colors group-hover:text-[#16364d]">Continue with GitHub</span>
            </button>
          </div>

          <p className="mt-6 text-center text-sm text-[#6a8aa1]">
            New to Nimbus?{' '}
            <Link
              to="/signup"
              className="font-semibold text-primary transition-colors hover:text-[#0d75be] underline-offset-4 hover:underline"
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
          <source src="/nimbus.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(244,251,255,0.18),rgba(20,50,74,0.24),rgba(244,251,255,0.12))]"></div>
        <div className="absolute inset-x-0 bottom-0 h-64 bg-[linear-gradient(180deg,transparent,rgba(7,41,70,0.55))]"></div>
        <div className="absolute top-8 right-8 h-24 w-24 rounded-full bg-sky-200/30 blur-2xl"></div>
        <div className="absolute bottom-12 left-12 h-36 w-36 rounded-full bg-white/20 blur-3xl"></div>
      </div>
    </div>
  );
} 
