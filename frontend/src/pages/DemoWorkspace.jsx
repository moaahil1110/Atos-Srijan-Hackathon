import { useEffect, useMemo, useState } from 'react';
import { sendEmailVerification } from 'firebase/auth';
import { PanelRightOpen, User2, X } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import AdvisorChatPanel from '../components/workspace/AdvisorChatPanel';
import ConfigPanel from '../components/workspace/ConfigPanel';
import RequirementRail from '../components/workspace/RequirementRail';
import { signOutUser } from '../firebase/authService';
import { auth } from '../firebase/config';

const API_BASE_URL = 'http://127.0.0.1:5000';
const OBJECTIVE_TAB_MAP = {
  recommendation: 'recommended',
  optimize: 'optimize',
  terraform: 'terraform',
};

const OBJECTIVE_INTRO = {
  recommendation:
    'Describe the company and workload in your own words. I will keep asking follow-up questions until I have enough context to recommend the best provider and service mix, then I will explain exactly why it matches your requirements.',
  optimize:
    'Describe the company, workload, and any current-cloud concerns. I will gather enough context to prepare the strongest target architecture first, then you can compare it against your current setup in the optimization flow.',
  terraform:
    'Describe the company and workload in your own words. I will gather the context needed to shape a Terraform-ready cloud plan, then I will explain why that architecture best fits your requirements.',
};

const createInitialChat = (objective = 'recommendation') => [
  {
    role: 'assistant',
    content: OBJECTIVE_INTRO[objective] || OBJECTIVE_INTRO.recommendation,
  },
];

