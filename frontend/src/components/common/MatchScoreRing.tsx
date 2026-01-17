import React from 'react';
import { motion } from 'framer-motion';

interface MatchScoreRingProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const MatchScoreRing: React.FC<MatchScoreRingProps> = ({
  score,
  size = 'md',
  showLabel = true
}) => {
  const dimensions = {
    sm: { width: 48, strokeWidth: 4, fontSize: 'text-xs' },
    md: { width: 64, strokeWidth: 5, fontSize: 'text-sm' },
    lg: { width: 96, strokeWidth: 6, fontSize: 'text-lg' }
  };

  const { width, strokeWidth, fontSize } = dimensions[size];
  const radius = (width - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((100 - score) / 100) * circumference;

  const getColor = () => {
    if (score >= 80) return 'hsl(var(--success))';
    if (score >= 60) return 'hsl(var(--warning))';
    return 'hsl(var(--destructive))';
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={width} height={width} className="-rotate-90">
        <circle
          cx={width / 2}
          cy={width / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
          className="opacity-30"
        />
        <motion.circle
          cx={width / 2}
          cy={width / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: progress }}
          transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
          className={`font-bold ${fontSize} text-foreground`}
        >
          {score}%
        </motion.span>
        {showLabel && size !== 'sm' && (
          <span className="text-xs text-muted-foreground">Match</span>
        )}
      </div>
    </div>
  );
};

export default MatchScoreRing;
