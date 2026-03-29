interface SnipLogoProps {
  size?: number
  className?: string
}

export function SnipLogo({ size = 24, className }: SnipLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Left blade */}
      <path
        d="M4 4L11 11"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      {/* Right blade */}
      <path
        d="M4 20L11 13"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      {/* Pivot point */}
      <circle cx="11.5" cy="12" r="1.5" fill="currentColor" />
      {/* Cut line (the snipped link) */}
      <path
        d="M15 8L20 4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="2 3"
      />
      <path
        d="M15 16L20 20"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="2 3"
      />
    </svg>
  )
}