export default function DemoWorkspace() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedObjective, setSelectedObjective] = useState('recommendation');
  const [sessionId, setSessionId] = useState(null);
  const [chatMessages, setChatMessages] = useState(createInitialChat('recommendation'));
  const [chatInput, setChatInput] = useState('');
  const [advisoryContext, setAdvisoryContext] = useState({});
  const [contextCoverage, setContextCoverage] = useState({
    business: false,
    scale: false,
    security: false,
    cost: false,
  });
  const [architectureOptions, setArchitectureOptions] = useState([]);
  const [preparedSummary, setPreparedSummary] = useState('');
  const [reasoningMode, setReasoningMode] = useState('fallback');
  const [allConfigs, setAllConfigs] = useState({});
  const [schemas, setSchemas] = useState({});
  const [serviceCatalog, setServiceCatalog] = useState({});
  const [loadingServices, setLoadingServices] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const [isConfiguring, setIsConfiguring] = useState(false);
  const [verifiedNoticeVisible, setVerifiedNoticeVisible] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [emailBannerMessage, setEmailBannerMessage] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);

  const session = useMemo(
    () =>
      sessionId
        ? {
            sessionId,
            suggestedServices: Object.keys(serviceCatalog),
          }
        : null,
    [serviceCatalog, sessionId],
  );

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

  useEffect(() => {
    const hasUserMessages = chatMessages.some((message) => message.role === 'user');
    if (!hasUserMessages) {
      setChatMessages(createInitialChat(selectedObjective));
    }
  }, [selectedObjective]);

  const sendChatMessage = async (message) => {
    const nextMessage = message.trim();
    if (!nextMessage) {
      return;
    }

    setStatusMessage('');
    setIsChatting(true);
    setChatInput('');
    setChatMessages((current) => [...current, { role: 'user', content: nextMessage }]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          message: nextMessage,
          objective: selectedObjective,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Conversation failed.');
      }

      setSessionId(data.sessionId);
      setAdvisoryContext(data.extracted_fields || {});
      setContextCoverage(
        data.context_coverage || {
          business: false,
          scale: false,
          security: false,
          cost: false,
        },
      );
      setArchitectureOptions(data.architecture_options || []);
      setPreparedSummary(data.prepared_summary || '');
      setReasoningMode(data.reasoningMode || 'fallback');
      setSelectedObjective(data.objective || selectedObjective);
      setChatMessages((current) => [...current, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setStatusMessage(error.message);
      setChatMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content:
            'I hit an error while processing that message. Please retry, and I will continue the requirement interview from the current context.',
        },
      ]);
      setReasoningMode('fallback');
    } finally {
      setIsChatting(false);
    }
  };

  const configurePlan = async (planItems, label) => {
    if (!sessionId || !planItems.length) {
      return;
    }

    setIsConfiguring(true);
    setStatusMessage('');
    const nextConfigs = { ...allConfigs };
    const nextSchemas = { ...schemas };
    const nextCatalog = { ...serviceCatalog };

    try {
      for (let index = 0; index < planItems.length; index += 1) {
        const plan = planItems[index];
        const loadingKey = `${plan.provider}:${plan.service}`;
        setLoadingServices((current) => [...new Set([...current, loadingKey])]);
        setStatusMessage(
          `Preparing ${plan.service} on ${plan.provider.toUpperCase()}... (${index + 1} of ${planItems.length})`,
        );

        const schemaResponse = await fetch(`${API_BASE_URL}/schema`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId,
            service: plan.service,
            provider: plan.provider,
          }),
        });
        const schemaData = await schemaResponse.json();
        if (!schemaResponse.ok) {
          throw new Error(schemaData.detail || `Schema fetch failed for ${plan.service}.`);
        }

        const resolvedService = schemaData.service || plan.service;
        const resolvedProvider = schemaData.provider || plan.provider;
        nextSchemas[resolvedService] = schemaData.schema_data || schemaData.schema;
        nextCatalog[resolvedService] = {
          provider: resolvedProvider,
          sourceLabel: label,
        };
        setSchemas({ ...nextSchemas });
        setServiceCatalog({ ...nextCatalog });

        const configResponse = await fetch(`${API_BASE_URL}/config`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId,
            service: plan.service,
            provider: plan.provider,
          }),
        });
        const configData = await configResponse.json();
        if (!configResponse.ok) {
          throw new Error(configData.detail || `Config generation failed for ${plan.service}.`);
        }

        const configuredService = configData.service || resolvedService;
        nextConfigs[configuredService] = configData.config;
        nextCatalog[configuredService] = {
          provider: resolvedProvider,
          sourceLabel: label,
        };
        setAllConfigs({ ...nextConfigs });
        setServiceCatalog({ ...nextCatalog });
        setLoadingServices((current) => current.filter((item) => item !== loadingKey));
      }

      setStatusMessage(`Prepared ${planItems.length} service configuration${planItems.length === 1 ? '' : 's'} from ${label}.`);
    } catch (error) {
      setStatusMessage(error.message);
    } finally {
      setIsConfiguring(false);
      setLoadingServices([]);
    }
  };

  const handleConfigureProviderPlan = async (provider, services, label) => {
    const planItems = services.map((service) => ({ provider, service }));
    await configurePlan(planItems, label);
  };

  const handleConfigureFullOption = async (option) => {
    const planItems = option.providers.flatMap((providerBlock) =>
      providerBlock.services.map((serviceInfo) => ({
        provider: providerBlock.provider,
        service: serviceInfo.service,
      })),
    );
    await configurePlan(planItems, option.title);
  };

  const handleObjectiveChange = (nextObjective) => {
    if (nextObjective === selectedObjective) {
      return;
    }
    setSelectedObjective(nextObjective);
    if (chatMessages.some((message) => message.role === 'user')) {
      const labels = {
        recommendation: 'recommendation-ready output',
        optimize: 'optimization-ready output',
        terraform: 'Terraform-ready output',
      };
      setStatusMessage(`Nimbus will now steer this session toward ${labels[nextObjective] || 'the selected output'}.`);
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
  const needsVerification = Boolean(user) && isEmailPasswordProvider && !user?.emailVerified;
  const readyCount = Object.values(contextCoverage || {}).filter(Boolean).length;
  const hasStartedConversation = chatMessages.some((message) => message.role === 'user');
  const hasConfigLabContent =
    Object.keys(serviceCatalog || {}).length > 0 ||
    Object.keys(allConfigs || {}).length > 0 ||
    Object.keys(schemas || {}).length > 0 ||
    (loadingServices || []).length > 0;

  return (
    <div className="min-h-screen bg-transparent text-[#14324a]">
      <div className="mx-auto flex min-h-screen max-w-[1640px] flex-col px-4 py-4">
        {verifiedNoticeVisible ? (
          <div className="mb-3 rounded-2xl border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            Email verified successfully.
          </div>
        ) : null}

        <section className="flex flex-1 flex-col overflow-hidden rounded-[32px] border border-[#c9e0ef] bg-white/78 shadow-[0_22px_55px_rgba(115,173,214,0.12)] backdrop-blur-md">
          <header className="px-5 pb-1 pt-4 sm:px-6">
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0">
                <h1 className="font-brand brand-wordmark">Nimbus</h1>
              </div>
              <button
                type="button"
                onClick={() => setSettingsOpen(true)}
                aria-label="Open workspace drawer"
                className="relative inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-[#c9e0ef] bg-white/90 text-[#315770] transition-colors hover:bg-white"
              >
                <PanelRightOpen className="h-4 w-4" />
                {needsVerification ? <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-[#2792df]" /> : null}
              </button>
            </div>
          </header>

          {statusMessage ? (
            <div className="px-5 pb-1 pt-1 sm:px-6">
              <div className="rounded-2xl border border-[#d7e9f4] bg-[#f9fcff] px-4 py-3 text-sm text-[#41627a]">{statusMessage}</div>
            </div>
          ) : null}

          {hasStartedConversation ? (
            <div className="px-5 pb-1 pt-2 sm:px-6">
              <RequirementRail
                advisoryContext={advisoryContext}
                contextCoverage={contextCoverage}
                preparedSummary={preparedSummary}
                reasoningMode={reasoningMode}
                embedded
              />
            </div>
          ) : null}

          <main
            className={`min-h-0 flex-1 ${
              hasConfigLabContent ? 'grid xl:grid-cols-[minmax(0,1fr)_390px] xl:items-stretch' : ''
            }`}
          >
            <div className="min-w-0 px-5 py-2 sm:px-6">
              <AdvisorChatPanel
                messages={chatMessages}
                chatInput={chatInput}
                onInputChange={setChatInput}
                onSendMessage={sendChatMessage}
                isChatting={isChatting}
                architectureOptions={architectureOptions}
                preparedSummary={preparedSummary}
                reasoningMode={reasoningMode}
                onConfigureProviderPlan={handleConfigureProviderPlan}
                onConfigureFullOption={handleConfigureFullOption}
                isConfiguring={isConfiguring}
                embedded
                selectedObjective={selectedObjective}
                onObjectiveChange={handleObjectiveChange}
              />
            </div>

            {hasConfigLabContent ? (
              <aside className="min-h-0 border-t border-[#d6e8f3] bg-[#fbfdff] xl:border-l xl:border-t-0">
                <ConfigPanel
                  session={session}
                  configs={allConfigs}
                  schemas={schemas}
                  loadingServices={loadingServices}
                  serviceCatalog={serviceCatalog}
                  onConfigUpdate={handleConfigUpdate}
                  embedded
                  preferredTab={OBJECTIVE_TAB_MAP[selectedObjective] || 'recommended'}
                />
              </aside>
            ) : null}
          </main>
        </section>
      </div>

      {settingsOpen ? (
        <div className="fixed inset-0 z-50">
          <button
            type="button"
            aria-label="Close workspace menu"
            onClick={() => setSettingsOpen(false)}
            className="absolute inset-0 bg-[#7caecf]/20 backdrop-blur-[2px]"
          />
          <aside className="absolute right-4 top-4 bottom-4 w-[min(380px,calc(100vw-2rem))] overflow-y-auto rounded-[28px] border border-[#c9e0ef] bg-white/92 p-5 shadow-[0_24px_60px_rgba(69,124,163,0.18)] backdrop-blur-md">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">Workspace menu</p>
                <h2 className="mt-2 text-2xl font-semibold text-[#16324a]">Account and session</h2>
              </div>
              <button
                type="button"
                onClick={() => setSettingsOpen(false)}
                className="rounded-2xl border border-[#d7e9f4] p-2 text-[#315770] transition-colors hover:bg-[#f8fcff]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-5 rounded-3xl border border-[#d7e9f4] bg-[#f8fcff] p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e6f5ff] text-[#2792df]">
                  <User2 className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold text-[#16324a]">{userName}</div>
                  <div className="truncate text-sm text-[#4e6c82]">{user?.email}</div>
                </div>
              </div>
            </div>

            {needsVerification ? (
              <div className="mt-4 rounded-3xl border border-sky-200 bg-sky-50 p-4">
                <div className="text-sm font-semibold text-[#21506b]">Email verification pending</div>
                <p className="mt-2 text-sm leading-6 text-[#4e6c82]">
                  Verify <span className="font-medium">{user?.email}</span> to keep your workspace fully unlocked.
                </p>
                {emailBannerMessage ? <div className="mt-3 text-xs text-[#4d6f89]">{emailBannerMessage}</div> : null}
                <button
                  onClick={handleResendVerification}
                  disabled={resendingEmail}
                  className="mt-4 rounded-2xl bg-[#58b7ff] px-4 py-2.5 text-sm font-semibold text-[#08304d] disabled:opacity-50"
                >
                  {resendingEmail ? 'Sending...' : 'Resend verification email'}
                </button>
              </div>
            ) : null}

            <div className="mt-4 rounded-3xl border border-[#d7e9f4] bg-[#fafdff] p-4">
              <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#2792df]">Current session</div>
              <div className="mt-3 space-y-3 text-sm text-[#4e6c82]">
                <div className="flex items-center justify-between gap-4">
                  <span>Context captured</span>
                  <span className="font-semibold text-[#16324a]">{readyCount}/4</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Reasoning mode</span>
                  <span className="font-semibold capitalize text-[#16324a]">
                    {reasoningMode === 'bedrock-model' ? 'Model-backed' : reasoningMode === 'hybrid' ? 'Model + fallback' : 'Fallback'}
                  </span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Session started</span>
                  <span className="font-semibold text-[#16324a]">{sessionId ? 'Active' : 'Not started'}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Output mode</span>
                  <span className="font-semibold capitalize text-[#16324a]">
                    {selectedObjective === 'optimize' ? 'Optimise' : selectedObjective}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-3xl border border-[#d7e9f4] bg-[#fafdff] p-4">
              <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#2792df]">Previous chats</div>
              <div className="mt-3 space-y-2">
                {chatMessages.length <= 1 ? (
                  <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-3 text-sm text-[#5f7f97]">
                    Your conversation history will appear here after you start chatting.
                  </div>
                ) : (
                  chatMessages.slice(1).map((message, index) => (
                    <div
                      key={`${message.role}-${index}`}
                      className="rounded-2xl border border-[#d7e9f4] bg-white/80 p-3"
                    >
                      <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#6b8ba2]">
                        {message.role === 'user' ? 'You' : 'Nimbus'}
                      </div>
                      <div className="mt-2 max-h-[72px] overflow-hidden text-sm leading-6 text-[#4e6c82]">{message.content}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <button
              onClick={handleSignOut}
              className="mt-6 w-full rounded-2xl border border-[#c9e0ef] bg-white px-4 py-3 text-sm font-semibold text-[#315770] transition-colors hover:bg-[#f8fcff]"
            >
              Sign out
            </button>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
