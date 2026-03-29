import { useEffect, useMemo, useRef, useState } from 'react';
import { sendEmailVerification } from 'firebase/auth';
import { PanelRightOpen, User2, X } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import AdvisorChatPanel, { AdvisorChatComposer, AdvisorChatTranscript } from '../components/workspace/AdvisorChatPanel';
import ConfigPanel from '../components/workspace/ConfigPanel';
import RequirementRail from '../components/workspace/RequirementRail';
import { signOutUser } from '../firebase/authService';
import { auth } from '../firebase/config';
import {
  areWorkspaceSnapshotsEqual,
  createWorkspaceStorageKey,
  loadWorkspacePersistence,
  saveWorkspacePersistence,
  upsertWorkspaceSnapshot,
} from '../utils/workspacePersistence';

const API_BASE_URL = 'http://127.0.0.1:5000';
const SUPPORTED_OBJECTIVES = ['recommendation', 'optimize'];
const DEFAULT_CONTEXT_COVERAGE = {
  business: false,
  scale: false,
  security: false,
  cost: false,
};
const OBJECTIVE_LABELS = {
  recommendation: 'Recommendation',
  optimize: 'Optimise',
};

const OBJECTIVE_INTRO = {
  recommendation:
    'Describe the company and workload in your own words. I will keep asking follow-up questions until I have enough context to recommend the best provider and service mix, then I will explain exactly why it matches your requirements.',
  optimize:
    'Please provide the current configurations of your cloud service so I can optimize them based on your company context and compliance requirements.',
};

const normalizeObjectiveSelection = (objective) =>
  SUPPORTED_OBJECTIVES.includes(objective) ? objective : 'optimize';

const createInitialChat = (objective = 'optimize') => [
  {
    role: 'assistant',
    content: OBJECTIVE_INTRO[normalizeObjectiveSelection(objective)] || OBJECTIVE_INTRO.optimize,
  },
];

const buildFollowUpApiMessage = (context, message) => {
  if (!context) {
    return message;
  }

  return [
    `Follow-up context: ${context.referenceLabel}`,
    `Service: ${context.service}`,
    `Provider: ${context.provider}`,
    context.fieldId ? `Field: ${context.fieldId}` : null,
    context.value !== undefined ? `Current value: ${String(context.value)}` : null,
    context.recommendedValue !== undefined ? `Recommended value: ${String(context.recommendedValue)}` : null,
    context.severity ? `Severity: ${context.severity}` : null,
    context.reason ? `Reasoning: ${context.reason}` : null,
    `User follow-up: ${message}`,
  ]
    .filter(Boolean)
    .join('\n');
};

const buildFollowUpDisplayMessage = (context, message) => {
  if (!context) {
    return message;
  }

  return `Follow-up on ${context.referenceLabel}\n${message}`;
};

const truncateText = (value, maxLength = 96) => {
  const normalized = (value || '').trim();
  if (!normalized) {
    return '';
  }
  return normalized.length > maxLength ? `${normalized.slice(0, maxLength - 3)}...` : normalized;
};

const createSessionTitle = (messages, objective) => {
  const firstUserMessage = (messages || []).find((message) => message.role === 'user')?.content;
  return truncateText(firstUserMessage, 64) || `${OBJECTIVE_LABELS[objective] || 'Nimbus'} session`;
};

const createSessionPreview = (snapshot) => {
  const lastMessage = [...(snapshot?.chatMessages || [])]
    .reverse()
    .find((message) => typeof message?.content === 'string' && message.content.trim());

  return truncateText(lastMessage?.content || snapshot?.preparedSummary || 'Saved workspace snapshot', 116);
};

const formatSessionTimestamp = (value) => {
  if (!value) {
    return 'Saved recently';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return 'Saved recently';
  }

  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};

