import { useEffect, useMemo, useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:5000';

const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

export default function ConfigPanel({
  session,
  provider,
  configs,
  schemas,
  loadingServices,
  onConfigUpdate,
}) {
  const providerLabel = PROVIDER_LABELS[provider] || provider.toUpperCase();
  const configuredServices = Object.keys(configs || {});
  const availableServices = Array.from(
    new Set([...(session?.suggestedServices || []), ...configuredServices, ...loadingServices]),
  );
  const [activeService, setActiveService] = useState(configuredServices[0] || '');
  const [activeTab, setActiveTab] = useState('recommended');
  const [existingConfigJson, setExistingConfigJson] = useState('');
  const [optimizeGaps, setOptimizeGaps] = useState({});
  const [notice, setNotice] = useState('');
  const [noticeTone, setNoticeTone] = useState('neutral');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [explainField, setExplainField] = useState(null);
  const [explainMessages, setExplainMessages] = useState([]);
  const [explainInput, setExplainInput] = useState('');
  const [isExplaining, setIsExplaining] = useState(false);

  useEffect(() => {
    if (!activeService && availableServices.length) {
      setActiveService(availableServices[0]);
    }
    if (activeService && !availableServices.includes(activeService) && availableServices.length) {
      setActiveService(availableServices[0]);
    }
  }, [activeService, availableServices]);

  const activeConfig = configs?.[activeService] || {};
  const activeSchemaFields = schemas?.[activeService]?.fields || [];
  const fieldMap = useMemo(
    () => Object.fromEntries(activeSchemaFields.map((field) => [field.fieldId, field])),
    [activeSchemaFields],
  );

  const setBanner = (message, tone = 'neutral') => {
    setNotice(message);
    setNoticeTone(tone);
    window.setTimeout(() => setNotice(''), 3000);
  };

  const openExplainPanel = (fieldId, value, reason) => {
    const metadata = fieldMap[fieldId] || {};
    setExplainField({
      fieldId,
      label: metadata.label || fieldId,
      value,
      reason,
    });
    setExplainMessages([
      {
        role: 'assistant',
        content: `Ask about ${metadata.label || fieldId}. Nimbus will explain the recommendation for this company.`,
      },
    ]);
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    try {
      const parsed = JSON.parse(existingConfigJson);
      const response = await fetch(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: session.sessionId,
          service: activeService,
          existingConfig: parsed,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Optimization failed.');
      }
      setOptimizeGaps((current) => ({ ...current, [activeService]: data.gaps || [] }));
      if ((data.gaps || []).length === 0) {
        setBanner('No security or compliance gaps found.', 'success');
      }
    } catch (error) {
      if (error instanceof SyntaxError) {
        setBanner('Invalid JSON. Please fix the input and try again.', 'error');
      } else {
        setBanner(error.message, 'error');
      }
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleExplain = async () => {
    if (!explainField || !explainInput.trim()) {
      return;
    }
    const outgoing = explainInput;
    setExplainInput('');
    setExplainMessages((current) => [...current, { role: 'user', content: outgoing }]);
    setIsExplaining(true);
    try {
      const response = await fetch(`${API_BASE_URL}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: session.sessionId,
          fieldId: explainField.fieldId,
          fieldLabel: explainField.label,
          currentValue: explainField.value,
          inlineReason: explainField.reason,
          message: outgoing,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Explain failed.');
      }
      if (data.configUpdate && activeService) {
        onConfigUpdate?.(
          activeService,
          data.configUpdate.fieldId,
          data.configUpdate.newValue,
          data.configUpdate.newReason,
        );
        setExplainField((current) =>
          current
            ? {
                ...current,
                value: data.configUpdate.newValue,
                reason: data.configUpdate.newReason,
              }
            : current,
        );
        setBanner(`Updated ${data.configUpdate.fieldId} for ${activeService}.`, 'success');
      }
      setExplainMessages((current) => [...current, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setExplainMessages((current) => [...current, { role: 'assistant', content: error.message }]);
    } finally {
      setIsExplaining(false);
    }
  };

  const downloadTerraform = async (exportAll = false) => {
    try {
      const response = await fetch(`${API_BASE_URL}/terraform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: session.sessionId,
          service: exportAll ? null : activeService,
          provider,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Terraform export failed.');
      }

      const terraformContent = data.terraformContent;
      const downloadName = exportAll
        ? 'nimbus-all-services-config.tf'
        : `nimbus-${activeService.toLowerCase()}-config.tf`;
      const blob = new Blob([terraformContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = downloadName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setBanner(`${downloadName} downloaded`, 'success');
    } catch (error) {
      setBanner(error.message, 'error');
    }
  };

  const noticeStyles =
    noticeTone === 'error'
      ? 'border-red-400/20 bg-red-500/10 text-red-100'
      : noticeTone === 'success'
        ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-100'
        : 'border-white/10 bg-white/[0.04] text-white';

  return (
    <div className="grid min-h-[760px] gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03]">
        <div className="border-b border-white/8 px-6 py-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#D4A43C]">
            Workspace
          </p>
          <div className="mt-3 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">
                {activeService ? `${providerLabel} ${activeService} Configuration` : `${providerLabel} Configuration`}
              </h2>
              <p className="mt-2 text-sm leading-6 text-[#9F978E]">
                A focused review surface for recommendations, gaps, and Terraform exports.
              </p>
            </div>
            {notice ? <div className={`rounded-2xl border px-4 py-3 text-sm ${noticeStyles}`}>{notice}</div> : null}
          </div>
        </div>

        <div className="border-b border-white/8 px-4 py-3">
          <div className="flex flex-wrap gap-2">
            {availableServices.map((service) => {
              const configured = Boolean(configs?.[service]);
              const loading = loadingServices.includes(service);
              return (
                <button
                  key={service}
                  type="button"
                  onClick={() => setActiveService(service)}
                  className={`rounded-2xl border px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] ${
                    activeService === service
                      ? 'border-[#D4A43C]/40 bg-[#D4A43C]/12 text-[#F6E3B4]'
                      : 'border-white/10 text-[#C9C1B8] hover:bg-white/[0.04]'
                  }`}
                >
                  {service} {configured ? 'Done' : ''} {loading ? 'Loading' : ''}
                </button>
              );
            })}
          </div>
        </div>

        <div className="border-b border-white/8 px-4 py-3">
          <div className="flex gap-2">
            {[
              ['recommended', 'Recommended'],
              ['optimize', 'Optimise'],
              ['terraform', 'Terraform'],
            ].map(([key, label]) => (
              <button
                key={key}
                type="button"
                onClick={() => setActiveTab(key)}
                className={`rounded-2xl border px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] ${
                  activeTab === key
                    ? 'border-white/20 bg-white/[0.08] text-white'
                    : 'border-white/10 text-[#9F978E] hover:bg-white/[0.04]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {!session ? (
            <div className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-[#8E857A]">
              Sign in, analyze a company profile, and choose the services you want to configure.
            </div>
          ) : null}

          {session && activeTab === 'recommended' ? (
            <div className="space-y-3">
              {Object.keys(activeConfig).length === 0 ? (
                <div className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-[#8E857A]">
                  No configuration has been generated for this service yet.
                </div>
              ) : null}
              {Object.entries(activeConfig).map(([fieldId, entry]) => {
                const value = entry?.value ?? entry;
                const reason = entry?.reason ?? '';
                return (
                  <div key={fieldId} className="rounded-2xl border border-white/10 p-5">
                    <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="mono text-sm font-semibold text-white">{fieldId}</span>
                          <span className="rounded-full border border-white/10 px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[#BFB6AB]">
                            {providerLabel}
                          </span>
                        </div>
                        <div className="mt-3 text-sm font-medium text-[#F2E7D1]">{String(value)}</div>
                        <div className="mt-2 text-sm leading-7 text-[#9F978E]">{reason}</div>
                      </div>
                      <button
                        type="button"
                        onClick={() => openExplainPanel(fieldId, value, reason)}
                        className="rounded-2xl border border-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition-colors hover:bg-white/[0.04]"
                      >
                        Ask Follow-up
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : null}

          {session && activeTab === 'optimize' ? (
            <div className="space-y-4">
              <textarea
                value={existingConfigJson}
                onChange={(event) => setExistingConfigJson(event.target.value)}
                className="h-56 w-full rounded-2xl border border-white/10 bg-[#12100d] p-4 font-mono text-xs text-white placeholder:text-[#7D7368] focus:border-[#D4A43C]/35 focus:outline-none"
                placeholder='{"ServerSideEncryptionConfiguration":"None","BlockPublicAcls":false}'
              />
              <button
                type="button"
                onClick={handleOptimize}
                disabled={isOptimizing || !activeService}
                className="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition-colors hover:bg-[#F3EEE8] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isOptimizing ? 'Analyzing...' : 'Analyze Existing Config'}
              </button>

              {(optimizeGaps[activeService] || []).map((gap, index) => (
                <div key={`${gap.fieldId}-${index}`} className="rounded-2xl border border-white/10 p-5">
                  <div className="flex items-center justify-between gap-4">
                    <div className="mono text-sm font-semibold text-white">{gap.fieldId}</div>
                    <div className="rounded-full border border-red-400/20 bg-red-500/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-red-100">
                      {gap.severity}
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-2xl bg-[#161310] p-4">
                      <div className="text-[10px] uppercase tracking-[0.18em] text-[#7D7368]">Current</div>
                      <div className="mt-2 text-sm text-red-200">{gap.currentValue}</div>
                    </div>
                    <div className="rounded-2xl bg-[#161310] p-4">
                      <div className="text-[10px] uppercase tracking-[0.18em] text-[#7D7368]">Recommended</div>
                      <div className="mt-2 text-sm text-emerald-200">{gap.recommendedValue}</div>
                    </div>
                  </div>
                  <div className="mt-4 text-sm leading-7 text-[#9F978E]">{gap.reason}</div>
                  <button
                    type="button"
                    onClick={() => openExplainPanel(gap.fieldId, gap.currentValue, gap.reason)}
                    className="mt-4 rounded-2xl border border-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition-colors hover:bg-white/[0.04]"
                  >
                    Ask Follow-up
                  </button>
                </div>
              ))}
            </div>
          ) : null}

          {session && activeTab === 'terraform' ? (
            <div className="rounded-3xl border border-white/10 p-8 text-center">
              <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#D4A43C]">
                Terraform
              </p>
              <h3 className="mt-3 text-2xl font-semibold text-white">Export Infrastructure Code</h3>
              <p className="mt-2 text-sm leading-6 text-[#9F978E]">
                Download the active service or the full session as deployable Terraform.
              </p>
              {!activeService || !configs?.[activeService] ? (
                <div className="mt-6 rounded-2xl border border-dashed border-white/10 p-5 text-sm text-[#8E857A]">
                  Generate a recommended config first, then export it as Terraform.
                </div>
              ) : (
                <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => downloadTerraform(false)}
                    disabled={!activeService || !configs?.[activeService]}
                    className="rounded-2xl border border-white/10 px-5 py-3 text-sm text-white transition-colors hover:bg-white/[0.04] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Download as Terraform ({providerLabel})
                  </button>
                  <button
                    type="button"
                    onClick={() => downloadTerraform(true)}
                    disabled={configuredServices.length === 0}
                    className="rounded-2xl bg-[#D4A43C] px-5 py-3 text-sm font-semibold text-black transition-colors hover:bg-[#E0B458] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Export All as Terraform
                  </button>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </section>

      <aside className="rounded-3xl border border-white/10 bg-white/[0.03]">
        <div className="border-b border-white/8 px-5 py-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#D4A43C]">
            Conversation
          </p>
          <h3 className="mt-3 text-xl font-semibold text-white">
            {explainField ? explainField.label : 'Select A Field'}
          </h3>
          <p className="mt-2 text-sm leading-6 text-[#9F978E]">
            Keep follow-ups focused on one setting at a time.
          </p>
        </div>
        <div className="flex h-[560px] flex-col">
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {!explainField ? (
              <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-[#8E857A]">
                Choose any recommended field or gap to open a lightweight explanation thread.
              </div>
            ) : null}
            {explainMessages.map((message, index) => (
              <div key={`${message.role}-${index}`} className="space-y-1">
                <div className="text-[10px] uppercase tracking-[0.18em] text-[#7D7368]">
                  {message.role === 'user' ? 'You' : 'Nimbus'}
                </div>
                <div
                  className={
                    message.role === 'user'
                      ? 'rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm leading-7 text-white'
                      : 'rounded-2xl border border-[#D4A43C]/20 bg-[#D4A43C]/8 p-4 text-sm leading-7 text-[#F2E7D1]'
                  }
                >
                  {message.content}
                </div>
              </div>
            ))}
          </div>
          <div className="border-t border-white/8 p-4">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleExplain();
              }}
              className="space-y-3"
            >
              <input
                type="text"
                value={explainInput}
                onChange={(event) => setExplainInput(event.target.value)}
                disabled={!explainField || isExplaining}
                className="h-11 w-full rounded-2xl border border-white/10 bg-[#12100d] px-4 text-sm text-white placeholder:text-[#7D7368] focus:border-[#D4A43C]/35 focus:outline-none disabled:opacity-50"
                placeholder="Ask a follow-up"
              />
              <button
                type="submit"
                disabled={!explainField || isExplaining || !explainInput.trim()}
                className="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition-colors hover:bg-[#F3EEE8] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isExplaining ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      </aside>
    </div>
  );
}
