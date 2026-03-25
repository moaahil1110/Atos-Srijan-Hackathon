export default function AuthShell({
  children,
  badge = null,
  title,
  description,
  heroTitle = 'Cloud architecture, with a clearer horizon.',
  heroCopy = 'Nimbus turns ambiguous business intent into secure, explainable cloud decisions without making the interface feel heavy.',
}) {
  return (
    <div className="flex min-h-screen w-full flex-col bg-transparent font-display text-[#49697f] lg:flex-row">
      <div className="flex w-full items-center justify-center bg-[linear-gradient(180deg,rgba(255,255,255,0.72),rgba(241,250,255,0.94))] p-7 md:p-9 lg:w-1/2 lg:p-12">
        <div className="w-full max-w-md lg:max-w-lg">
          <div className="mb-8">
            {badge ? (
              <span className="inline-flex items-center rounded-full border border-[rgba(88,183,255,0.2)] bg-[rgba(88,183,255,0.12)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.28em] text-[#228bda]">
                {badge}
              </span>
            ) : null}
            {title ? <h1 className="mt-5 text-3xl font-bold text-[#14324a] sm:text-4xl">{title}</h1> : null}
            {description ? <p className="mt-2 text-sm leading-6 text-[#67879d] sm:text-base">{description}</p> : null}
          </div>

          {children}
        </div>
      </div>

      <div className="relative hidden overflow-hidden lg:block lg:w-1/2">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 h-full w-full object-cover"
        >
          <source src="/nimbus.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(244,251,255,0.18),rgba(20,50,74,0.24),rgba(244,251,255,0.12))]" />
        <div className="absolute inset-x-0 bottom-0 h-64 bg-[linear-gradient(180deg,transparent,rgba(7,41,70,0.55))]" />
        <div className="absolute bottom-10 left-10 max-w-xl rounded-[28px] border border-white/25 bg-white/18 p-8 text-white backdrop-blur-md">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[#dff5ff]">Nimbus</p>
          <h2 className="mt-4 text-3xl font-semibold leading-tight">{heroTitle}</h2>
          <p className="mt-4 text-sm leading-7 text-[#eef9ff]">{heroCopy}</p>
        </div>
        <div className="absolute top-8 right-8 h-24 w-24 rounded-full bg-sky-200/30 blur-2xl" />
        <div className="absolute bottom-12 left-12 h-36 w-36 rounded-full bg-white/20 blur-3xl" />
      </div>
    </div>
  );
}