export default function DemoWorkspace() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedObjective, setSelectedObjective] = useState('optimize');
  const [sessionId, setSessionId] = useState(null);
  const [chatMessages, setChatMessages] = useState(createInitialChat('optimize'));
  const [chatInput, setChatInput] = useState('');
  const [advisoryContext, setAdvisoryContext] = useState({});
  const [contextCoverage, setContextCoverage] = useState(DEFAULT_CONTEXT_COVERAGE);
  const [architectureOptions, setArchitectureOptions] = useState([]);
  const [preparedSummary, setPreparedSummary] = useState('');
  const [reasoningMode, setReasoningMode] = useState('bedrock-model');
  const [allConfigs, setAllConfigs] = useState({});
  const [schemas, setSchemas] = useState({});
  const [serviceCatalog, setServiceCatalog] = useState({});
  const [loadingServices, setLoadingServices] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const [isConfiguring, setIsConfiguring] = useState(false);
  const [activeFollowUpContext, setActiveFollowUpContext] = useState(null);
  const [chatFocusSignal, setChatFocusSignal] = useState(0);
  const [verifiedNoticeVisible, setVerifiedNoticeVisible] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [emailBannerMessage, setEmailBannerMessage] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [previousSessions, setPreviousSessions] = useState([]);
  const [isLoadingSession, setIsLoadingSession] = useState(false);
  const [savedSessions, setSavedSessions] = useState([]);
  const [activeSavedSessionId, setActiveSavedSessionId] = useState(null);
  const [storageReady, setStorageReady] = useState(false);
  const [loadedStorageKey, setLoadedStorageKey] = useState(null);
  const chatPanelRef = useRef(null);
  const storageKey = useMemo(() => createWorkspaceStorageKey(user?.uid), [user?.uid]);

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

  const resetWorkspace = (nextObjective = 'optimize') => {
    const normalizedObjective = normalizeObjectiveSelection(nextObjective);
    setSelectedObjective(normalizedObjective);
    setSessionId(null);
    setChatMessages(createInitialChat(normalizedObjective));
    setChatInput('');
    setAdvisoryContext({});
    setContextCoverage(DEFAULT_CONTEXT_COVERAGE);
    setArchitectureOptions([]);
    setPreparedSummary('');
    setReasoningMode('bedrock-model');
    setAllConfigs({});
    setSchemas({});
    setServiceCatalog({});
    setLoadingServices([]);
    setStatusMessage('');
    setActiveFollowUpContext(null);
  };

  const applyWorkspaceSnapshot = (snapshot) => {
    const nextObjective = normalizeObjectiveSelection(snapshot?.objective);

    setSelectedObjective(nextObjective);
    setSessionId(snapshot?.sessionId || null);
    setChatMessages(
      Array.isArray(snapshot?.chatMessages) && snapshot.chatMessages.length
        ? snapshot.chatMessages
        : createInitialChat(nextObjective),
    );
    setChatInput('');
    setAdvisoryContext(snapshot?.advisoryContext || {});
    setContextCoverage({
      ...DEFAULT_CONTEXT_COVERAGE,
      ...(snapshot?.contextCoverage || {}),
    });
    setArchitectureOptions(Array.isArray(snapshot?.architectureOptions) ? snapshot.architectureOptions : []);
    setPreparedSummary(snapshot?.preparedSummary || '');
    setReasoningMode(snapshot?.reasoningMode || 'bedrock-model');
    setAllConfigs(snapshot?.allConfigs || {});
    setSchemas(snapshot?.schemas || {});
    setServiceCatalog(snapshot?.serviceCatalog || {});
    setLoadingServices([]);
    setStatusMessage('');
    setActiveFollowUpContext(null);
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
    if (!storageKey) {
      setSavedSessions([]);
      setActiveSavedSessionId(null);
      setStorageReady(false);
      setLoadedStorageKey(null);
      resetWorkspace('optimize');
      return;
    }

    const persisted = loadWorkspacePersistence(storageKey);
    const activeSnapshot = persisted.activeSessionId
      ? persisted.sessions.find((item) => item.sessionId === persisted.activeSessionId)
      : null;

    setSavedSessions(persisted.sessions);
    setActiveSavedSessionId(persisted.activeSessionId);

    if (activeSnapshot) {
      applyWorkspaceSnapshot(activeSnapshot);
    } else {
      resetWorkspace('optimize');
    }

    setLoadedStorageKey(storageKey);
    setStorageReady(true);
  }, [storageKey]);

  useEffect(() => {
    if (!storageReady || !storageKey || loadedStorageKey !== storageKey || !sessionId) {
      return;
    }

    const snapshotSeed = {
      sessionId,
      title: createSessionTitle(chatMessages, selectedObjective),
      objective: selectedObjective,
      chatMessages,
      advisoryContext,
      contextCoverage,
      architectureOptions,
      preparedSummary,
      reasoningMode,
      allConfigs,
      schemas,
      serviceCatalog,
    };

    setSavedSessions((current) => {
      const existing = current.find((item) => item.sessionId === sessionId);
      const comparableSnapshot = {
        ...snapshotSeed,
        createdAt: existing?.createdAt || '',
        updatedAt: existing?.updatedAt || '',
      };

      if (existing && areWorkspaceSnapshotsEqual(existing, comparableSnapshot)) {
        return current;
      }

      const timestamp = new Date().toISOString();
      return upsertWorkspaceSnapshot(current, {
        ...snapshotSeed,
        createdAt: existing?.createdAt || timestamp,
        updatedAt: timestamp,
      });
    });
    setActiveSavedSessionId((current) => (current === sessionId ? current : sessionId));
  }, [
    advisoryContext,
    allConfigs,
    architectureOptions,
    chatMessages,
    contextCoverage,
    preparedSummary,
    reasoningMode,
    schemas,
    selectedObjective,
    serviceCatalog,
    sessionId,
    loadedStorageKey,
    storageKey,
    storageReady,
  ]);

  useEffect(() => {
    if (!storageReady || !storageKey || loadedStorageKey !== storageKey) {
      return;
    }

    saveWorkspacePersistence(storageKey, {
      activeSessionId: activeSavedSessionId,
      sessions: savedSessions,
    });
  }, [activeSavedSessionId, loadedStorageKey, savedSessions, storageKey, storageReady]);

  useEffect(() => {
    const hasUserMessages = chatMessages.some((message) => message.role === 'user');
    if (!hasUserMessages) {
      setChatMessages(createInitialChat(selectedObjective));
    }
  }, [selectedObjective]);

  // Load previous sessions from DynamoDB when user is available
  useEffect(() => {
    if (user?.uid) {
      fetch(`${API_BASE_URL}/sessions?userId=${encodeURIComponent(user.uid)}`)
        .then((r) => r.json())
        .then((d) => setPreviousSessions(Array.isArray(d) ? d : []))
        .catch(() => {});
    } else {
      setPreviousSessions([]);
    }
  }, [user?.uid]);

  const sendChatMessage = async (message) => {
    const nextMessage = message.trim();
    if (!nextMessage) {
      return;
    }
    const followUpContext = activeFollowUpContext;
    const displayMessage = buildFollowUpDisplayMessage(followUpContext, nextMessage);
    const apiMessage = buildFollowUpApiMessage(followUpContext, nextMessage);

    setStatusMessage('');
    setIsChatting(true);
    setChatInput('');
    setChatMessages((current) => [...current, { role: 'user', content: displayMessage }]);
    setActiveFollowUpContext(null);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          message: apiMessage,
          objective: selectedObjective,
          userId: user?.uid || '',
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
      setReasoningMode(data.reasoningMode || 'bedrock-model');
      setSelectedObjective(normalizeObjectiveSelection(data.objective || selectedObjective));
      setChatMessages((current) => [...current, { role: 'assistant', content: data.reply }]);
      // Refresh sidebar session list
      if (user?.uid) {
        fetch(`${API_BASE_URL}/sessions?userId=${encodeURIComponent(user.uid)}`)
          .then((r) => r.json())
          .then((d) => setPreviousSessions(Array.isArray(d) ? d : []))
          .catch(() => {});
      }
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
      setReasoningMode('bedrock-model');
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

  const handleAskFollowUp = (followUpContext) => {
    setActiveFollowUpContext(followUpContext);
    setChatFocusSignal((current) => current + 1);
    window.setTimeout(() => {
      chatPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 0);
  };

  const handleStartNewSession = () => {
    setActiveSavedSessionId(null);
    resetWorkspace(selectedObjective);
    setSettingsOpen(false);
  };

  const handleRestoreSession = async (sessionIdToRestore) => {
    if (!sessionIdToRestore) {
      return;
    }

    setIsLoadingSession(true);
    setStatusMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionIdToRestore}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to load session.');
      }

      const snapshot = {
        sessionId: data.sessionId,
        title: data.sessionTitle,
        objective: data.advisoryObjective,
        chatMessages: data.chatMessages,
        advisoryContext: data.advisoryContext,
        contextCoverage: data.contextCoverage,
        architectureOptions: data.architectureOptions,
        preparedSummary: data.preparedSummary,
        reasoningMode: data.reasoningMode,
        allConfigs: data.allConfigs,
        schemas: data.schemas,
        serviceCatalog: data.serviceCatalog,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
      };

      applyWorkspaceSnapshot(snapshot);
      setActiveSavedSessionId(snapshot.sessionId);
      setSettingsOpen(false);
      setStatusMessage(`Restored ${snapshot.title || 'saved session'}.`);
    } catch (error) {
      setStatusMessage(error.message);
    } finally {
      setIsLoadingSession(false);
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

  const activeDrawerSessionId = sessionId || activeSavedSessionId;
  const currentSavedSession = useMemo(
    () => savedSessions.find((item) => item.sessionId === activeDrawerSessionId) || null,
    [activeDrawerSessionId, savedSessions],
  );
  const previousSessionsLocal = useMemo(
    () => savedSessions.filter((item) => item.sessionId !== activeDrawerSessionId),
    [activeDrawerSessionId, savedSessions],
  );
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
                <h1 className="font-brand">
                  <span className="brand-wordmark" aria-label="Nimbus">
                    <span className="brand-wordmark__halo" />
                    <span className="brand-wordmark__capsule">
                      <span className="brand-wordmark__text">Nimbus</span>
                    </span>
                  </span>
                </h1>
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

          <main className="min-h-0 flex-1 overflow-y-auto">
            <div className="min-w-0 px-5 py-2 sm:px-6">
              <div className="flex min-h-full flex-col gap-3 pb-4">
                {hasStartedConversation ? (
                  <RequirementRail
                    advisoryContext={advisoryContext}
                    contextCoverage={contextCoverage}
                    preparedSummary={preparedSummary}
                    reasoningMode={reasoningMode}
                    embedded
                  />
                ) : null}

                {hasConfigLabContent ? (
                  <>
                    <div className="min-h-0 flex-1">
                      <AdvisorChatTranscript
                        messages={chatMessages}
                        onSendMessage={sendChatMessage}
                        isChatting={isChatting}
                        architectureOptions={architectureOptions}
                        reasoningMode={reasoningMode}
                        onConfigureProviderPlan={handleConfigureProviderPlan}
                        onConfigureFullOption={handleConfigureFullOption}
                        isConfiguring={isConfiguring}
                        embedded
                        selectedObjective={selectedObjective}
                      />
                    </div>

                    <div className="border-t border-[#d6e8f3] bg-[#fbfdff]">
                      <ConfigPanel
                        session={session}
                        configs={allConfigs}
                        schemas={schemas}
                        loadingServices={loadingServices}
                        serviceCatalog={serviceCatalog}
                        onAskFollowUp={handleAskFollowUp}
                        embedded
                      />
                    </div>

                    <div ref={chatPanelRef} className="border-t border-[#d6e8f3] pt-3">
                      <AdvisorChatComposer
                        chatInput={chatInput}
                        onInputChange={setChatInput}
                        onSendMessage={sendChatMessage}
                        selectedObjective={selectedObjective}
                        pendingFollowUpContext={activeFollowUpContext}
                        onClearFollowUpContext={() => setActiveFollowUpContext(null)}
                        composerFocusSignal={chatFocusSignal}
                        embedded
                      />
                    </div>
                  </>
                ) : (
                  <div ref={chatPanelRef} className="min-h-0 flex-1">
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
                      pendingFollowUpContext={activeFollowUpContext}
                      onClearFollowUpContext={() => setActiveFollowUpContext(null)}
                      composerFocusSignal={chatFocusSignal}
                    />
                  </div>
                )}
              </div>
            </div>
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
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#2792df]">Current session</div>
                  <div className="mt-2 text-sm font-semibold text-[#16324a]">
                    {currentSavedSession?.title || `${OBJECTIVE_LABELS[selectedObjective] || 'Nimbus'} session`}
                  </div>
                  <div className="mt-1 text-xs text-[#5f7f97]">
                    {currentSavedSession
                      ? `${OBJECTIVE_LABELS[normalizeObjectiveSelection(currentSavedSession.objective)] || 'Optimise'} | ${formatSessionTimestamp(currentSavedSession.updatedAt)}`
                      : 'Start a new advisory thread and Nimbus will keep this workspace saved locally.'}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleStartNewSession}
                  className="rounded-2xl border border-[#d7e9f4] px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#315770] transition-colors hover:bg-white"
                >
                  New session
                </button>
              </div>
              <div className="mt-4 space-y-3 text-sm text-[#4e6c82]">
                <div className="flex items-center justify-between gap-4">
                  <span>Context captured</span>
                  <span className="font-semibold text-[#16324a]">{readyCount}/4</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Reasoning mode</span>
                  <span className="font-semibold capitalize text-[#16324a]">
                    {reasoningMode === 'bedrock-model' ? 'Model-backed' : 'Model-backed'}
                  </span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Session started</span>
                  <span className="font-semibold text-[#16324a]">{sessionId ? 'Active' : 'Not started'}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span>Saved session ID</span>
                  <span className="font-semibold text-[#16324a]">{currentSavedSession?.sessionId?.slice(0, 8) || 'Pending'}</span>
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
                {previousSessions.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-3 text-sm text-[#5f7f97]">
                    Your conversation history will appear here after you start chatting.
                  </div>
                ) : (
                  previousSessions.map((s) => (
                    <button
                      key={s.sessionId}
                      type="button"
                      onClick={() => handleRestoreSession(s.sessionId)}
                      disabled={isLoadingSession}
                      className={`w-full rounded-2xl border p-3 text-left transition-colors disabled:opacity-50 ${
                        s.sessionId === sessionId
                          ? 'border-[#8ecff9] bg-[#eaf7ff]'
                          : 'border-[#d7e9f4] bg-white/80 hover:bg-white'
                      }`}
                    >
                      <div className="truncate text-sm font-medium text-[#16324a]">
                        {s.sessionTitle || 'Untitled chat'}
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <span className="rounded-full border border-[#d7e9f4] px-2 py-0.5 text-[10px] uppercase tracking-[0.14em] text-[#6b8ba2]">
                          {normalizeObjectiveSelection(s.advisoryObjective)}
                        </span>
                        <span className="text-[10px] text-[#8ba5b8]">
                          {s.createdAt ? new Date(s.createdAt).toLocaleDateString() : ''}
                        </span>
                      </div>
                    </button>
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
