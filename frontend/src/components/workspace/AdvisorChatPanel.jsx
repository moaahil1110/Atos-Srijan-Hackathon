import { useEffect, useRef, useState } from 'react';

const STARTER_PROMPTS = [
  'We are a healthcare startup handling patient records and billing for clinics across India.',
  'We need a secure SaaS backend for enterprise customers and our budget is tight in year one.',
  'We are building an AI data platform with strict compliance and we already use Microsoft tools heavily.',
];

const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

const OBJECTIVE_META = {
  recommendation: {
    headingStart: 'Start the conversation',
    helper:
      'Nimbus will discover the requirements it needs, then recommend the best provider and service mix with clear reasoning.',
    placeholder:
      'Tell Nimbus about the workload, industry, compliance posture, scale, budget, or current stack.',
    starterPrompts: STARTER_PROMPTS,
    optionsEyebrow: 'Prepared recommendation',
    optionsHeading: 'Best-fit cloud options',
    actionLabel: 'Load recommendation',
    providerActionPrefix: 'Load',
  },
  optimize: {
    headingStart: 'Prepare an optimization target',
    helper:
      'Nimbus will prepare the strongest target architecture first, then you can compare it against your current cloud setup.',
    placeholder:
      'Describe the workload and any current-cloud pain points, gaps, or controls you want Nimbus to optimize.',
    starterPrompts: [
      'We run a healthcare SaaS on AWS and want Nimbus to find the strongest secure target before we compare against our current setup.',
      'We already have a customer-facing backend and want to understand what the ideal architecture should look like before optimizing cost and security gaps.',
      'We use Microsoft-heavy tooling today and want Nimbus to prepare the target cloud pattern we should compare our current estate against.',
    ],
    optionsEyebrow: 'Prepared optimization target',
    optionsHeading: 'Target architectures to compare against',
    actionLabel: 'Prepare optimization target',
    providerActionPrefix: 'Prepare',
  },
};

