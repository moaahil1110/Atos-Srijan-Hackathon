const LABELS = {
  industry: 'Industry',
  workload_type: 'Workload',
  scale: 'Scale',
  budget: 'Budget',
  compliance: 'Compliance',
  security_level: 'Security',
  current_stack: 'Stack',
};

const REASONING_LABELS = {
  'bedrock-model': 'Model-backed',
};

export default function RequirementRail({ advisoryContext, contextCoverage, preparedSummary, reasoningMode, embedded = false }) {
  const filled = Object.values(contextCoverage || {}).filter(Boolean).length;
  const total = Object.keys(contextCoverage || {}).length || 4;
  const entries = Object.entries(advisoryContext || {}).slice(0, 6);

  return (
    <section
      className={
        embedded
          ? 'rounded-[28px] border border-[#d7e9f4] bg-[#fafdff] px-4 py-4'
          : 'rounded-3xl border border-[#c9e0ef] bg-white/76 px-5 py-4 shadow-[0_18px_45px_rgba(115,173,214,0.08)] backdrop-blur-md'
      }
    >
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0 xl:max-w-[34%]">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">Progress</p>
            <span className="rounded-full border border-[#b7d8eb] bg-[#f7fbfe] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315770]">
              {REASONING_LABELS[reasoningMode] || 'Model-backed'}
            </span>
          </div>
          <p className="mt-2 text-sm leading-6 text-[#4e6c82]">
            {preparedSummary || 'Still gathering the key business, scale, security, and cost signals.'}
          </p>
        </div>

        <div className="xl:w-[240px]">
          <div className="flex items-center justify-between text-sm text-[#41637a]">
            <span>Captured</span>
            <span>
              {filled}/{total}
            </span>
          </div>
          <div className="mt-3 h-2 rounded-full bg-[#dbeef9]">
            <div className="h-2 rounded-full bg-[#58b7ff]" style={{ width: `${(filled / total) * 100}%` }} />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(contextCoverage || {}).map(([key, ready]) => (
              <span
                key={key}
                className={`rounded-full border px-3 py-1 text-[10px] uppercase tracking-[0.18em] ${
                  ready
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                    : 'border-[#d7e9f4] text-[#5f7f97]'
                }`}
              >
                {key}
              </span>
            ))}
          </div>
        </div>

        <div className="xl:max-w-[42%]">
          <div className="text-[10px] uppercase tracking-[0.18em] text-[#6b8ba2]">Captured so far</div>
          {entries.length === 0 ? (
            <div className="mt-2 text-sm text-[#5f7f97]">Requirement signals will appear here as the conversation progresses.</div>
          ) : (
            <div className="mt-3 flex flex-wrap gap-2">
              {entries.map(([key, value]) => (
                <span key={key} className="rounded-full border border-[#d7e9f4] bg-[#f8fcff] px-3 py-1.5 text-xs text-[#35566c]">
                  <span className="font-semibold text-[#16324a]">{LABELS[key] || key}:</span> {String(value)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
