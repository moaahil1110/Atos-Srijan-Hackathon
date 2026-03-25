import { useEffect, useRef, useState } from 'react';
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import AuthShell from '../components/AuthShell';
import {
  EMAIL_ACTION_MODES,
  getActionDisplayName,
  handleVerifyEmail,
  parseEmailActionParams,
} from '../firebase/emailActionHandlers';

export default function EmailActionHandler() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const hasHandledRef = useRef(false);
  const redirectTimeoutRef = useRef(null);
  const [state, setState] = useState({
    loading: true,
    mode: null,
    error: null,
    success: false,
    email: null,
    message: null,
  });

  useEffect(() => {
    if (state.success && state.mode === EMAIL_ACTION_MODES.VERIFY_EMAIL) {
      redirectTimeoutRef.current = setTimeout(() => {
        navigate('/?verified=true', { replace: true });
      }, 4000);
    }

    return () => {
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
    };
  }, [navigate, state.mode, state.success]);

  useEffect(() => {
    if (!hasHandledRef.current) {
      hasHandledRef.current = true;
      handleEmailAction();
    }
  });

  const handleEmailAction = async () => {
    try {
      const params = parseEmailActionParams(searchParams);

      if (!params.mode || !params.oobCode) {
        setState({
          loading: false,
          mode: params.mode,
          error: 'Invalid or missing parameters in the link.',
          success: false,
        });
        return;
      }

      if (params.mode === EMAIL_ACTION_MODES.RESET_PASSWORD) {
        setState({
          loading: false,
          mode: params.mode,
          shouldRedirectToReset: true,
        });
        return;
      }

      if (params.mode === EMAIL_ACTION_MODES.VERIFY_EMAIL) {
        await handleEmailVerificationAction(params);
        return;
      }

      setState({
        loading: false,
        mode: params.mode,
        error: 'This action type is not supported. Please contact support.',
        success: false,
      });
    } catch (error) {
      console.error('Email action handler error:', error);
      setState({
        loading: false,
        error: 'An unexpected error occurred. Please try again.',
        success: false,
      });
    }
  };

  const handleEmailVerificationAction = async (params) => {
    try {
      setState((current) => ({
        ...current,
        loading: true,
        mode: params.mode,
      }));

      const result = await handleVerifyEmail(params.oobCode);

      if (result.success) {
        setState({
          loading: false,
          mode: params.mode,
          success: true,
          email: result.email,
          message: 'Your email has been successfully verified.',
        });
        return;
      }

      if (result.code === 'auth/invalid-action-code' || result.code === 'auth/expired-action-code') {
        navigate('/', { replace: true });
        return;
      }

      setState({
        loading: false,
        mode: params.mode,
        success: false,
        error: result.error,
      });
    } catch (error) {
      console.error('Email verification action error:', error);
      setState({
        loading: false,
        mode: params.mode,
        success: false,
        error: 'An unexpected error occurred during email verification.',
      });
    }
  };

  if (state.mode === EMAIL_ACTION_MODES.RESET_PASSWORD && !state.loading) {
    return <Navigate to={`/reset-password?${searchParams.toString()}`} replace />;
  }

  if (state.loading) {
    return (
      <AuthShell
        title="Processing your Nimbus request"
        description={
          state.mode === EMAIL_ACTION_MODES.VERIFY_EMAIL
            ? 'Nimbus is verifying your email...'
            : 'Nimbus is processing your request...'
        }
      >
        <div className="py-12 text-center">
          <div className="mx-auto mb-4 h-12 w-12 rounded-full border-b-2 border-primary animate-spin" />
          <p className="text-sm text-[#6a8aa1]">
            {state.mode === EMAIL_ACTION_MODES.VERIFY_EMAIL
              ? 'Verifying your email...'
              : 'Processing your request...'}
          </p>
        </div>
      </AuthShell>
    );
  }

  if (state.success) {
    return (
      <AuthShell
        title="Email verified successfully"
        description="Your Nimbus account is verified and ready."
      >
        <div className="text-center">
          <div className="mb-6">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border-2 border-emerald-300 bg-emerald-50">
              <svg className="h-10 w-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          <p className="mb-6 text-base text-[#6a8aa1]">
            Your email address has been verified. You can now access all Nimbus features.
          </p>

          {state.email ? (
            <p className="mb-6 text-sm text-[#7b98ad]">
              Verified: <span className="text-primary">{state.email}</span>
            </p>
          ) : null}

          <div className="mb-6 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-700">
            Redirecting to your workspace in 4 seconds...
          </div>

          <button
            onClick={() => navigate('/', { replace: true })}
            className="inline-flex items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-[#08304d] transition-all duration-200 hover:bg-[#7dcaff]"
          >
            Go to Workspace Now
          </button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title={`${state.mode ? getActionDisplayName(state.mode) : 'Action'} failed`}
      description="Nimbus could not complete that email action."
    >
      <div className="text-center">
        <div className="mb-6">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border-2 border-red-300 bg-red-50">
            <svg className="h-10 w-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        </div>

          <div className="mb-6 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          <p className="mb-2 font-semibold">Error</p>
          <p>{state.error || 'An unexpected error occurred.'}</p>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => navigate('/forgot-password')}
            className="flex h-12 w-full items-center justify-center rounded-xl bg-primary px-[28px] py-[14px] text-base font-bold text-[#08304d] transition-all duration-200 hover:bg-[#7dcaff]"
          >
            Request Password Reset Link
          </button>

          <button
            onClick={() => navigate('/signin')}
            className="flex h-12 w-full items-center justify-center rounded-xl border border-[#c9e0ef] bg-white/80 px-[28px] py-[14px] text-base font-medium text-[#4f6f86] transition-all duration-200 hover:bg-white"
          >
            Back to Sign In
          </button>
        </div>
      </div>
    </AuthShell>
  );
}
