"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sparkles,
  Target,
  TrendingUp,
  BrainCircuit,
  ShieldCheck,
} from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const features = [
    {
      icon: TrendingUp,
      text: "Accelerate your career trajectory with data-driven insights",
    },
    {
      icon: BrainCircuit,
      text: "AI-powered skill gap analysis and personalized learning",
    },
    {
      icon: Target,
      text: "Smart job matching that fits your unique profile",
    },
    {
      icon: ShieldCheck,
      text: "Private and secure resume parsing technology",
    },
  ];

  return (
    <div className="min-h-screen w-full flex bg-background text-foreground overflow-hidden">
      {/* Left Side - Brand & Features */}
      <div className="hidden lg:flex w-1/2 bg-zinc-900 relative items-center justify-center p-12 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
          <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] bg-primary/20 rounded-full blur-[120px]" />
          <div className="absolute bottom-[-20%] right-[-20%] w-[80%] h-[80%] bg-purple-600/20 rounded-full blur-[120px]" />
        </div>

        <div className="relative z-10 max-w-lg">
          <Link href="/" className="inline-flex items-center gap-2 mb-12 group">
            <div className="p-2 rounded-xl bg-primary/20 backdrop-blur-sm border border-primary/20 group-hover:bg-primary/30 transition-colors">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">
              Wevolve
            </span>
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
              Join the Future of <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">
                Career Growth
              </span>
            </h1>
            <p className="text-zinc-400 text-lg mb-12 leading-relaxed">
              Create your account to access AI-powered insights, automated
              resume parsing, and precision job matching.
            </p>

            <div className="space-y-6">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
                  className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors"
                >
                  <div className="p-2 rounded-lg bg-primary/20 text-primary">
                    <feature.icon className="w-5 h-5" />
                  </div>
                  <span className="text-zinc-200 font-medium">
                    {feature.text}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Form Container */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 relative">
        <div className="absolute inset-0 bg-background z-0" />
        {children}
      </div>
    </div>
  );
}
