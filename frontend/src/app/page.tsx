"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Upload,
  Target,
  Briefcase,
  ArrowRight,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Layout from "@/components/layout/Layout";
import SplineBg from "@/components/3d/splinebg";

const features = [
  {
    icon: Upload,
    title: "Smart Resume Parsing",
    description:
      "AI-powered extraction with confidence scoring for accurate data capture",
  },
  {
    icon: Target,
    title: "Skills Gap Analysis",
    description:
      "Compare your skills against target roles with personalized learning paths",
  },
  {
    icon: Briefcase,
    title: "Dynamic Job Discovery",
    description:
      "Find perfectly matched opportunities with smart filtering and match scoring",
  },
];

const steps = [
  { number: "01", title: "Upload Resume", description: "PDF or DOCX format" },
  { number: "02", title: "Verify & Edit", description: "Review parsed data" },
  { number: "03", title: "Analyze Gaps", description: "Find missing skills" },
  { number: "04", title: "Discover Jobs", description: "Get matched roles" },
];

export default function Home() {
  return (
    <Layout>
      {/* Hero Section */}
      <section className=" w-full relative min-h-[90vh] flex items-center overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <SplineBg />
        </div>

        <div className="container mx-auto px-4 py-20 relative z-10 pointer-events-none">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight"
            >
              Wevolve Your AI Career Co-Pilot

            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto"
            >
              Navigate your career journey with intelligent resume analysis,
              personalized skill gap insights, and dynamic job matching.
            </motion.p>


          </div>
        </div>
        <div className="absolute"
          style={{
            left: "50%",
            bottom: "20%",
            transform: "translateX(-50%) translateY(60%)",
          }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center pointer-events-auto"
          >
            <Link href="/upload">
              <Button
                size="lg"
                className="w-full sm:w-auto text-base px-8 py-6 rounded-xl group"
              >
                Upload Your Resume
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/jobs">
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto text-base px-8 py-6 rounded-xl"
              >
                Explore Jobs
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-card">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powerful Career Tools
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Everything you need to accelerate your career journey
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="p-8 rounded-2xl bg-background border border-border shadow-lg hover:shadow-xl transition-all"
              >
                <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mb-6">
                  <feature.icon className="w-7 h-7 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Four simple steps to your dream career
            </p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-6">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                <div className="text-center p-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-4">
                    {step.number}
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {step.description}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2">
                    <ArrowRight className="w-6 h-6 text-muted" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-primary/5">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="max-w-3xl mx-auto text-center"
          >
            <div className="inline-flex items-center gap-2 text-primary mb-4">
              <CheckCircle2 className="w-5 h-5" />
              <span className="text-sm font-medium">
                Free to use, no credit card required
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Accelerate Your Career?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Start your journey today with AI-powered insights and job
              matching.
            </p>
            <Link href="/upload">
              <Button size="lg" className="text-base px-10 py-6 rounded-xl">
                Get Started Now
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p className="text-sm">
            Built with ❤️ by Kasukabe Defence Group.
          </p>
        </div>
      </footer>
    </Layout>
  );
}
