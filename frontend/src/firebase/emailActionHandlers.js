import { applyActionCode, checkActionCode, verifyPasswordResetCode } from 'firebase/auth';
import { auth } from './config.js';

export const EMAIL_ACTION_MODES = {
  RESET_PASSWORD: 'resetPassword',
  VERIFY_EMAIL: 'verifyEmail',
};

export function parseEmailActionParams(searchParams) {
  return {
    mode: searchParams.get('mode'),
    oobCode: searchParams.get('oobCode'),
    apiKey: searchParams.get('apiKey'),
    continueUrl: searchParams.get('continueUrl'),
    lang: searchParams.get('lang'),
  };
}

export async function handleVerifyEmail(oobCode) {
  try {
    const info = await checkActionCode(auth, oobCode);
    const email = info.data.email;

    await applyActionCode(auth, oobCode);

    return {
      success: true,
      email,
    };
  } catch (error) {
    console.error('Email verification error:', error);

    let errorMessage = 'Failed to verify email. Please try again.';

    switch (error.code) {
      case 'auth/expired-action-code':
        errorMessage = 'This verification link has expired. Please request a new one.';
        break;
      case 'auth/invalid-action-code':
        errorMessage = 'This verification link is invalid. It may have already been used.';
        break;
      case 'auth/user-disabled':
        errorMessage = 'This account has been disabled.';
        break;
      case 'auth/user-not-found':
        errorMessage = 'No account found for this email.';
        break;
      default:
        errorMessage = error.message || errorMessage;
    }

    return {
      success: false,
      error: errorMessage,
      code: error.code,
    };
  }
}

export async function verifyPasswordResetCodeHandler(oobCode) {
  try {
    const email = await verifyPasswordResetCode(auth, oobCode);

    return {
      success: true,
      email,
    };
  } catch (error) {
    console.error('Password reset code verification error:', error);

    let errorMessage = 'This password reset link is invalid or has expired.';

    switch (error.code) {
      case 'auth/expired-action-code':
        errorMessage = 'This password reset link has expired. Please request a new one.';
        break;
      case 'auth/invalid-action-code':
        errorMessage = 'This password reset link is invalid. Please request a new one.';
        break;
      case 'auth/user-disabled':
        errorMessage = 'This account has been disabled.';
        break;
      case 'auth/user-not-found':
        errorMessage = 'No account found for this email.';
        break;
      default:
        errorMessage = error.message || errorMessage;
    }

    return {
      success: false,
      error: errorMessage,
      code: error.code,
    };
  }
}

export function getActionDisplayName(mode) {
  switch (mode) {
    case EMAIL_ACTION_MODES.RESET_PASSWORD:
      return 'Password Reset';
    case EMAIL_ACTION_MODES.VERIFY_EMAIL:
      return 'Email Verification';
    default:
      return 'Email Action';
  }
}
