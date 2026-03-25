import {
  EmailAuthProvider,
  GithubAuthProvider,
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  fetchSignInMethodsForEmail,
  getRedirectResult,
  linkWithCredential,
  onAuthStateChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
  validatePassword,
} from 'firebase/auth';
import { auth } from './config.js';

export const AUTH_ERROR_CODES = {
  ACCOUNT_EXISTS: 'auth/account-exists-with-different-credential',
  EMAIL_IN_USE: 'auth/email-already-in-use',
  INVALID_EMAIL: 'auth/invalid-email',
  WEAK_PASSWORD: 'auth/weak-password',
  WRONG_PASSWORD: 'auth/wrong-password',
  USER_NOT_FOUND: 'auth/user-not-found',
  TOO_MANY_REQUESTS: 'auth/too-many-requests',
  POPUP_BLOCKED: 'auth/popup-blocked-by-browser',
  POPUP_CLOSED: 'auth/popup-closed-by-user',
  INVALID_CREDENTIAL: 'auth/invalid-credential',
  CREDENTIAL_ALREADY_IN_USE: 'auth/credential-already-in-use',
};

export const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  requireLowercase: true,
  requireUppercase: true,
  requireNumeric: true,
  requireNonAlphanumeric: true,
};

const PENDING_CREDENTIAL_KEY = 'firebase_pending_credential';
const PENDING_EMAIL_KEY = 'firebase_pending_email';

export async function validatePasswordStrength(password) {
  try {
    if (!password || password.length < PASSWORD_REQUIREMENTS.minLength) {
      return {
        isValid: false,
        missingRequirements: [`minimum ${PASSWORD_REQUIREMENTS.minLength} characters`],
      };
    }

    const status = await validatePassword(auth, password);

    if (!status.isValid) {
      const missingRequirements = [];

      if (status.containsLowercaseLetter !== true) {
        missingRequirements.push('at least one lowercase letter');
      }
      if (status.containsUppercaseLetter !== true) {
        missingRequirements.push('at least one uppercase letter');
      }
      if (status.containsNumericCharacter !== true) {
        missingRequirements.push('at least one number');
      }
      if (status.containsNonAlphanumericCharacter !== true) {
        missingRequirements.push('at least one special character');
      }
      if (status.meetsMinPasswordLength !== true) {
        missingRequirements.push(`minimum ${PASSWORD_REQUIREMENTS.minLength} characters`);
      }

      return {
        isValid: false,
        missingRequirements,
      };
    }

    return { isValid: true, missingRequirements: [] };
  } catch (error) {
    console.error('Password validation error:', error);

    const missingRequirements = [];

    if (!password || password.length < PASSWORD_REQUIREMENTS.minLength) {
      missingRequirements.push(`minimum ${PASSWORD_REQUIREMENTS.minLength} characters`);
    }
    if (!/[a-z]/.test(password)) {
      missingRequirements.push('at least one lowercase letter');
    }
    if (!/[A-Z]/.test(password)) {
      missingRequirements.push('at least one uppercase letter');
    }
    if (!/[0-9]/.test(password)) {
      missingRequirements.push('at least one number');
    }
    if (!/[^a-zA-Z0-9]/.test(password)) {
      missingRequirements.push('at least one special character');
    }

    return {
      isValid: missingRequirements.length === 0,
      missingRequirements:
        missingRequirements.length > 0
          ? missingRequirements
          : ['Password validation failed'],
    };
  }
}

