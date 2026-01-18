"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  X,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Trophy,
  Target,
  BookOpen,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Job } from "@/data/mockData";
import MatchScoreRing from "@/components/common/MatchScoreRing";

interface JobRoadmapPopupProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export default function JobRoadmapPopup({
  job,
  isOpen,
  onClose,
}: JobRoadmapPopupProps) {
  // Generate a mock roadmap based on missing skills if not provided by backend
  const missingSkills = job.missingSkills || [];

  const roadmapSteps = missingSkills.map((skill, index) => {
    // Determine difficulty and time based on skill name or random for variety
    const isHard = skill.length > 8;
    const isMedium = skill.length > 5 && skill.length <= 8;

    return {
      skill,
      difficulty: isHard ? "Hard" : isMedium ? "Medium" : "Easy",
      weeks: isHard ? 4 : isMedium ? 2 : 1,
      order: index + 1,
    };
  });

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto p-0 border-none bg-background/95 backdrop-blur-xl">
        <div className="relative">
          {/* Header Banner */}
          <div className="h-32 bg-gradient-to-r from-primary/20 via-primary/10 to-transparent relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-white/5" />
            <div className="absolute bottom-0 left-0 w-full h-px bg-border/50" />
          </div>

          <div className="px-6 pb-8 -mt-12 relative">
            <div className="flex flex-col md:flex-row gap-6 items-start">
              {/* Score Section */}
              <div className="bg-background border border-border rounded-2xl p-4 shadow-xl">
                <MatchScoreRing score={job.matchScore} size="lg" />
              </div>

              {/* Title Section */}
              <div className="flex-1 pt-12 md:pt-14">
                <div className="flex items-center gap-2 mb-2">
                  <Badge
                    variant="outline"
                    className="bg-primary/5 border-primary/20 text-primary"
                  >
                    Personalized Growth Path
                  </Badge>
                  {job.matchScore >= 80 && (
                    <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                      High Potential
                    </Badge>
                  )}
                </div>
                <h2 className="text-3xl font-bold tracking-tight">
                  {job.title}
                </h2>
                <p className="text-muted-foreground text-lg">
                  at{" "}
                  <span className="text-foreground font-medium">
                    {job.company}
                  </span>{" "}
                  • {job.location}
                </p>
              </div>
            </div>

            {/* Strategic Advice */}
            <div className="mt-8 grid md:grid-cols-2 gap-4">
              <div className="bg-primary/5 rounded-2xl p-5 border border-primary/10">
                <div className="flex items-center gap-2 mb-3 text-primary">
                  <Target className="w-5 h-5" />
                  <h3 className="font-semibold">Match Insight</h3>
                </div>
                <p className="text-sm leading-relaxed">
                  {job.explanation ||
                    job.topReason ||
                    "Your profile strongly aligns with the core requirements of this role."}
                </p>
              </div>
              <div className="bg-secondary/20 rounded-2xl p-5 border border-border">
                <div className="flex items-center gap-2 mb-3 text-foreground">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  <h3 className="font-semibold">Strategic Focus</h3>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {job.topImprovement ||
                    "Focus on mastering the required tech stack to increase your match score to 90% or higher."}
                </p>
              </div>
            </div>

            {/* Missing Skills Section */}
            {missingSkills.length > 0 && (
              <div className="mt-10">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-primary" />
                  Skill Gaps to Bridge
                </h3>
                <div className="flex flex-wrap gap-2">
                  {missingSkills.map((skill) => (
                    <Badge
                      key={skill}
                      variant="secondary"
                      className="px-3 py-1 text-sm bg-muted/50 border-border/50 hover:bg-muted transition-colors"
                    >
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Roadmap Timeline */}
            <div className="mt-12">
              <h3 className="text-xl font-bold mb-8 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-500" />
                Upskilling Roadmap
              </h3>

              <div className="space-y-6">
                {roadmapSteps.length > 0 ? (
                  roadmapSteps.map((step, idx) => (
                    <motion.div
                      key={step.skill}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="flex gap-4 group"
                    >
                      <div className="flex flex-col items-center">
                        <div className="w-10 h-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-primary group-hover:bg-primary group-hover:text-white transition-all duration-300">
                          {step.order}
                        </div>
                        {idx < roadmapSteps.length - 1 && (
                          <div className="w-px h-full bg-border my-2" />
                        )}
                      </div>

                      <div className="flex-1 bg-card border border-border rounded-xl p-5 group-hover:border-primary/30 transition-all duration-300">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-bold text-lg">
                            {step.skill} Mastery
                          </h4>
                          <span
                            className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                              step.difficulty === "Easy"
                                ? "bg-emerald-500/10 text-emerald-500"
                                : step.difficulty === "Medium"
                                ? "bg-amber-500/10 text-amber-500"
                                : "bg-rose-500/10 text-rose-500"
                            }`}
                          >
                            {step.difficulty}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">
                          Comprehensive training on {step.skill} best practices,
                          architecture, and real-world application.
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />~{step.weeks}{" "}
                              weeks
                            </span>
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              Project included
                            </span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-xs font-semibold hover:bg-primary/10 hover:text-primary transition-all"
                          >
                            View Resources
                            <ArrowRight className="w-3.5 h-3.5 ml-1" />
                          </Button>
                        </div>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center py-12 text-center bg-emerald-500/5 border border-dashed border-emerald-500/20 rounded-3xl"
                  >
                    <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mb-4">
                      <Trophy className="w-8 h-8 text-emerald-500" />
                    </div>
                    <h4 className="text-xl font-bold text-emerald-500 mb-2">
                      Perfect Skill Match!
                    </h4>
                    <p className="text-muted-foreground max-w-sm">
                      Your expertise exactly matches the requirements for this
                      position. You're ready to apply!
                    </p>
                    <Button className="mt-6 bg-emerald-600 hover:bg-emerald-700 shadow-xl shadow-emerald-600/20">
                      Apply Now
                    </Button>
                  </motion.div>
                )}
              </div>
            </div>

            {/* Final Action Button */}
            <div className="mt-12 flex justify-center">
              <Button
                size="lg"
                className="rounded-full px-12 font-bold shadow-xl shadow-primary/20 hover:scale-105 transition-transform"
              >
                Start My Learning Journey
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
