/**
 * Fintech-style 3D stacked blocks with glowing accents.
 * Matches dashboard electric/indigo color scheme. Use on Insights and Login.
 */
export function Fintech3D({ className = '' }: { className?: string }) {
  return (
    <div
      className={`fintech-3d-root flex flex-col items-center justify-center gap-1 ${className}`}
      aria-hidden
    >
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="fintech-3d-block relative w-24 h-16 md:w-28 md:h-20 rounded-lg flex items-center justify-center"
        >
          {/* Metallic face */}
          <div className="absolute inset-0 rounded-lg fintech-3d-face" />
          {/* Two glowing "screens" */}
          <div className="flex gap-2 relative z-10">
            <div className="w-6 h-4 md:w-7 md:h-5 rounded-sm fintech-3d-glow" />
            <div className="w-6 h-4 md:w-7 md:h-5 rounded-sm fintech-3d-glow" />
          </div>
        </div>
      ))}
    </div>
  );
}
