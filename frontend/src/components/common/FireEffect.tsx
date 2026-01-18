"use client";

import React from 'react';
import { motion } from 'framer-motion';

interface FireEffectProps {
    children: React.ReactNode;
    active?: boolean;
    intensity?: 'low' | 'medium' | 'high';
    className?: string;
}

/**
 * Ember border effect for low-confidence fields
 * Simple animated glowing border that pulses with ember colors
 */
export default function FireEffect({
    children,
    active = true,
    intensity = 'medium',
    className = ''
}: FireEffectProps) {
    if (!active) {
        return <>{children}</>;
    }

    const intensityConfig = {
        low: { glowSize: 4, duration: 3 },
        medium: { glowSize: 6, duration: 2.5 },
        high: { glowSize: 8, duration: 2 },
    };

    const config = intensityConfig[intensity];

    return (
        <div className={`relative ${className}`}>
            {/* Animated ember border glow */}
            <motion.div
                className="absolute -inset-[1px] rounded-xl pointer-events-none"
                style={{
                    background: 'linear-gradient(90deg, #ff6b35, #f7931e, #ff4444, #ff6b35)',
                    backgroundSize: '300% 100%',
                }}
                animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                }}
                transition={{
                    duration: config.duration,
                    repeat: Infinity,
                    ease: 'linear',
                }}
            />

            {/* Pulsing outer glow */}
            <motion.div
                className="absolute rounded-xl pointer-events-none"
                style={{
                    inset: -config.glowSize,
                    boxShadow: `0 0 ${config.glowSize * 2}px rgba(255, 107, 53, 0.5), 0 0 ${config.glowSize * 4}px rgba(247, 147, 30, 0.3)`,
                }}
                animate={{
                    opacity: [0.5, 1, 0.5],
                }}
                transition={{
                    duration: config.duration,
                    repeat: Infinity,
                    ease: 'easeInOut',
                }}
            />

            {/* Content container - masks out the center of the gradient */}
            <div className="relative z-10 rounded-xl bg-card">
                {children}
            </div>
        </div>
    );
}
