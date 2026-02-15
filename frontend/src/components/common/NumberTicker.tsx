import { useState, useEffect, useRef } from 'react';

interface NumberTickerProps {
  value: number | string;
  duration?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  compact?: boolean; // 1.2M, 1.5K
  className?: string;
}

function easeOutQuart(t: number): number {
  return 1 - Math.pow(1 - t, 4);
}

export function NumberTicker({
  value,
  duration = 1200,
  prefix = '',
  suffix = '',
  decimals = 0,
  compact = false,
  className = ''
}: NumberTickerProps) {
  const isNumeric = typeof value === 'number';
  const numericValue = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.-]/g, '')) || 0 : value;
  const [displayValue, setDisplayValue] = useState(isNumeric ? 0 : numericValue);
  const startRef = useRef(isNumeric ? 0 : numericValue);
  const startTimeRef = useRef<number | null>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    if (!isNumeric) return;
    const target = value as number;
    startRef.current = displayValue;
    startTimeRef.current = null;

    const tick = (timestamp: number) => {
      if (startTimeRef.current === null) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutQuart(progress);
      setDisplayValue(startRef.current + (target - startRef.current) * eased);
      if (progress < 1) rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [isNumeric, value, duration]);

  const formatDisplay = (n: number) => {
    if (compact && Math.abs(n) >= 1000) {
      if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(1);
      if (Math.abs(n) >= 1_000) return (n / 1_000).toFixed(1);
    }
    return n.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  /* Non-numeric strings (e.g. date range) – show as-is, no animation */
  if (typeof value === 'string') {
    return <span className={className}>{prefix}{value}{suffix}</span>;
  }

  const display = formatDisplay(displayValue);
  const compactSuffix = compact && Math.abs(numericValue) >= 1_000_000
    ? 'M'
    : compact && Math.abs(numericValue) >= 1_000
    ? 'K'
    : '';

  return (
    <span className={className}>
      {prefix}{display}{compactSuffix || suffix}
    </span>
  );
}
