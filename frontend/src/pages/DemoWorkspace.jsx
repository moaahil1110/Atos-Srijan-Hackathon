import { useEffect, useState } from 'react';
import { sendEmailVerification } from 'firebase/auth';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import IntakePanel from '../components/workspace/IntakePanel';
import ConfigPanel from '../components/workspace/ConfigPanel';
import { signOutUser } from '../firebase/authService';
import { auth } from '../firebase/config';

const API_BASE_URL = 'http://127.0.0.1:5000';

export default function DemoWorkspace() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [provider, setProvider] = useState('aws');
  const [session, setSession] = useState(null);
  const [selectedServices, setSelectedServices] = useState([]);
  const [allConfigs, setAllConfigs] = useState({});
  const [schemas, setSchemas] = useState({});
  const [loadingServices, setLoadingServices] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isConfiguring, setIsConfiguring] = useState(false);
  const [verificationBannerDismissed, setVerificationBannerDismissed] = useState(false);
  const [verifiedNoticeVisible, setVerifiedNoticeVisible] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [emailBannerMessage, setEmailBannerMessage] = useState('');

  const handleConfigUpdate = (service, fieldId, newValue, newReason) => {
    setAllConfigs((current) => ({
      ...current,
      [service]: {
        ...(current[service] || {}),
        [fieldId]: {
          value: newValue,
          reason: newReason,
        },
      },
    }));
  };

  useEffect(() => {
    if (searchParams.get('verified') !== 'true') {
      return;
    }
    setVerifiedNoticeVisible(true);
    if (auth.currentUser) {
      auth.currentUser.reload().catch(() => {});
    }
    setSearchParams({});
  }, [searchParams, setSearchParams]);

  const analyzeDescription = async (description, nextProvider) => {
    setIsAnalyzing(true);
    setStatusMessage('');
    setAllConfigs({});
    setSchemas({});
    try {
      const response = await fetch(`${API_BASE_URL}/intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, provider: nextProvider }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Intent generation failed.');
      }
      setProvider(nextProvider);
      setSession(data);
      setSelectedServices(data.suggestedServices || []);
    } catch (error) {
      setStatusMessage(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const configureSelectedServices = async (services) => {
    if (!session?.sessionId || services.length === 0) {
      return;
    }

    setIsConfiguring(true);
    setStatusMessage('');
    const nextConfigs = {};
    const nextSchemas = {};

    try {
      for (let index = 0; index < services.length; index += 1) {
        const service = services[index];
        setLoadingServices((current) => [...new Set([...current, service])]);
        setStatusMessage(`Configuring ${service}... (${index + 1} of ${services.length})`);

        const schemaResponse = await fetch(`${API_BASE_URL}/schema`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: session.sessionId,
            service,
            provider,
          }),
        });
        const schemaData = await schemaResponse.json();
        if (!schemaResponse.ok) {
          throw new Error(schemaData.detail || `Schema fetch failed for ${service}.`);
        }
        const resolvedService = schemaData.service || service;
        nextSchemas[resolvedService] = schemaData.schema_data || schemaData.schema;

        const configResponse = await fetch(`${API_BASE_URL}/config`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: session.sessionId,
            service,
            provider,
          }),
        });
        const configData = await configResponse.json();
        if (!configResponse.ok) {
          throw new Error(configData.detail || `Config generation failed for ${service}.`);
        }

        nextConfigs[configData.service || resolvedService] = configData.config;
        setAllConfigs({ ...nextConfigs });
        setSchemas({ ...nextSchemas });
        setLoadingServices((current) => current.filter((item) => item !== service));
      }
      setStatusMessage(`Configured ${services.length} service${services.length === 1 ? '' : 's'}.`);
    } catch (error) {
      setStatusMessage(error.message);
    } finally {
      setIsConfiguring(false);
    }
  };

  const handleResendVerification = async () => {
    setResendingEmail(true);
    setEmailBannerMessage('');
    try {
      if (auth.currentUser) {
        await sendEmailVerification(auth.currentUser);
        setEmailBannerMessage('Verification email sent. Please check your inbox.');
      }
    } catch (error) {
      if (error.code === 'auth/too-many-requests') {
        setEmailBannerMessage('Too many requests. Please wait a few minutes before trying again.');
      } else {
        setEmailBannerMessage('Failed to send verification email. Please try again later.');
      }
    } finally {
      setResendingEmail(false);
    }
  };

  const handleSignOut = async () => {
    const result = await signOutUser();
    if (result.success) {
      navigate('/signin', { replace: true });
      return;
    }
    setStatusMessage(result.error || 'Failed to sign out.');
  };

  const userName = user?.displayName || user?.email?.split('@')[0] || 'Nimbus user';
  const isEmailPasswordProvider = user?.providerData?.some((item) => item.providerId === 'password');
  const showVerificationBanner =
    Boolean(user) && isEmailPasswordProvider && !user?.emailVerified && !verificationBannerDismissed;

  return (
    <div className="min-h-screen bg-[#0E0C09] text-white">
      <div className="mx-auto max-w-[1480px] px-4 py-6">
        {verifiedNoticeVisible ? (
          <div className="mb-4 rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-5 py-4 text-sm text-emerald-100">
            Email verified successfully.
          </div>
        ) : null}

        {showVerificationBanner ? (
          <div className="mb-4 rounded-2xl border border-yellow-400/20 bg-yellow-500/10 px-5 py-4 text-sm text-yellow-100">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                Verify <span className="font-medium">{user?.email}</span> to keep your workspace fully unlocked.
                {emailBannerMessage ? <div className="mt-2 text-xs text-yellow-100/80">{emailBannerMessage}</div> : null}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleResendVerification}
                  disabled={resendingEmail}
                  className="rounded-xl bg-[#D4A43C] px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
                >
                  {resendingEmail ? 'Sending...' : 'Resend'}
                </button>
                <button
                  onClick={() => setVerificationBannerDismissed(true)}
                  className="rounded-xl border border-yellow-400/20 px-4 py-2 text-sm"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        ) : null}

        <div className="mb-6 flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/[0.03] px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#D4A43C]">Nimbus Workspace</p>
            <h1 className="mt-3 text-3xl font-semibold">Cloud Security Copilot</h1>
            <p className="mt-2 max-w-3xl text-sm leading-7 text-[#9F978E]">
              A quieter workspace for analyzing company context, generating secure service configurations, and exporting implementation-ready Terraform.
            </p>
          </div>
          <div className="flex flex-col items-start gap-3 text-sm text-[#C9C1B8] lg:items-end">
            <div>{userName}</div>
            <div>{user?.email}</div>
            <button
              onClick={handleSignOut}
              className="rounded-2xl border border-white/10 px-4 py-2 text-sm transition-colors hover:bg-white/[0.04]"
            >
              Sign out
            </button>
          </div>
        </div>

        {statusMessage ? (
          <div className="mb-4 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-[#E7DED2]">
            {statusMessage}
          </div>
        ) : null}

        <div className="grid gap-4 xl:grid-cols-[380px_minmax(0,1fr)]">
          <IntakePanel
            provider={provider}
            session={session}
            selectedServices={selectedServices}
            setSelectedServices={setSelectedServices}
            onProviderChange={setProvider}
            onAnalyze={analyzeDescription}
            onConfigureSelected={() => configureSelectedServices(selectedServices)}
            isAnalyzing={isAnalyzing}
            isConfiguring={isConfiguring}
          />
          <ConfigPanel
            session={session}
            provider={provider}
            configs={allConfigs}
            schemas={schemas}
            loadingServices={loadingServices}
            onConfigUpdate={handleConfigUpdate}
          />
        </div>
      </div>
    </div>
  );
}
