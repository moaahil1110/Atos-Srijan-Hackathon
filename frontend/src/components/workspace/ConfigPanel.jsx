import { ScanSearch } from 'lucide-react';
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
  onAskFollowUp,
  embedded = false,
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
  const [optimizePanelOpen, setOptimizePanelOpen] = useState({});
  const [existingConfigInputs, setExistingConfigInputs] = useState({});
  const [optimizeGaps, setOptimizeGaps] = useState({});
  const [optimizeChecked, setOptimizeChecked] = useState({});
  const [notice, setNotice] = useState('');
  const [noticeTone, setNoticeTone] = useState('neutral');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isTerraformLoading, setIsTerraformLoading] = useState(false);

  useEffect(() => {
    if (!activeService && availableServices.length) {
      setActiveService(availableServices[0]);
    }
    if (activeService && !availableServices.includes(activeService) && availableServices.length) {
      setActiveService(availableServices[0]);
    }
  }, [activeService, availableServices]);

  const activeConfig = configs?.[activeService] || {};
  const activeSchema = schemas?.[activeService] || {};
  const activeSchemaFields = activeSchema?.fields || [];
  const activeProvider = serviceCatalog?.[activeService]?.provider || activeSchema?.provider || 'aws';
  const providerLabel = PROVIDER_LABELS[activeProvider] || activeProvider.toUpperCase();
  const fieldMap = useMemo(
    () => Object.fromEntries(activeSchemaFields.map((field) => [field.fieldId, field])),
    [activeSchemaFields],
  );

  const noticeStyles =
    noticeTone === 'error'
      ? 'border-red-300 bg-red-50 text-red-700'
      : noticeTone === 'success'
        ? 'border-emerald-300 bg-emerald-50 text-emerald-700'
        : 'border-[#d7e9f4] bg-white/70 text-[#35556d]';

  const isServiceLoading = (service) =>
    (loadingServices || []).some((item) => item === service || item.endsWith(`:${service}`));

  const getTerraformDownloadName = (serviceName) =>
    `nimbus-${(serviceName || 'service').toLowerCase().replaceAll(' ', '-')}-config.tf`;

  const downloadTerraformFile = (terraformContent, serviceName) => {
    const downloadName = getTerraformDownloadName(serviceName);
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

  const setBanner = (message, tone = 'neutral') => {
    setNotice(message);
    setNoticeTone(tone);
    window.setTimeout(() => setNotice(''), 3000);
  };

  const openFollowUp = ({ fieldId, label, value, reason, currentValue, recommendedValue, severity }) => {
    const metadata = fieldMap[fieldId] || {};
    onAskFollowUp?.({
      service: activeService,
      provider: activeProvider,
      fieldId,
      label: label || metadata.label || fieldId,
      value,
      reason,
      currentValue,
      recommendedValue,
      severity,
      referenceLabel: `${providerLabel} ${activeService} / ${label || metadata.label || fieldId}`,
    });
  };

  const handleOptimizeToggle = (serviceName) => {
    setOptimizePanelOpen((current) => ({
      ...current,
      [serviceName]: !current[serviceName],
    }));
  };

  const handleConfigUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file || !activeService) {
      return;
    }

    try {
      const text = await file.text();
      JSON.parse(text);
      setExistingConfigInputs((current) => ({
        ...current,
        [activeService]: text,
      }));
      setBanner(`${file.name} loaded for ${activeService}.`, 'success');
    } catch (error) {
      setBanner('That file is not valid JSON.', 'error');
    } finally {
      event.target.value = '';
    }
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

  const downloadTerraform = async () => {
    if (!session?.sessionId) {
      return;
    }

    if (!activeService || !configs?.[activeService]) {
      return;
    }

    setIsTerraformLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/terraform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: session.sessionId,
          service: activeService,
          provider: activeProvider,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Terraform export failed.');
      }
      downloadTerraformFile(data.terraformContent, activeService);
    } catch (error) {
      setBanner(error.message, 'error');
    } finally {
      setIsTerraformLoading(false);
    }
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

      <div className="space-y-5 p-4">
        {!session ? (
          <div className="rounded-2xl border border-dashed border-[#d7e9f4] p-6 text-sm text-[#5f7f97]">
            Start the advisory conversation first. Nimbus will gather your requirements before it prepares any cloud configuration.
          </div>
        ) : null}

        {session ? (
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
                      onClick={() => openFollowUp({ fieldId, value, reason })}
                      className="w-fit rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white"
                    >
                      Ask Follow-up
                    </button>
                  </div>
                </div>
              );
            })}
            {availableServices.length > 0 && Object.keys(activeConfig).length > 0 ? (
              <div className="space-y-4">
                <div className="rounded-[28px] border border-[#9fd8ff] bg-[linear-gradient(180deg,#eef8ff_0%,#fafdff_100%)] p-5 shadow-[0_14px_30px_rgba(88,183,255,0.12)]">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#2792df]">
                        <ScanSearch className="h-4 w-4" />
                        Important next step
                      </div>
                      <div className="mt-2 text-base font-semibold text-[#14324a]">Optimize against your current JSON config</div>
                      <div className="mt-1 text-sm leading-7 text-[#4e6c82]">
                        Upload your existing {activeService} JSON here to compare it directly against Nimbus recommendations for this service.
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleOptimizeToggle(activeService)}
                      className="rounded-2xl bg-[#58b7ff] px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#08304d] transition-colors hover:bg-[#7dcaff]"
                    >
                      {optimizePanelOpen[activeService] ? 'Hide optimization' : 'Open optimization review'}
                    </button>
                  </div>

                  {optimizePanelOpen[activeService] ? (
                    <div className="mt-4 space-y-4 border-t border-[#e2eef6] pt-4">
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                        <label className="w-fit cursor-pointer rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white">
                          Upload JSON
                          <input type="file" accept=".json,application/json" className="hidden" onChange={handleConfigUpload} />
                        </label>
                        <div className="text-xs text-[#5f7f97]">
                          Upload a file or paste JSON below, then run the comparison.
                        </div>
                      </div>

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
                            onClick={() =>
                              openFollowUp({
                                fieldId: gap.fieldId,
                                value: gap.currentValue,
                                reason: gap.reason,
                                currentValue: gap.currentValue,
                                recommendedValue: gap.recommendedValue,
                                severity: gap.severity,
                              })
                            }
                            className="mt-4 rounded-2xl border border-[#d7e9f4] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[#21506b] transition-colors hover:bg-white"
                          >
                            Ask Follow-up
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>

                <div className="rounded-2xl border border-[#d7e9f4] bg-white/84 p-5">
                  <div className="text-sm leading-7 text-[#4e6c82]">
                    Download Terraform after reviewing the final configuration shown above.
                  </div>
                  <button
                    type="button"
                    onClick={downloadTerraform}
                    disabled={isTerraformLoading || !activeService}
                    className="mt-4 rounded-2xl bg-[#58b7ff] px-4 py-3 text-sm font-semibold text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isTerraformLoading ? 'Preparing Terraform...' : 'Download Terraform'}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  );
}
