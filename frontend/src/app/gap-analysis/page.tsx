"use client";

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Target, TrendingUp, BookOpen, ChevronDown, ChevronRight, Clock, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Layout from '@/components/layout/Layout';
import SkillBadge from '@/components/common/SkillBadge';
import MatchScoreRing from '@/components/common/MatchScoreRing';
import { useResume, ParsedResumeFrontend } from '@/contexts/ResumeContext';
import { targetRoles, skillTaxonomy } from '@/data/mockData';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts';

// Sample data for when no resume has been parsed
const sampleParsedResume: ParsedResumeFrontend = {
  name: 'Alex Johnson',
  email: 'alex.johnson@email.com',
  phone: '(555) 123-4567',
  skills: [
    { name: 'React', confidence: 95 },
    { name: 'JavaScript', confidence: 92 },
    { name: 'TypeScript', confidence: 88 },
    { name: 'CSS', confidence: 90 },
    { name: 'Node.js', confidence: 75 },
    { name: 'Git', confidence: 85 },
    { name: 'REST APIs', confidence: 82 }
  ],
  experience: [],
  education: [],
  projects: [],
  preferredLocations: [],
  preferredRoles: [],
  expectedSalary: null,
  nameConfidence: 98,
  emailConfidence: 95,
  phoneConfidence: 72,
  yearsOfExperience: 4
};

