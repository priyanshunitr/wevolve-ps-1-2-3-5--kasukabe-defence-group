import React from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

interface SkillBadgeProps {
  skill: string;
  variant?: 'default' | 'matched' | 'missing' | 'lowConfidence';
  onRemove?: () => void;
  confidence?: number;
}

const SkillBadge: React.FC<SkillBadgeProps> = ({
  skill,
  variant = 'default',
  onRemove,
  confidence
}) => {
  const variants = {
    default: 'bg-secondary text-secondary-foreground',
    matched: 'bg-success/20 text-success border border-success/30',
    missing: 'bg-destructive/20 text-destructive border border-destructive/30',
    lowConfidence: 'bg-warning/20 text-warning-foreground border border-warning/50'
  };

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.05 }}
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium transition-all ${variants[variant]}`}
    >
      {skill}
      {confidence !== undefined && (
        <span className="text-xs opacity-70">({confidence}%)</span>
      )}
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-1 p-0.5 rounded-full hover:bg-foreground/10 transition-colors"
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </motion.span>
  );
};

export default SkillBadge;
