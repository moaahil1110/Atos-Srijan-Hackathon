export default function FullScreenLoader({
  title = 'Loading Nimbus',
  description = 'Preparing your secure workspace...',
}) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-transparent px-6 text-center text-[#14324a]">
      <div className="max-w-md">
        <div className="loader mx-auto mb-5 h-12 w-12 rounded-full border-4 border-[rgba(88,183,255,0.2)] border-t-[#58b7ff]" />
        <p className="mb-2 text-sm font-semibold uppercase tracking-[0.32em] text-[#2792df]">
          Nimbus
        </p>
        <h1 className="text-2xl font-semibold text-[#14324a]">{title}</h1>
        <p className="mt-3 text-sm leading-6 text-[#6f8ea5]">{description}</p>
      </div>
    </div>
  );
}