export default function GapAnalysisPage() {
  const { parsedResume } = useResume();
  const resume = parsedResume || sampleParsedResume;
  const [selectedRoleId, setSelectedRoleId] = useState<string>('senior-frontend');
  const [expandedPhase, setExpandedPhase] = useState<number | null>(0);

  const selectedRole = useMemo(() => {
    return targetRoles.find(r => r.id === selectedRoleId) || targetRoles[0];
  }, [selectedRoleId]);

  const currentSkills = useMemo(() => {
    return resume.skills.map(s => s.name);
  }, [resume]);

  const analysis = useMemo(() => {
    const required = selectedRole.requiredSkills;
    const matched = currentSkills.filter(s => required.includes(s));
    const missing = required.filter(s => !currentSkills.includes(s));

    const gapPercentage = Math.round((missing.length / required.length) * 100);
    const readinessScore = Math.round(100 - gapPercentage);

    return {
      matched,
      missing,
      gapPercentage,
      readinessScore,
      required
    };
  }, [selectedRole, currentSkills]);

  const radarData = useMemo(() => {
    const categories = ['Frontend', 'Backend', 'DevOps', 'Database', 'Soft Skills', 'Architecture'];

    return categories.map(category => {
      const relevantRequired = selectedRole.requiredSkills.filter(
        skill => skillTaxonomy[skill]?.category === category ||
          (category === 'Soft Skills' && ['Communication', 'Team Leadership', 'Agile'].includes(skill))
      );
      const relevantCurrent = currentSkills.filter(
        skill => skillTaxonomy[skill]?.category === category ||
          (category === 'Soft Skills' && ['Communication', 'Team Leadership', 'Agile'].includes(skill))
      );

      return {
        subject: category,
        required: relevantRequired.length > 0 ? 100 : 0,
        current: relevantCurrent.length > 0
          ? Math.min(100, (relevantCurrent.length / Math.max(1, relevantRequired.length)) * 100)
          : (relevantCurrent.length > 0 ? 50 : 0)
      };
    });
  }, [selectedRole, currentSkills]);

  const learningRoadmap = useMemo(() => {
    const phases: {
      title: string;
      skills: string[];
      durationMonths: number;
      priority: 'High' | 'Medium' | 'Low';
    }[] = [];

    const sortedMissing = [...analysis.missing].sort((a, b) => {
      const diffA = skillTaxonomy[a]?.difficulty || 'Medium';
      const diffB = skillTaxonomy[b]?.difficulty || 'Medium';
      const order = { 'Easy': 0, 'Medium': 1, 'Hard': 2 };
      return order[diffA] - order[diffB];
    });

    const easy = sortedMissing.filter(s => skillTaxonomy[s]?.difficulty === 'Easy');
    const medium = sortedMissing.filter(s => skillTaxonomy[s]?.difficulty === 'Medium');
    const hard = sortedMissing.filter(s => skillTaxonomy[s]?.difficulty === 'Hard');

    if (easy.length > 0) {
      phases.push({
        title: 'Quick Wins',
        skills: easy,
        durationMonths: Math.max(...easy.map(s => skillTaxonomy[s]?.learningTimeMonths || 1)),
        priority: 'High'
      });
    }

    if (medium.length > 0) {
      phases.push({
        title: 'Core Skills',
        skills: medium,
        durationMonths: Math.max(...medium.map(s => skillTaxonomy[s]?.learningTimeMonths || 2)),
        priority: 'Medium'
      });
    }

    if (hard.length > 0) {
      phases.push({
        title: 'Advanced Topics',
        skills: hard,
        durationMonths: Math.max(...hard.map(s => skillTaxonomy[s]?.learningTimeMonths || 4)),
        priority: 'Low'
      });
    }

    return phases;
  }, [analysis.missing]);

  return (
    <Layout>
      <div className="py-8">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-10"
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-4">Skills Gap Analysis</h1>
            <p className="text-muted-foreground max-w-xl mx-auto">
              See how your current skills compare to your target role
            </p>
          </motion.div>

          {/* Role Selection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="max-w-md mx-auto mb-12"
          >
            <label className="block text-sm font-medium mb-2">Select Target Role</label>
            <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
              <SelectTrigger className="w-full py-6 rounded-xl">
                <SelectValue placeholder="Choose a role" />
              </SelectTrigger>
              <SelectContent>
                {targetRoles.map((role) => (
                  <SelectItem key={role.id} value={role.id}>
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-primary" />
                      {role.title}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </motion.div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <MatchScoreRing score={analysis.readinessScore} size="lg" />
              <h3 className="font-semibold mt-4">Readiness Score</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Your match for {selectedRole.title}
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <div className="text-5xl font-bold text-primary mb-2">
                {analysis.matched.length}/{analysis.required.length}
              </div>
              <h3 className="font-semibold">Skills Matched</h3>
              <p className="text-sm text-muted-foreground mt-1">
                You have {analysis.matched.length} of {analysis.required.length} required skills
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <div className="text-5xl font-bold text-warning mb-2">
                {analysis.missing.length}
              </div>
              <h3 className="font-semibold">Skills to Learn</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Focus areas for your growth
              </p>
            </motion.div>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Radar Chart */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-card border border-border rounded-2xl p-6"
            >
              <h2 className="font-semibold mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                Skills Comparison
              </h2>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis
                      dataKey="subject"
                      tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
                    />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                    <Radar
                      name="Required"
                      dataKey="required"
                      stroke="hsl(var(--chart-1))"
                      fill="hsl(var(--chart-1))"
                      fillOpacity={0.2}
                    />
                    <Radar
                      name="Your Skills"
                      dataKey="current"
                      stroke="hsl(var(--chart-2))"
                      fill="hsl(var(--chart-2))"
                      fillOpacity={0.4}
                    />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Skills Breakdown */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-card border border-border rounded-2xl p-6"
            >
              <h2 className="font-semibold mb-6">Skills Breakdown</h2>

              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-medium text-success mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-success" />
                    Matched Skills ({analysis.matched.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.matched.map((skill) => (
                      <SkillBadge key={skill} skill={skill} variant="matched" />
                    ))}
                    {analysis.matched.length === 0 && (
                      <p className="text-sm text-muted-foreground">No matched skills yet</p>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-destructive mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-destructive" />
                    Missing Skills ({analysis.missing.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.missing.map((skill) => (
                      <SkillBadge key={skill} skill={skill} variant="missing" />
                    ))}
                    {analysis.missing.length === 0 && (
                      <p className="text-sm text-muted-foreground">You have all required skills!</p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Learning Roadmap */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-card border border-border rounded-2xl p-6"
          >
            <h2 className="font-semibold mb-6 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-primary" />
              Learning Roadmap
            </h2>

            {learningRoadmap.length === 0 ? (
              <div className="text-center py-12">
                <Zap className="w-12 h-12 text-success mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">You're all set!</h3>
                <p className="text-muted-foreground">
                  You already have all the skills required for this role.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {learningRoadmap.map((phase, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="border border-border rounded-xl overflow-hidden"
                  >
                    <button
                      onClick={() => setExpandedPhase(expandedPhase === index ? null : index)}
                      className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${phase.priority === 'High' ? 'bg-success/20 text-success' :
                          phase.priority === 'Medium' ? 'bg-warning/20 text-warning-foreground' :
                            'bg-muted text-muted-foreground'
                          }`}>
                          {index + 1}
                        </div>
                        <div className="text-left">
                          <h3 className="font-medium">{phase.title}</h3>
                          <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              ~{phase.durationMonths} months
                            </span>
                            <span className={`px-2 py-0.5 rounded text-xs ${phase.priority === 'High' ? 'bg-success/20 text-success' :
                              phase.priority === 'Medium' ? 'bg-warning/20 text-warning-foreground' :
                                'bg-muted'
                              }`}>
                              {phase.priority} Priority
                            </span>
                          </div>
                        </div>
                      </div>
                      {expandedPhase === index ? (
                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      )}
                    </button>

                    {expandedPhase === index && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-4 pb-4"
                      >
                        <div className="pt-4 border-t border-border">
                          <h4 className="text-sm font-medium mb-3">Skills to Learn:</h4>
                          <div className="flex flex-wrap gap-2">
                            {phase.skills.map((skill) => (
                              <div
                                key={skill}
                                className="px-3 py-2 rounded-lg bg-muted/50 text-sm"
                              >
                                <span className="font-medium">{skill}</span>
                                {skillTaxonomy[skill] && (
                                  <span className="text-muted-foreground ml-2">
                                    ({skillTaxonomy[skill].learningTimeMonths} mo)
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};


