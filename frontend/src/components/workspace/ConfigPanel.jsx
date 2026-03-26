import { useEffect, useMemo, useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:5000';

const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

export default function ConfigPanel({
  session,
  configs,
  schemas,
  loadingServices,
  serviceCatalog,
  onConfigUpdate,
  embedded = false,
  preferredTab = 'recommended',
}) {
  const availableServices = useMemo(() => {
    const loadingNames = (loadingServices || []).map((item) => (item.includes(':') ? item.split(':').slice(1).join(':') : item));
    return Array.from(
      new Set([
        ...Object.keys(serviceCatalog || {}),
        ...Object.keys(configs || {}),
        ...Object.keys(schemas || {}),
        ...loadingNames,
      ]),
    );
  }, [configs, loadingServices, schemas, serviceCatalog]);

  const [activeService, setActiveService] = useState(availableServices[0] || '');
  const [activeTab, setActiveTab] = useState(preferredTab);
  const [existingConfigInputs, setExistingConfigInputs] = useState({});
  const [optimizeGaps, setOptimizeGaps] = useState({});
  const [optimizeChecked, setOptimizeChecked] = useState({});
  const [notice, setNotice] = useState('');
  const [noticeTone, setNoticeTone] = useState('neutral');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [explainField, setExplainField] = useState(null);
  const [explainMessages, setExplainMessages] = useState([]);
  const [explainInput, setExplainInput] = useState('');
  const [isExplaining, setIsExplaining] = useState(false);
  const [terraformPreviewCache, setTerraformPreviewCache] = useState({});
  const [terraformPreview, setTerraformPreview] = useState(null);
  const [isTerraformLoading, setIsTerraformLoading] = useState(false);

  useEffect(() => {
    if (!activeService && availableServices.length) {
      setActiveService(availableServices[0]);
    }
    if (activeService && !availableServices.includes(activeService) && availableServices.length) {
      setActiveService(availableServices[0]);
    }
  }, [activeService, availableServices]);

  useEffect(() => {
    if (preferredTab) {
      setActiveTab(preferredTab);
    }
  }, [preferredTab]);

  const activeConfig = configs?.[activeService] || {};
  const activeSchema = schemas?.[activeService] || {};
  const activeSchemaFields = activeSchema?.fields || [];
  const activeProvider = serviceCatalog?.[activeService]?.provider || activeSchema?.provider || 'aws';
  const providerLabel = PROVIDER_LABELS[activeProvider] || activeProvider.toUpperCase();
  const configuredServiceCount = Object.keys(configs || {}).length;
  const fieldMap = useMemo(
    () => Object.fromEntries(activeSchemaFields.map((field) => [field.fieldId, field])),
    [activeSchemaFields],
  );

  useEffect(() => {
    if (activeTab !== 'terraform' || !session?.sessionId) {
      return;
    }

    if (activeService && configs?.[activeService]) {
      const activePreviewKey = `${session.sessionId}:${activeProvider}:${activeService}`;
      if (terraformPreviewCache[activePreviewKey]) {
        if (terraformPreview?.key !== activePreviewKey) {
          setTerraformPreview(terraformPreviewCache[activePreviewKey]);
        }
        return;
      }

      void fetchTerraformPreview(false);
      return;
    }

    if (configuredServiceCount > 0) {
      const allServicesPreviewKey = `${session.sessionId}:all-services`;
      if (terraformPreviewCache[allServicesPreviewKey]) {
        if (terraformPreview?.key !== allServicesPreviewKey) {
          setTerraformPreview(terraformPreviewCache[allServicesPreviewKey]);
        }
        return;
      }

      void fetchTerraformPreview(true);
    }
  }, [
    activeProvider,
    activeService,
    activeTab,
    configuredServiceCount,
    configs,
    session?.sessionId,
    terraformPreview,
    terraformPreviewCache,
  ]);

  const noticeStyles =
    noticeTone === 'error'
      ? 'border-red-300 bg-red-50 text-red-700'
      : noticeTone === 'success'
        ? 'border-emerald-300 bg-emerald-50 text-emerald-700'
        : 'border-[#d7e9f4] bg-white/70 text-[#35556d]';

  const isServiceLoading = (service) =>
    (loadingServices || []).some((item) => item === service || item.endsWith(`:${service}`));

  const getTerraformDownloadName = (exportAll, serviceName) =>
    exportAll ? 'nimbus-all-services-config.tf' : `nimbus-${(serviceName || 'service').toLowerCase().replaceAll(' ', '-')}-config.tf`;

  const downloadTerraformFile = (terraformContent, exportAll, serviceName) => {
    const downloadName = getTerraformDownloadName(exportAll, serviceName);
    const blob = new Blob([terraformContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = downloadName;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
    setBanner(`${downloadName} downloaded`, 'success');
  };

  const getTerraformRequestMeta = (exportAll) => ({
    previewKey: exportAll ? `${session?.sessionId}:all-services` : `${session?.sessionId}:${activeProvider}:${activeService}`,
    previewLabel: exportAll ? 'All configured services' : `${providerLabel} ${activeService}`,
    serviceName: exportAll ? null : activeService,
    provider: activeProvider,
  });

  const setBanner = (message, tone = 'neutral') => {
    setNotice(message);
    setNoticeTone(tone);
    window.setTimeout(() => setNotice(''), 3000);
  };

  const openExplainPanel = (fieldId, value, reason) => {
    const metadata = fieldMap[fieldId] || {};
    setExplainField({
      service: activeService,
      provider: activeProvider,
      fieldId,
      label: metadata.label || fieldId,
      value,
      reason,
    });
    setExplainMessages([
      {
        role: 'assistant',
        content: `Ask about ${metadata.label || fieldId}. Nimbus will explain why it recommended this value for your stated requirements.`,
      },
    ]);
  };

  const handleOptimize = async () => {
    if (!activeService) {
      return;
    }

    setIsOptimizing(true);
    try {
      const parsed = JSON.parse(existingConfigInputs[activeService] || '{}');
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
      setOptimizeChecked((current) => ({ ...current, [activeService]: true }));
      setOptimizeGaps((current) => ({ ...current, [activeService]: data.gaps || [] }));
      if ((data.gaps || []).length === 0) {
        setBanner('No security or compliance gaps found for this service.', 'success');
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

      if (data.configUpdate && explainField.service) {
        onConfigUpdate?.(
          explainField.service,
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
        setBanner(`Updated ${data.configUpdate.fieldId} for ${explainField.service}.`, 'success');
      }

      setExplainMessages((current) => [...current, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setExplainMessages((current) => [...current, { role: 'assistant', content: error.message }]);
    } finally {
      setIsExplaining(false);
    }
  };

  const fetchTerraformPreview = async (exportAll = false, options = {}) => {
    const { download = false, force = false } = options;
    const { previewKey, previewLabel, serviceName, provider } = getTerraformRequestMeta(exportAll);

    if (!session?.sessionId) {
      return null;
    }

    if (!exportAll && (!serviceName || !configs?.[serviceName])) {
      return null;
    }

    if (exportAll && configuredServiceCount === 0) {
      return null;
    }

    if (!force && terraformPreviewCache[previewKey]) {
      const cachedPreview = terraformPreviewCache[previewKey];
      setTerraformPreview(cachedPreview);
      if (download) {
        downloadTerraformFile(cachedPreview.content, exportAll, serviceName);
      }
      return cachedPreview;
    }

    setIsTerraformLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/terraform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: session.sessionId,
          service: serviceName,
          provider,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Terraform export failed.');
      }

      const nextPreview = {
        key: previewKey,
        label: previewLabel,
        serviceName,
        content: data.terraformContent,
        updatedAt: new Date().toISOString(),
      };

      setTerraformPreviewCache((current) => ({
        ...current,
        [previewKey]: nextPreview,
      }));
      setTerraformPreview(nextPreview);

      if (download) {
        downloadTerraformFile(nextPreview.content, exportAll, serviceName);
      }

      return nextPreview;
    } catch (error) {
      setBanner(error.message, 'error');
      return null;
    } finally {
      setIsTerraformLoading(false);
    }
  };

  const downloadTerraform = async (exportAll = false) => {
    await fetchTerraformPreview(exportAll, { download: true });
  };

  return (
    <section
      className={`flex h-full min-h-0 flex-col overflow-hidden ${
        embedded
          ? 'bg-transparent'
          : 'rounded-3xl border border-[#c9e0ef] bg-white/76 shadow-[0_18px_45px_rgba(115,173,214,0.12)] backdrop-blur-md'
      }`}
    >
      <div className="border-b border-[#d6e8f3] px-5 py-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">Configuration Lab</p>
        <div className="mt-3 flex flex-col gap-4">
          <div>
            <h2 className="text-xl font-semibold text-[#14324a]">
              {activeService ? `${providerLabel} ${activeService}` : 'Prepared Service Configurations'}
            </h2>
            <p className="mt-2 text-sm leading-6 text-[#4e6c82]">
              Generate provider-specific recommendations from the advisory chat, then review, challenge, and export them here.
            </p>
          </div>
          {notice ? <div className={`rounded-2xl border px-4 py-3 text-sm ${noticeStyles}`}>{notice}</div> : null}
        </div>
      </div>

      <div className="border-b border-[#d6e8f3] px-4 py-3">
        <div className="flex flex-wrap gap-2">
          {availableServices.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[#d7e9f4] px-4 py-3 text-sm text-[#5f7f97]">
              Once you load a provider plan from the chat, the generated service configs will appear here.
            </div>
          ) : null}
          {availableServices.map((service) => {
            const serviceProvider = serviceCatalog?.[service]?.provider || schemas?.[service]?.provider || 'aws';
            const tabProviderLabel = PROVIDER_LABELS[serviceProvider] || serviceProvider.toUpperCase();
            const configured = Boolean(configs?.[service]);
            const loading = isServiceLoading(service);
            return (
              <button
                key={`${serviceProvider}-${service}`}
                type="button"
                onClick={() => setActiveService(service)}
                className={`rounded-2xl border px-4 py-2 text-left text-xs font-semibold uppercase tracking-[0.18em] ${
                  activeService === service
                    ? 'border-[#a9d8f4] bg-[#eef8ff] text-[#2792df]'
                    : 'border-[#d7e9f4] text-[#41637a] hover:bg-white'
                }`}
              >
                <div>{service}</div>
                <div className="mt-1 text-[10px] text-[#6b8ba2]">
                  {tabProviderLabel}
                  {configured ? ' - Ready' : ''}
                  {loading ? ' - Loading' : ''}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="border-b border-[#d6e8f3] px-4 py-3">
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
                  ? 'border-[#a9d8f4] bg-[#eef8ff] text-[#2792df]'
                  : 'border-[#d7e9f4] text-[#4e6c82] hover:bg-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-5 overflow-y-auto p-4">
        {!session ? (
          <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-6 text-sm text-[#5f7f97]">
            Start the advisory conversation first. Nimbus will gather your requirements before it prepares any cloud configuration.
          </div>
        ) : null}

        {session && activeTab === 'recommended' ? (
          <div className="space-y-3">
            {availableServices.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-6 text-sm text-[#5f7f97]">
                Load a recommendation from the conversation to populate this lab.
              </div>
            ) : null}

            {availableServices.length > 0 && Object.keys(activeConfig).length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-6 text-sm text-[#5f7f97]">
                {isServiceLoading(activeService) ? `Nimbus is preparing ${activeService} right now.` : 'No configuration has been generated for this service yet.'}
              </div>
            ) : null}

            {Object.entries(activeConfig).map(([fieldId, entry]) => {
              const value = entry?.value ?? entry;
              const reason = entry?.reason ?? '';
              return (
                <div key={fieldId} className="rounded-2xl border border-[#d7e9f4] bg-[#fafdff] p-5">
                  <div className="flex flex-col gap-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="mono text-sm font-semibold text-[#14324a]">{fieldId}</span>
                      <span className="rounded-full border border-[#d7e9f4] px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[#49697f]">
                        {providerLabel}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-[#21506b]">{String(value)}</div>
                    <div className="text-sm leading-7 text-[#4e6c82]">{reason}</div>
                    <button
                      type="button"
                      onClick={() => openExplainPanel(fieldId, value, reason)}
                      className="w-fit rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white"
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
              value={existingConfigInputs[activeService] || ''}
              onChange={(event) =>
                setExistingConfigInputs((current) => ({
                  ...current,
                  [activeService]: event.target.value,
                }))
              }
              className="h-56 w-full rounded-2xl border border-[#c9e0ef] bg-white/84 p-4 font-mono text-xs text-[#14324a] placeholder:text-[#6f8ea3] focus:border-[#58b7ff] focus:outline-none"
              placeholder='{"ServerSideEncryptionConfiguration":"None","BlockPublicAcls":false}'
            />
            <button
              type="button"
              onClick={handleOptimize}
              disabled={isOptimizing || !activeService}
              className="rounded-2xl bg-[#58b7ff] px-4 py-3 text-sm font-semibold text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isOptimizing ? 'Analyzing...' : 'Analyze Existing Config'}
            </button>

            {optimizeChecked[activeService] && (optimizeGaps[activeService] || []).length === 0 ? (
              <div className="rounded-2xl border border-emerald-300 bg-emerald-50 p-5 text-sm leading-7 text-emerald-700">
                Your existing configuration matches all recommended controls for this service.
              </div>
            ) : null}

            {(optimizeGaps[activeService] || []).map((gap, index) => (
              <div key={`${gap.fieldId}-${index}`} className="rounded-2xl border border-[#d7e9f4] bg-[#fafdff] p-5">
                <div className="flex items-center justify-between gap-4">
                  <div className="mono text-sm font-semibold text-[#14324a]">{gap.fieldId}</div>
                  <div className="rounded-full border border-red-300 bg-red-50 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-red-700">
                    {gap.severity}
                  </div>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <div className="rounded-2xl bg-[#fff7f7] p-4">
                    <div className="text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">Current</div>
                    <div className="mt-2 text-sm text-red-600">{String(gap.currentValue)}</div>
                  </div>
                  <div className="rounded-2xl bg-[#f5fffa] p-4">
                    <div className="text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">Recommended</div>
                    <div className="mt-2 text-sm text-emerald-700">{String(gap.recommendedValue)}</div>
                  </div>
                </div>
                <div className="mt-4 text-sm leading-7 text-[#4e6c82]">{gap.reason}</div>
                <button
                  type="button"
                  onClick={() => openExplainPanel(gap.fieldId, gap.currentValue, gap.reason)}
                  className="mt-4 rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white"
                >
                  Ask Follow-up
                </button>
              </div>
            ))}
          </div>
        ) : null}

        {session && activeTab === 'terraform' ? (
          <div className="rounded-3xl border border-[#d7e9f4] bg-[#fafdff] p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">Terraform</p>
            <h3 className="mt-3 text-2xl font-semibold text-[#14324a]">Preview Infrastructure Code</h3>
            <p className="mt-2 text-sm leading-6 text-[#4e6c82]">
              Review the generated HCL in the browser first, then download the active service or the full multi-service recommendation.
            </p>

            {configuredServiceCount === 0 ? (
              <div className="mt-6 rounded-2xl border border-dashed border-[#d7e9f4] p-5 text-sm text-[#5f7f97]">
                Generate a recommended config first, then export it as Terraform.
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                <div className="grid gap-3 lg:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => fetchTerraformPreview(false, { force: true })}
                    disabled={!activeService || !configs?.[activeService] || isTerraformLoading}
                    className="rounded-2xl border border-[#d7e9f4] px-5 py-3 text-sm text-[#21506b] transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isTerraformLoading && terraformPreview?.key === `${session?.sessionId}:${activeProvider}:${activeService}`
                      ? 'Refreshing preview...'
                      : `Preview ${providerLabel} ${activeService}`}
                  </button>
                  <button
                    type="button"
                    onClick={() => fetchTerraformPreview(true, { force: true })}
                    disabled={configuredServiceCount === 0 || isTerraformLoading}
                    className="rounded-2xl border border-[#d7e9f4] px-5 py-3 text-sm text-[#21506b] transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isTerraformLoading && terraformPreview?.key === `${session?.sessionId}:all-services`
                      ? 'Refreshing preview...'
                      : 'Preview all services'}
                  </button>
                </div>

                <div className="grid gap-3 lg:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => downloadTerraform(false)}
                    disabled={!activeService || !configs?.[activeService] || isTerraformLoading}
                    className="rounded-2xl border border-[#d7e9f4] px-5 py-3 text-sm text-[#21506b] transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Download as Terraform ({providerLabel})
                  </button>
                  <button
                    type="button"
                    onClick={() => downloadTerraform(true)}
                    disabled={configuredServiceCount === 0 || isTerraformLoading}
                    className="rounded-2xl bg-[#58b7ff] px-5 py-3 text-sm font-semibold text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Export All as Terraform
                  </button>
                </div>

                <div className="rounded-[28px] border border-[#d7e9f4] bg-[#f7fbfe] p-4">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#6b8ba2]">HCL preview</div>
                      <div className="mt-1 text-sm font-semibold text-[#14324a]">
                        {terraformPreview?.label || `${providerLabel} ${activeService}`}
                      </div>
                    </div>
                    <div className="text-xs text-[#6b8ba2]">
                      {isTerraformLoading
                        ? 'Generating preview...'
                        : terraformPreview?.updatedAt
                          ? `Updated ${new Date(terraformPreview.updatedAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`
                          : 'Preview will appear here'}
                    </div>
                  </div>

                  <div className="mt-4 overflow-hidden rounded-3xl border border-[#d7e9f4] bg-[#102131]">
                    {terraformPreview?.content ? (
                      <pre className="max-h-[420px] overflow-auto p-4 text-xs leading-6 text-[#d9ebfa]">
                        <code>{terraformPreview.content}</code>
                      </pre>
                    ) : (
                      <div className="p-5 text-sm text-[#c2d8ea]">
                        {isTerraformLoading
                          ? 'Nimbus is generating Terraform for this target.'
                          : 'Choose a preview target to inspect the generated HCL here.'}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {explainField ? (
          <div className="rounded-3xl border border-[#d7e9f4] bg-[#fafdff] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">Explain</p>
                <h3 className="mt-2 text-xl font-semibold text-[#14324a]">{explainField.label}</h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  setExplainField(null);
                  setExplainMessages([]);
                  setExplainInput('');
                }}
                className="rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white"
              >
                Close
              </button>
            </div>

            <div className="mt-5 space-y-3">
              {explainMessages.map((message, index) => (
                <div key={`${message.role}-${index}`} className={message.role === 'user' ? 'ml-auto max-w-[84%]' : 'max-w-[90%]'}>
                  <div className="mb-2 text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">
                    {message.role === 'user' ? 'You' : 'Nimbus'}
                  </div>
                  <div
                    className={
                      message.role === 'user'
                        ? 'message-bubble-user rounded-[22px] p-4 text-sm leading-7'
                        : 'message-bubble-assistant rounded-[22px] p-4 text-sm leading-7'
                    }
                  >
                    {message.content}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex flex-col gap-3">
              <textarea
                value={explainInput}
                onChange={(event) => setExplainInput(event.target.value)}
                placeholder="Ask Nimbus why this value matches your requirements, or challenge it with a trade-off."
                className="h-28 w-full rounded-2xl border border-[#c9e0ef] bg-white/84 p-4 text-sm leading-7 text-[#14324a] placeholder:text-[#6f8ea3] focus:border-[#58b7ff] focus:outline-none"
              />
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleExplain}
                  disabled={isExplaining || !explainInput.trim()}
                  className="rounded-2xl bg-[#58b7ff] px-5 py-3 text-sm font-semibold text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isExplaining ? 'Thinking...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
