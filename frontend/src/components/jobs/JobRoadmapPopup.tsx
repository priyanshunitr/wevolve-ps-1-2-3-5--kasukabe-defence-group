"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  CheckCircle2,
  Clock,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Trophy,
  Target,
  BookOpen,
  Play,
  Star,
  Zap,
  GraduationCap,
  Code,
  ExternalLink,
  ChevronRight,
  Rocket,
  Award,
  TrendingUp,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Job } from "@/data/mockData";
import { skillTaxonomy } from "@/data/mockData";
import MatchScoreRing from "@/components/common/MatchScoreRing";

interface JobRoadmapPopupProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

interface LearningResource {
  type: "course" | "project" | "article" | "video";
  title: string;
  provider: string;
  duration: string;
  link?: string;
}

interface RoadmapStep {
  skill: string;
  difficulty: "Easy" | "Medium" | "Hard";
  weeks: number;
  order: number;
  category: string;
  resources: LearningResource[];
  milestones: string[];
}

// Generate learning resources for a skill
function generateResources(skill: string): LearningResource[] {
  const encodedSkill = encodeURIComponent(skill);
  const resources: LearningResource[] = [
    {
      type: "course",
      title: `Complete ${skill} Masterclass`,
      provider: "Udemy",
      duration: "20 hours",
      link: `https://www.udemy.com/courses/search/?q=${encodedSkill}`,
    },
    {
      type: "video",
      title: `${skill} Crash Course`,
      provider: "YouTube",
      duration: "2 hours",
      link: `https://www.youtube.com/results?search_query=${encodedSkill}+tutorial`,
    },
    {
      type: "project",
      title: `Build a ${skill} Project`,
      provider: "GitHub",
      duration: "10 hours",
      link: `https://github.com/topics/${encodedSkill.toLowerCase()}`,
    },
    {
      type: "article",
      title: `${skill} Best Practices Guide`,
      provider: "Google",
      duration: "30 mins",
      link: `https://www.google.com/search?q=${encodedSkill}+best+practices+guide`,
    },
  ];
  return resources;
}

// Generate milestones for a skill
function generateMilestones(skill: string): string[] {
  return [
    `Understand ${skill} fundamentals and core concepts`,
    `Complete hands-on exercises and tutorials`,
    `Build a mini-project using ${skill}`,
    `Apply ${skill} in a real-world scenario`,
  ];
}

