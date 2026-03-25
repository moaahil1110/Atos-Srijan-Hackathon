export default function FullScreenLoader({
  title = 'Loading Nimbus',
  description = 'Preparing your secure workspace...',
}) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-[#0E0C09] px-6 text-center text-white">
      <div className="max-w-md">
        <div className="mx-auto mb-5 h-12 w-12 rounded-full border-4 border-[rgba(255,193,7,0.2)] border-t-[#FFC107] loader" />
        <p className="mb-2 text-sm font-semibold uppercase tracking-[0.32em] text-[#FFC107]">
          Nimbus
        </p>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        <p className="mt-3 text-sm leading-6 text-[#B7AEA2]">{description}</p>
      </div>
    </div>
  );
}