export async function signUpEmail(email, password, displayName = null) {
  try {
    const validation = await validatePasswordStrength(password);

    if (!validation.isValid) {
      return {
        success: false,
        error: `Password does not meet requirements: ${validation.missingRequirements.join(', ')}`,
      };
    }

    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    if (displayName) {
      await updateProfile(user, { displayName });
    }

    try {
      await sendEmailVerification(user);
    } catch (verificationError) {
      console.warn('Failed to send verification email:', verificationError.message);
    }

    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        emailVerified: user.emailVerified,
      },
    };
  } catch (error) {
    console.error('Email signup error:', error);

    let errorMessage = 'Failed to create account. Please try again.';

    switch (error.code) {
      case AUTH_ERROR_CODES.EMAIL_IN_USE:
        errorMessage = 'This email address is already in use. Please sign in or use a different email.';
        break;
      case AUTH_ERROR_CODES.INVALID_EMAIL:
        errorMessage = 'Invalid email address format.';
        break;
      case AUTH_ERROR_CODES.WEAK_PASSWORD:
        errorMessage = 'Password is too weak. Please choose a stronger password.';
        break;
      case AUTH_ERROR_CODES.TOO_MANY_REQUESTS:
        errorMessage = 'Too many failed attempts. Please try again later.';
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

export async function signInEmail(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        emailVerified: user.emailVerified,
        photoURL: user.photoURL,
      },
    };
  } catch (error) {
    console.error('Email sign-in error:', error);

    let errorMessage = 'Failed to sign in. Please check your credentials.';

    switch (error.code) {
      case AUTH_ERROR_CODES.INVALID_EMAIL:
        errorMessage = 'Invalid email address format.';
        break;
      case AUTH_ERROR_CODES.USER_NOT_FOUND:
      case AUTH_ERROR_CODES.WRONG_PASSWORD:
        errorMessage = 'Invalid email or password.';
        break;
      case AUTH_ERROR_CODES.TOO_MANY_REQUESTS:
        errorMessage = 'Too many failed attempts. Please try again later or reset your password.';
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

export async function resetPassword(email) {
  try {
    await sendPasswordResetEmail(auth, email);
    return { success: true };
  } catch (error) {
    console.error('Password reset error:', error);

    let errorMessage = 'Failed to send password reset email.';

    switch (error.code) {
      case AUTH_ERROR_CODES.INVALID_EMAIL:
        errorMessage = 'Invalid email address format.';
        break;
      case AUTH_ERROR_CODES.USER_NOT_FOUND:
        errorMessage = 'If this email is registered, you will receive a password reset link.';
        break;
      default:
        errorMessage = error.message || errorMessage;
    }

    return {
      success: error.code === AUTH_ERROR_CODES.USER_NOT_FOUND,
      error: errorMessage,
      code: error.code,
    };
  }
}

export async function signInWithGooglePopup(additionalScopes = []) {
  try {
    const provider = new GoogleAuthProvider();

    provider.setCustomParameters({ prompt: 'select_account' });
    additionalScopes.forEach((scope) => provider.addScope(scope));

    const result = await signInWithPopup(auth, provider);
    const credential = GoogleAuthProvider.credentialFromResult(result);

    return {
      success: true,
      user: {
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        emailVerified: result.user.emailVerified,
      },
      token: credential?.accessToken,
    };
  } catch (error) {
    console.error('Google popup sign-in error:', error);

    if (error.code === AUTH_ERROR_CODES.ACCOUNT_EXISTS) {
      return handleAccountExistsError(error, 'Google');
    }

    let errorMessage = 'Failed to sign in with Google.';

    switch (error.code) {
      case AUTH_ERROR_CODES.POPUP_BLOCKED:
        errorMessage = 'Popup was blocked by your browser. Please allow popups and try again.';
        break;
      case AUTH_ERROR_CODES.POPUP_CLOSED:
        errorMessage = 'Sign-in was cancelled.';
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

export async function signInWithGitHubPopup(additionalScopes = []) {
  try {
    const provider = new GithubAuthProvider();

    additionalScopes.forEach((scope) => provider.addScope(scope));

    const result = await signInWithPopup(auth, provider);
    const credential = GithubAuthProvider.credentialFromResult(result);

    return {
      success: true,
      user: {
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        emailVerified: result.user.emailVerified,
      },
      token: credential?.accessToken,
    };
  } catch (error) {
    console.error('GitHub popup sign-in error:', error);

    if (error.code === AUTH_ERROR_CODES.ACCOUNT_EXISTS) {
      return handleAccountExistsError(error, 'GitHub');
    }

    let errorMessage = 'Failed to sign in with GitHub.';

    switch (error.code) {
      case AUTH_ERROR_CODES.POPUP_BLOCKED:
        errorMessage = 'Popup was blocked by your browser. Please allow popups and try again.';
        break;
      case AUTH_ERROR_CODES.POPUP_CLOSED:
        errorMessage = 'Sign-in was cancelled.';
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

export async function handleRedirectResult() {
  try {
    const result = await getRedirectResult(auth);

    if (!result) {
      return { success: false, noRedirect: true };
    }

    let credential = null;
    let provider = 'unknown';

    if (result.providerId?.includes('google')) {
      credential = GoogleAuthProvider.credentialFromResult(result);
      provider = 'google';
    } else if (result.providerId?.includes('github')) {
      credential = GithubAuthProvider.credentialFromResult(result);
      provider = 'github';
    }

    clearPendingCredential();

    return {
      success: true,
      user: {
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        emailVerified: result.user.emailVerified,
      },
      token: credential?.accessToken,
      provider,
    };
  } catch (error) {
    console.error('Redirect result error:', error);

    if (error.code === AUTH_ERROR_CODES.ACCOUNT_EXISTS) {
      const email = error.customData?.email;
      const credential = error.credential;

      if (email && credential) {
        savePendingCredential(credential, email);

        try {
          const methods = await fetchSignInMethodsForEmail(auth, email);

          return {
            success: false,
            error: `An account with this email already exists. Please sign in with ${methods[0] || 'your existing method'} first.`,
            code: error.code,
            needsLinking: true,
            existingMethods: methods,
            pendingEmail: email,
          };
        } catch (fetchError) {
          console.error('Error fetching sign-in methods:', fetchError);
        }
      }
    }

    return {
      success: false,
      error: error.message || 'Failed to complete sign-in.',
      code: error.code,
    };
  }
}

async function handleAccountExistsError(error, attemptedProvider) {
  try {
    const email = error.customData?.email;
    const pendingCredential = error.credential;

    if (!email || !pendingCredential) {
      throw new Error('Missing email or credential in error object');
    }

    savePendingCredential(pendingCredential, email);

    const methods = await fetchSignInMethodsForEmail(auth, email);
    const methodNames = methods.map((method) => {
      if (method.includes('google')) return 'Google';
      if (method.includes('github')) return 'GitHub';
      if (method.includes('password')) return 'Email/Password';
      return method;
    });

    return {
      success: false,
      needsLinking: true,
      existingMethods: methodNames,
      pendingEmail: email,
      error: `An account already exists with this email address. Please sign in with ${methodNames[0]} first, then Nimbus can link your ${attemptedProvider} account.`,
      code: AUTH_ERROR_CODES.ACCOUNT_EXISTS,
    };
  } catch (fetchError) {
    console.error('Error handling account exists:', fetchError);
    return {
      success: false,
      needsLinking: false,
      error: 'An account with this email already exists. Please try signing in with a different method.',
      code: AUTH_ERROR_CODES.ACCOUNT_EXISTS,
    };
  }
}

export async function linkPendingCredential() {
  try {
    const currentUser = auth.currentUser;

    if (!currentUser) {
      return {
        success: false,
        error: 'No user is currently signed in. Please sign in first.',
      };
    }

    const pendingCred = retrievePendingCredential();

    if (!pendingCred) {
      return {
        success: false,
        error: 'No pending credential found. The link may have expired.',
      };
    }

    if (pendingCred.email && pendingCred.email !== currentUser.email) {
      clearPendingCredential();
      return {
        success: false,
        error: 'This credential belongs to a different account. Please try signing in again.',
      };
    }

    const result = await linkWithCredential(currentUser, pendingCred.credential);
    clearPendingCredential();

    return {
      success: true,
      user: {
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        emailVerified: result.user.emailVerified,
      },
    };
  } catch (error) {
    console.error('Credential linking error:', error);

    let errorMessage = 'Failed to link accounts.';

    switch (error.code) {
      case AUTH_ERROR_CODES.CREDENTIAL_ALREADY_IN_USE:
        errorMessage = 'This credential is already associated with a different account.';
        clearPendingCredential();
        break;
      case AUTH_ERROR_CODES.INVALID_CREDENTIAL:
        errorMessage = 'The credential has expired. Please try signing in again.';
        clearPendingCredential();
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

function savePendingCredential(credential, email) {
  try {
    sessionStorage.setItem(
      PENDING_CREDENTIAL_KEY,
      JSON.stringify({
        credential: {
          providerId: credential.providerId,
          signInMethod: credential.signInMethod,
          accessToken: credential.accessToken,
          idToken: credential.idToken,
          secret: credential.secret,
        },
        timestamp: Date.now(),
      }),
    );
    sessionStorage.setItem(PENDING_EMAIL_KEY, email);
  } catch (error) {
    console.error('Failed to save pending credential:', error);
  }
}

function retrievePendingCredential() {
  try {
    const credentialData = sessionStorage.getItem(PENDING_CREDENTIAL_KEY);

    if (!credentialData) return null;

    const parsed = JSON.parse(credentialData);
    const expirationTime = 15 * 60 * 1000;

    if (Date.now() - parsed.timestamp > expirationTime) {
      clearPendingCredential();
      return null;
    }

    const credData = parsed.credential;
    let credential = null;

    if (credData.providerId === 'google.com') {
      credential = GoogleAuthProvider.credential(credData.idToken, credData.accessToken);
    } else if (credData.providerId === 'github.com') {
      credential = GithubAuthProvider.credential(credData.accessToken);
    }

    return credential
      ? { credential, email: sessionStorage.getItem(PENDING_EMAIL_KEY) }
      : null;
  } catch (error) {
    console.error('Failed to retrieve pending credential:', error);
    clearPendingCredential();
    return null;
  }
}

function clearPendingCredential() {
  try {
    sessionStorage.removeItem(PENDING_CREDENTIAL_KEY);
    sessionStorage.removeItem(PENDING_EMAIL_KEY);
  } catch (error) {
    console.error('Failed to clear pending credential:', error);
  }
}

export function checkPendingCredential() {
  const email = sessionStorage.getItem(PENDING_EMAIL_KEY);
  const credentialData = sessionStorage.getItem(PENDING_CREDENTIAL_KEY);

  return {
    hasPending: !!(email && credentialData),
    email: email || null,
  };
}

export function setupAuthObserver(callback) {
  return onAuthStateChanged(auth, (user) => {
    if (user) {
      callback({
        signedIn: true,
        user: {
          uid: user.uid,
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
          emailVerified: user.emailVerified,
          isAnonymous: user.isAnonymous,
          metadata: {
            creationTime: user.metadata.creationTime,
            lastSignInTime: user.metadata.lastSignInTime,
          },
          providerData: user.providerData,
        },
      });
      return;
    }

    callback({
      signedIn: false,
      user: null,
    });
  });
}

export function getCurrentUser() {
  const user = auth.currentUser;

  if (!user) return null;

  return {
    uid: user.uid,
    email: user.email,
    displayName: user.displayName,
    photoURL: user.photoURL,
    emailVerified: user.emailVerified,
    isAnonymous: user.isAnonymous,
    metadata: {
      creationTime: user.metadata.creationTime,
      lastSignInTime: user.metadata.lastSignInTime,
    },
    providerData: user.providerData,
  };
}

export async function signOutUser() {
  try {
    await signOut(auth);
    clearPendingCredential();

    try {
      const keysToRemove = [];

      for (let i = 0; i < sessionStorage.length; i += 1) {
        const key = sessionStorage.key(i);

        if (key && (key.startsWith('justVerified_') || key.startsWith('firebase_pending_'))) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach((key) => sessionStorage.removeItem(key));
    } catch (storageError) {
      console.warn('Failed to clear some sessionStorage keys:', storageError);
    }

    return { success: true };
  } catch (error) {
    console.error('Sign-out error:', error);
    return {
      success: false,
      error: error.message || 'Failed to sign out.',
    };
  }
}

export function getEmailCredential(email, password) {
  return EmailAuthProvider.credential(email, password);
}

export { auth };