export default function JobRoadmapPopup({
  job,
  isOpen,
  onClose,
}: JobRoadmapPopupProps) {
  const [showLearningPath, setShowLearningPath] = useState(false);
  const [activeSkillIndex, setActiveSkillIndex] = useState(0);

  const missingSkills = job.missingSkills || [];

  const roadmapSteps: RoadmapStep[] = missingSkills.map((skill, index) => {
    const taxonomy = skillTaxonomy[skill];
    const difficulty = taxonomy?.difficulty || (skill.length > 8 ? "Hard" : skill.length > 5 ? "Medium" : "Easy");
    const weeks = taxonomy?.learningTimeMonths ? taxonomy.learningTimeMonths * 4 : (difficulty === "Hard" ? 4 : difficulty === "Medium" ? 2 : 1);

    return {
      skill,
      difficulty,
      weeks,
      order: index + 1,
      category: taxonomy?.category || "General",
      resources: generateResources(skill),
      milestones: generateMilestones(skill),
    };
  });

  const totalWeeks = roadmapSteps.reduce((acc, step) => acc + step.weeks, 0);
  const totalMonths = Math.ceil(totalWeeks / 4);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Easy":
        return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
      case "Medium":
        return "bg-amber-500/10 text-amber-500 border-amber-500/20";
      case "Hard":
        return "bg-rose-500/10 text-rose-500 border-rose-500/20";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getResourceIcon = (type: string) => {
    switch (type) {
      case "course":
        return <GraduationCap className="w-4 h-4" />;
      case "video":
        return <Play className="w-4 h-4" />;
      case "project":
        return <Code className="w-4 h-4" />;
      case "article":
        return <BookOpen className="w-4 h-4" />;
      default:
        return <Star className="w-4 h-4" />;
    }
  };

  // Learning Path View
  if (showLearningPath && roadmapSteps.length > 0) {
    const activeStep = roadmapSteps[activeSkillIndex];

    return (
      <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
        <DialogContent className="max-w-5xl max-h-[95vh] overflow-hidden p-0 border-none bg-background">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary/20 via-primary/10 to-transparent p-6 border-b border-border/50">
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLearningPath(false)}
                className="gap-2 hover:bg-background/50"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Overview
              </Button>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-background/50">
                  <Clock className="w-3 h-3 mr-1" />
                  {totalMonths} months total
                </Badge>
                <Badge variant="outline" className="bg-background/50">
                  <Target className="w-3 h-3 mr-1" />
                  {roadmapSteps.length} skills
                </Badge>
              </div>
            </div>
            <div className="mt-4">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Rocket className="w-6 h-6 text-primary" />
                Your Learning Journey to {job.title}
              </h2>
              <p className="text-muted-foreground mt-1">
                Master these skills to reach 100% match score
              </p>
            </div>
          </div>

          <div className="flex h-[calc(95vh-180px)]">
            {/* Sidebar - Skills Timeline */}
            <div className="w-72 border-r border-border bg-muted/20 overflow-y-auto p-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Learning Path
              </h3>
              <div className="space-y-2">
                {roadmapSteps.map((step, idx) => (
                  <motion.button
                    key={step.skill}
                    onClick={() => setActiveSkillIndex(idx)}
                    className={`w-full text-left p-3 rounded-xl transition-all ${activeSkillIndex === idx
                      ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                      : "bg-card hover:bg-muted border border-border hover:border-primary/30"
                      }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${activeSkillIndex === idx
                        ? "bg-white/20"
                        : "bg-primary/10 text-primary"
                        }`}>
                        {step.order}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{step.skill}</p>
                        <div className="flex items-center gap-2 text-xs opacity-70">
                          <Clock className="w-3 h-3" />
                          {step.weeks} weeks
                        </div>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Progress Summary */}
              <div className="mt-6 p-4 bg-gradient-to-br from-primary/10 to-transparent rounded-xl border border-primary/20">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-5 h-5 text-primary" />
                  <span className="font-semibold">Completion Reward</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Upon completing this learning path, you'll be a perfect match for this role!
                </p>
              </div>
            </div>

            {/* Main Content - Active Skill Details */}
            <div className="flex-1 overflow-y-auto p-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeStep.skill}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Skill Header */}
                  <div className="flex items-start justify-between mb-8">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <Badge className={`${getDifficultyColor(activeStep.difficulty)} border`}>
                          {activeStep.difficulty}
                        </Badge>
                        <Badge variant="outline">{activeStep.category}</Badge>
                      </div>
                      <h3 className="text-3xl font-bold">{activeStep.skill}</h3>
                      <p className="text-muted-foreground mt-2">
                        Master {activeStep.skill} fundamentals and advanced concepts
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-primary">{activeStep.weeks}</div>
                      <div className="text-sm text-muted-foreground">weeks</div>
                    </div>
                  </div>

                  {/* Milestones */}
                  <div className="mb-8">
                    <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Target className="w-5 h-5 text-primary" />
                      Learning Milestones
                    </h4>
                    <div className="grid gap-3">
                      {activeStep.milestones.map((milestone, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex items-start gap-3 p-4 bg-card rounded-xl border border-border hover:border-primary/30 transition-colors"
                        >
                          <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <CheckCircle2 className="w-4 h-4 text-primary" />
                          </div>
                          <span>{milestone}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Resources */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-primary" />
                      Recommended Resources
                    </h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {activeStep.resources.map((resource, idx) => (
                        <motion.a
                          key={idx}
                          href={resource.link || "#"}
                          target="_blank"
                          rel="noopener noreferrer"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="group p-4 bg-card rounded-xl border border-border hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer block"
                        >
                          <div className="flex items-start gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${resource.type === "course" ? "bg-blue-500/10 text-blue-500" :
                              resource.type === "video" ? "bg-red-500/10 text-red-500" :
                                resource.type === "project" ? "bg-emerald-500/10 text-emerald-500" :
                                  "bg-amber-500/10 text-amber-500"
                              }`}>
                              {getResourceIcon(resource.type)}
                            </div>
                            <div className="flex-1">
                              <p className="font-medium group-hover:text-primary transition-colors">
                                {resource.title}
                              </p>
                              <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                                <span>{resource.provider}</span>
                                <span>•</span>
                                <span>{resource.duration}</span>
                              </div>
                            </div>
                            <ExternalLink className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </motion.a>
                      ))}
                    </div>
                  </div>

                  {/* Navigation */}
                  <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
                    <Button
                      variant="outline"
                      onClick={() => setActiveSkillIndex(Math.max(0, activeSkillIndex - 1))}
                      disabled={activeSkillIndex === 0}
                      className="gap-2"
                    >
                      <ArrowLeft className="w-4 h-4" />
                      Previous Skill
                    </Button>

                    {activeSkillIndex < roadmapSteps.length - 1 ? (
                      <Button
                        onClick={() => setActiveSkillIndex(activeSkillIndex + 1)}
                        className="gap-2"
                      >
                        Next Skill
                        <ArrowRight className="w-4 h-4" />
                      </Button>
                    ) : (
                      <Button className="gap-2 bg-emerald-600 hover:bg-emerald-700">
                        <Trophy className="w-4 h-4" />
                        Complete Journey
                      </Button>
                    )}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Default Overview View
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

            {/* Roadmap Preview */}
            <div className="mt-12">
              <h3 className="text-xl font-bold mb-8 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-500" />
                Upskilling Roadmap
              </h3>

              <div className="space-y-6">
                {roadmapSteps.length > 0 ? (
                  <>
                    {roadmapSteps.slice(0, 3).map((step, idx) => (
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
                          {idx < Math.min(roadmapSteps.length - 1, 2) && (
                            <div className="w-px h-full bg-border my-2" />
                          )}
                        </div>

                        <div className="flex-1 bg-card border border-border rounded-xl p-5 group-hover:border-primary/30 transition-all duration-300">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-lg">
                              {step.skill} Mastery
                            </h4>
                            <span
                              className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${getDifficultyColor(step.difficulty)}`}
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
                          </div>
                        </div>
                      </motion.div>
                    ))}

                    {roadmapSteps.length > 3 && (
                      <div className="flex items-center gap-4 text-muted-foreground">
                        <div className="w-10 flex justify-center">
                          <div className="w-2 h-2 rounded-full bg-border" />
                        </div>
                        <p className="text-sm">
                          +{roadmapSteps.length - 3} more skills in your learning path
                        </p>
                      </div>
                    )}
                  </>
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
            {roadmapSteps.length > 0 && (
              <div className="mt-12 flex justify-center">
                <Button
                  size="lg"
                  onClick={() => setShowLearningPath(true)}
                  className="rounded-full px-12 font-bold shadow-xl shadow-primary/20 hover:scale-105 transition-transform gap-2"
                >
                  <Rocket className="w-5 h-5" />
                  Start My Learning Journey
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
