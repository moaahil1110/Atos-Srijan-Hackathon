export default function AuthShell({
  children,
  badge = null,
  title,
  description,
}) {
  return (
    <div className="flex min-h-screen w-full flex-col bg-[#0E0C09] font-display text-gray-300 lg:flex-row">
      <div className="flex w-full items-center justify-center bg-[#0E0C09] p-7 md:p-9 lg:w-1/2 lg:p-12">
        <div className="w-full max-w-md lg:max-w-lg">
          <div className="mb-8">
            {badge ? (
              <span className="inline-flex items-center rounded-full border border-[rgba(255,193,7,0.18)] bg-[rgba(255,193,7,0.08)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.28em] text-[#FFC107]">
                {badge}
              </span>
            ) : null}
            {title ? <h1 className="mt-5 text-3xl font-bold text-white sm:text-4xl">{title}</h1> : null}
            {description ? <p className="mt-2 text-sm leading-6 text-gray-400 sm:text-base">{description}</p> : null}
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
          <source src="/hero.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="absolute inset-0 bg-gradient-to-br from-[#0E0C09]/90 via-black/40 to-transparent" />
        <div className="absolute top-8 right-8 h-20 w-20 rounded-full bg-yellow-400/10 blur-2xl" />
        <div className="absolute bottom-12 left-12 h-32 w-32 rounded-full bg-primary/5 blur-3xl" />
      </div>
    </div>
  );
}
