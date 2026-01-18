import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: number;
  showIcon?: boolean;
}

const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  showIcon = true
}) => {
  const isLow = confidence < 70;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium ${
        isLow
          ? 'bg-warning/20 text-warning-foreground'
          : 'bg-success/20 text-success'
      }`}
    >
      {showIcon && (
        isLow ? (
          <AlertCircle className="w-3 h-3" />
        ) : (
          <CheckCircle2 className="w-3 h-3" />
        )
      )}
      <span>{confidence}%</span>
      {isLow && <span className="hidden sm:inline">- Review Required</span>}
    </motion.div>
  );
};

export default ConfidenceBadge;
