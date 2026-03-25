import { useEffect, useState } from 'react';

const SERVICE_DESCRIPTIONS = {
  S3: 'Object storage',
  RDS: 'Relational database',
  IAM: 'Identity and access',
  EC2: 'Virtual machines',
  Lambda: 'Serverless',
  CloudFront: 'Content delivery',
  'Blob Storage': 'Object storage',
  'Azure Database for PostgreSQL': 'Relational database',
  'Azure Active Directory': 'Identity and access',
  'Virtual Machines': 'Virtual machines',
  'Azure Functions': 'Serverless',
  'Azure CDN': 'Content delivery',
  'Cloud Storage': 'Object storage',
  'Cloud SQL': 'Relational database',
  'Cloud IAM': 'Identity and access',
  'Compute Engine': 'Virtual machines',
  'Cloud Functions': 'Serverless',
  'Cloud CDN': 'Content delivery',
};

const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

export default function IntakePanel({
  provider,
  session,
  selectedServices,
  setSelectedServices,
  onProviderChange,
  onAnalyze,
  onConfigureSelected,
  isAnalyzing,
  isConfiguring,
}) {
  const [description, setDescription] = useState(
    'Healthcare startup storing patient records. HIPAA in-progress. Using S3 and RDS. Security non-negotiable.',
  );
  const [customService, setCustomService] = useState('');

  useEffect(() => {
    if (session?.suggestedServices) {
      setSelectedServices(session.suggestedServices);
    }
  }, [session, setSelectedServices]);

  const toggleService = (service) => {
    setSelectedServices((current) =>
      current.includes(service)
        ? current.filter((item) => item !== service)
        : [...current, service],
    );
  };

  const addCustomService = () => {
    const nextValue = customService.trim();
    if (!nextValue || selectedServices.includes(nextValue)) {
      return;
    }
    setSelectedServices((current) => [...current, nextValue]);
    setCustomService('');
  };

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">
          Provider
        </p>
        <div className="mt-4 grid grid-cols-3 gap-3">
          {[
            ['aws', 'AWS'],
            ['azure', 'Azure'],
            ['gcp', 'GCP'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => onProviderChange(value)}
              className={`rounded-2xl border px-4 py-3 text-sm transition-colors ${
                provider === value
                  ? 'border-[#a9d8f4] bg-[#eef8ff] text-[#2792df]'
                  : 'border-[#d7e9f4] bg-transparent text-[#55748b] hover:bg-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">
          Describe The Company
        </p>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="mt-4 h-56 w-full rounded-2xl border border-[#c9e0ef] bg-white/84 p-4 text-sm leading-7 text-[#14324a] placeholder:text-[#88a6bb] focus:border-[#58b7ff] focus:outline-none"
          placeholder="What does the company do, what data is sensitive, and which compliance or cost constraints matter?"
        />
        <button
          type="button"
          onClick={() => onAnalyze(description, provider)}
          disabled={isAnalyzing || !description.trim()}
          className="mt-4 w-full rounded-2xl bg-[#58b7ff] px-4 py-3 text-sm font-semibold text-[#08304d] transition-colors hover:bg-[#7dcaff] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Context'}
        </button>
      </section>

      {session ? (
        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#2792df]">
                Suggested Services
              </p>
              <p className="mt-2 text-sm leading-6 text-[#9F978E]">
                Select only the services you want Nimbus to configure in this run.
              </p>
              <p className="mt-2 text-xs uppercase tracking-[0.18em] text-[#8E857A]">
                Services identified for {PROVIDER_LABELS[provider] || provider.toUpperCase()}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 px-3 py-2 text-xs text-[#C9C1B8]">
              {selectedServices.length} selected
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {session.suggestedServices.map((service) => (
              <label
                key={service}
                className="flex items-center gap-3 rounded-2xl border border-white/10 px-4 py-3 text-sm text-white"
              >
                <input
                  type="checkbox"
                  checked={selectedServices.includes(service)}
                  onChange={() => toggleService(service)}
                />
                <div className="min-w-0">
                  <div className="font-medium">{service}</div>
                  <div className="text-xs text-[#8E857A]">{SERVICE_DESCRIPTIONS[service] || 'Custom service'}</div>
                </div>
              </label>
            ))}

            {selectedServices
              .filter((service) => !session.suggestedServices.includes(service))
              .map((service) => (
                <label
                  key={service}
                  className="flex items-center gap-3 rounded-2xl border border-white/10 px-4 py-3 text-sm text-white"
                >
                  <input
                    type="checkbox"
                    checked={selectedServices.includes(service)}
                    onChange={() => toggleService(service)}
                  />
                  <div className="min-w-0">
                    <div className="font-medium">{service}</div>
                    <div className="text-xs text-[#8E857A]">Custom service</div>
                  </div>
                </label>
              ))}
          </div>

          <div className="mt-4 flex gap-2">
            <input
              type="text"
              value={customService}
              onChange={(event) => setCustomService(event.target.value)}
              className="h-11 flex-1 rounded-2xl border border-[#c9e0ef] bg-white/84 px-4 text-sm text-[#14324a] placeholder:text-[#88a6bb] focus:border-[#58b7ff] focus:outline-none"
              placeholder="Add a custom service"
            />
            <button
              type="button"
              onClick={addCustomService}
              className="rounded-2xl border border-white/10 px-4 py-2 text-sm text-white transition-colors hover:bg-white/[0.05]"
            >
              Add
            </button>
          </div>

          <button
            type="button"
            onClick={onConfigureSelected}
            disabled={isConfiguring || selectedServices.length === 0}
            className="mt-4 w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-black transition-colors hover:bg-[#F3EEE8] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isConfiguring ? 'Configuring Services...' : 'Configure Selected Services'}
          </button>
        </section>
      ) : null}
    </div>
  );
}