export function AdvisorChatTranscript({
  messages,
  onSendMessage,
  isChatting,
  architectureOptions,
  reasoningMode,
  onConfigureProviderPlan,
  onConfigureFullOption,
  isConfiguring,
  selectedObjective = 'optimize',
  embedded = false,
}) {
  const scrollRef = useRef(null);
  const [expandedOptionId, setExpandedOptionId] = useState(null);
  const hasStartedConversation = messages.some((message) => message.role === 'user');
  const objective = OBJECTIVE_META[selectedObjective] || OBJECTIVE_META.optimize;

  useEffect(() => {
    if (!scrollRef.current) {
      return;
    }
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, isChatting, architectureOptions]);

  useEffect(() => {
    if (!architectureOptions.length) {
      setExpandedOptionId(null);
      return;
    }
    if (!expandedOptionId || !architectureOptions.some((option) => option.optionId === expandedOptionId)) {
      setExpandedOptionId(architectureOptions[0].optionId);
    }
  }, [architectureOptions, expandedOptionId]);

  const reasoningLabel = reasoningMode === 'bedrock-model' ? 'Model-backed reasoning' : 'Model-backed reasoning';

  return (
    <section className={`flex min-h-[480px] flex-col overflow-hidden ${embedded ? 'bg-transparent' : ''}`}>
      <div className="border-b border-[#d6e8f3] px-5 py-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <h2 className="text-[clamp(1.45rem,2vw,1.9rem)] font-semibold leading-tight text-[#14324a]">
              {objective.headingStart}
            </h2>
            <p className="mt-1.5 max-w-3xl text-sm leading-7 text-[#4e6c82]">{objective.helper}</p>
          </div>
          {hasStartedConversation ? (
            <div className="inline-flex rounded-full border border-[#b7d8eb] bg-[#f7fbfe] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315770]">
              {reasoningLabel}
            </div>
          ) : null}
        </div>
      </div>

      <div ref={scrollRef} className="space-y-4 overflow-y-auto px-5 py-5">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={message.role === 'user' ? 'ml-auto max-w-[76%]' : 'max-w-[84%]'}>
            <div
              className={
                message.role === 'user'
                  ? 'message-bubble-user rounded-[24px] p-4 text-sm leading-7 whitespace-pre-wrap'
                  : 'message-bubble-assistant rounded-[24px] p-4 text-sm leading-7 whitespace-pre-wrap'
              }
            >
              {message.content}
            </div>
          </div>
        ))}

        {messages.length <= 1 ? (
          <div className="grid gap-2 md:grid-cols-3">
            {objective.starterPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => onSendMessage(prompt)}
                className="rounded-2xl border border-[#d7e9f4] bg-[#f8fcff] p-4 text-left text-sm leading-6 text-[#35556b] transition-colors hover:bg-white"
              >
                {prompt}
              </button>
            ))}
          </div>
        ) : null}

        {isChatting ? (
          <div className="max-w-[84%]">
            <div className="message-bubble-assistant rounded-[24px] p-4">
              <div className="flex items-center gap-2">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
        </div>
        ) : null}

        {architectureOptions.length > 0 ? (
          <div className="mt-6 space-y-3">
            <div>
              <div className="text-[10px] uppercase tracking-[0.18em] text-[#6d8ba0]">{objective.optionsEyebrow}</div>
              <h3 className="mt-2 text-xl font-semibold text-[#14324a]">{objective.optionsHeading}</h3>
            </div>

            {architectureOptions.map((option) => {
              const expanded = expandedOptionId === option.optionId;
              return (
                <div key={option.optionId} className="rounded-[28px] border border-[#d7e9f4] bg-[#fafdff] p-4">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 max-w-3xl">
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="rounded-full border border-[#a9d8f4] bg-[#eef8ff] px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-[#2792df]">
                          {option.mode}
                        </div>
                        <div className="rounded-full border border-[#d7e9f4] px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-[#41637a]">
                          Fit score {option.fitScore}
                        </div>
                      </div>
                      <h4 className="mt-3 text-lg font-semibold text-[#14324a]">{option.title}</h4>
                      <p className="mt-2 text-sm leading-7 text-[#35556b]">{option.summary}</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => setExpandedOptionId(expanded ? null : option.optionId)}
                        className="rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#315770] transition-colors hover:bg-white"
                      >
                        {expanded ? 'Hide details' : 'Show details'}
                      </button>
                      <button
                        type="button"
                        onClick={() => onConfigureFullOption(option)}
                        disabled={isConfiguring}
                        className="rounded-2xl bg-[#58b7ff] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isConfiguring ? 'Preparing...' : objective.actionLabel}
                      </button>
                    </div>
                  </div>

                  {expanded ? (
                    <div className="mt-4 space-y-4 border-t border-[#e2eef6] pt-4">
                      <p className="text-sm leading-7 text-[#4e6c82]">{option.detailedExplanation}</p>

                      <div className="rounded-2xl border border-[#d7e9f4] bg-white/70 p-4">
                        <div className="text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">Matched requirements</div>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {option.matchedRequirements.map((item) => (
                            <span key={item} className="rounded-full border border-[#d7e9f4] px-3 py-1 text-xs text-[#35566c]">
                              {item}
                            </span>
                          ))}
                        </div>
                        <div className="mt-4 text-sm leading-7 text-[#4e6c82]">{option.tradeoffs}</div>
                      </div>

                      {option.providers.map((providerBlock) => (
                        <div key={`${option.optionId}-${providerBlock.provider}`} className="rounded-2xl border border-[#d7e9f4] bg-white/72 p-4">
                          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                            <div className="max-w-2xl">
                              <div className="text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">{providerBlock.role}</div>
                              <h5 className="mt-2 text-lg font-semibold text-[#14324a]">
                                {PROVIDER_LABELS[providerBlock.provider] || providerBlock.provider.toUpperCase()}
                              </h5>
                              <p className="mt-2 text-sm leading-7 text-[#35556b]">{providerBlock.reason}</p>
                              {providerBlock.detailedReason ? (
                                <p className="mt-2 text-sm leading-7 text-[#4e6c82]">{providerBlock.detailedReason}</p>
                              ) : null}
                            </div>
                            <button
                              type="button"
                              onClick={() =>
                                onConfigureProviderPlan(
                                  providerBlock.provider,
                                  providerBlock.services.map((item) => item.service),
                                  option.title,
                                )
                              }
                              disabled={isConfiguring}
                              className="rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {isConfiguring
                                ? 'Preparing...'
                                : `${objective.providerActionPrefix} ${PROVIDER_LABELS[providerBlock.provider] || providerBlock.provider.toUpperCase()} configs`}
                            </button>
                          </div>

                          <div className="mt-4 space-y-3">
                            {providerBlock.services.map((service) => (
                              <div key={`${providerBlock.provider}-${service.service}`} className="rounded-2xl border border-[#d7e9f4] bg-[#f8fcff] p-4">
                                <div className="text-sm font-semibold text-[#14324a]">{service.service}</div>
                                <p className="mt-2 text-sm leading-7 text-[#35556b]">{service.reason}</p>
                                {service.detailedReason ? (
                                  <p className="mt-2 text-sm leading-7 text-[#4e6c82]">{service.detailedReason}</p>
                                ) : null}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        ) : null}
      </div>
    </section>
  );
}

export function AdvisorChatComposer({
  chatInput,
  onInputChange,
  onSendMessage,
  selectedObjective = 'optimize',
  pendingFollowUpContext = null,
  onClearFollowUpContext,
  composerFocusSignal = 0,
  embedded = false,
}) {
  const textareaRef = useRef(null);
  const objective = OBJECTIVE_META[selectedObjective] || OBJECTIVE_META.optimize;
  const followUpReferenceLabel = pendingFollowUpContext?.referenceLabel || '';

  const handleComposerKeyDown = (event) => {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent?.isComposing) {
      return;
    }
    event.preventDefault();
    onSendMessage(chatInput);
  };

  useEffect(() => {
    if (!composerFocusSignal || !textareaRef.current) {
      return;
    }
    textareaRef.current.focus();
    textareaRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [composerFocusSignal]);

  return (
    <section
      className={`overflow-hidden ${
        embedded ? 'rounded-[32px] border border-[#c9e0ef] bg-white/76 shadow-[0_18px_45px_rgba(115,173,214,0.12)] backdrop-blur-md' : ''
      }`}
    >
      <div className="bg-white/86 px-5 py-4">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            onSendMessage(chatInput);
          }}
          className="space-y-3"
        >
          {pendingFollowUpContext ? (
            <div className="rounded-[24px] border border-[#a9d8f4] bg-[#eef8ff] p-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#2792df]">Follow-up context</div>
                  <div className="mt-2 text-sm font-semibold text-[#14324a]">{followUpReferenceLabel}</div>
                  <div className="mt-1 text-sm leading-6 text-[#4e6c82]">
                    Your next message will reference this configuration detail in the main Nimbus chat.
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => onClearFollowUpContext?.()}
                  className="rounded-2xl border border-[#c1def2] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-[#f8fcff]"
                >
                  Clear reference
                </button>
              </div>
            </div>
          ) : null}
          <textarea
            ref={textareaRef}
            value={chatInput}
            onChange={(event) => onInputChange(event.target.value)}
            onKeyDown={handleComposerKeyDown}
            placeholder={pendingFollowUpContext ? `Ask Nimbus about ${followUpReferenceLabel}.` : objective.placeholder}
            className="h-24 w-full rounded-[24px] border border-[#c9e0ef] bg-white px-5 py-4 text-sm leading-7 text-[#14324a] placeholder:text-[#6f8ea3] focus:border-[#58b7ff] focus:outline-none"
          />
          <div className="text-xs text-[#5f7f97]">Press Enter to send. Use Shift+Enter for a new line.</div>
        </form>
      </div>
    </section>
  );
}

export default function AdvisorChatPanel(props) {
  const { embedded = false } = props;

  return (
    <section
      className={`flex min-h-[640px] flex-col overflow-hidden ${
        embedded
          ? 'bg-transparent lg:h-full'
          : 'rounded-[32px] border border-[#c9e0ef] bg-white/76 shadow-[0_18px_45px_rgba(115,173,214,0.12)] backdrop-blur-md lg:h-[calc(100vh-210px)]'
      }`}
    >
      <div className="flex min-h-0 flex-1 flex-col">
        <AdvisorChatTranscript {...props} embedded />
        <div className="border-t border-[#d6e8f3]">
          <AdvisorChatComposer {...props} embedded={false} />
        </div>
      </div>
    </section>
  );
}
