"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { FileText, Plus, Trash2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import Layout from '@/components/layout/Layout';
import ConfidenceBadge from '@/components/common/ConfidenceBadge';
import SkillBadge from '@/components/common/SkillBadge';
import { useResume, ParsedResumeFrontend, transformFrontendToApi } from '@/contexts/ResumeContext';
import { saveResume, APIError } from '@/services/api';

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
  experience: [
    {
      title: 'Frontend Developer',
      company: 'TechStart Inc.',
      duration: '2021 - Present',
      description: 'Developed and maintained React applications, improving performance by 40%.',
      confidence: 92
    },
    {
      title: 'Junior Developer',
      company: 'WebAgency',
      duration: '2019 - 2021',
      description: 'Built responsive websites using modern JavaScript frameworks.',
      confidence: 65
    }
  ],
  education: [
    {
      degree: 'B.S. Computer Science',
      institution: 'State University',
      year: '2019',
      confidence: 95
    }
  ],
  projects: [
    {
      name: 'E-commerce Platform',
      description: 'Full-stack e-commerce solution with React and Node.js',
      technologies: ['React', 'Node.js', 'MongoDB'],
      confidence: 88
    },
    {
      name: 'Task Management App',
      description: 'Real-time collaborative task management application',
      technologies: ['React', 'Firebase', 'TypeScript'],
      confidence: 62
    }
  ],
  preferredLocations: [],
  preferredRoles: [],
  expectedSalary: null,
  nameConfidence: 98,
  emailConfidence: 95,
  phoneConfidence: 72,
  yearsOfExperience: 4
};

export default function VerifyPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { resumeFile, parsedResume, setParsedResume, candidateId, setIsVerified } = useResume();
  const [formData, setFormData] = useState<ParsedResumeFrontend>(parsedResume || sampleParsedResume);
  const [newSkill, setNewSkill] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!parsedResume) {
      setFormData(sampleParsedResume);
    } else {
      setFormData(parsedResume);
    }
  }, [parsedResume]);

  const handleAddSkill = () => {
    if (newSkill.trim()) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, { name: newSkill.trim(), confidence: 100 }]
      }));
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);

    try {
      // If we have a candidateId from API, save to backend
      if (candidateId) {
        const apiData = transformFrontendToApi(formData);
        await saveResume(candidateId, apiData);
      }

      setParsedResume(formData);
      setIsVerified(true);

      toast({
        title: 'Resume Verified',
        description: 'Your resume data has been saved successfully.',
      });

      router.push('/gap-analysis');
    } catch (err) {
      const message = err instanceof APIError ? err.message : 'Failed to save resume. Please try again.';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Layout>
      <div className="py-8">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-4">Verify Resume Data</h1>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Review and edit the parsed information. Fields with low confidence are highlighted.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* PDF Preview Placeholder */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-2xl p-6 h-[600px] overflow-hidden"
            >
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-primary" />
                <h2 className="font-semibold">Original Document</h2>
              </div>
              <div className="bg-muted/50 rounded-xl h-[calc(100%-40px)] flex items-center justify-center">
                <div className="text-center p-8">
                  <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    {resumeFile ? resumeFile.name : 'Sample Resume Preview'}
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    PDF viewer would display here
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Editable Form */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-2xl p-6 h-[600px] overflow-y-auto"
            >
              <h2 className="font-semibold mb-6">Parsed Information</h2>

              <div className="space-y-6">
                {/* Basic Info */}
                <div className="space-y-4">
                  <div className={`p-4 rounded-xl ${formData.nameConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <Label htmlFor="name">Full Name</Label>
                      <ConfidenceBadge confidence={formData.nameConfidence} />
                    </div>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    />
                  </div>

                  <div className={`p-4 rounded-xl ${formData.emailConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <Label htmlFor="email">Email</Label>
                      <ConfidenceBadge confidence={formData.emailConfidence} />
                    </div>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    />
                  </div>

                  <div className={`p-4 rounded-xl ${formData.phoneConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <Label htmlFor="phone">Phone</Label>
                      <ConfidenceBadge confidence={formData.phoneConfidence} />
                    </div>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                    />
                  </div>
                </div>

                {/* Skills */}
                <div className="p-4 rounded-xl bg-muted/30">
                  <Label className="mb-3 block">Skills</Label>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {formData.skills.map((skill, index) => (
                      <SkillBadge
                        key={index}
                        skill={skill.name}
                        confidence={skill.confidence}
                        variant={skill.confidence < 70 ? 'lowConfidence' : 'default'}
                        onRemove={() => handleRemoveSkill(index)}
                      />
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add a skill..."
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                    />
                    <Button variant="outline" size="icon" onClick={handleAddSkill}>
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Experience */}
                <div className="space-y-4">
                  <Label>Work Experience</Label>
                  {formData.experience.map((exp, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className={`p-4 rounded-xl ${exp.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium">{exp.title} at {exp.company}</span>
                        <ConfidenceBadge confidence={exp.confidence} />
                      </div>
                      <p className="text-sm text-muted-foreground">{exp.duration}</p>
                      <p className="text-sm mt-2">{exp.description}</p>
                    </motion.div>
                  ))}
                </div>

                {/* Education */}
                <div className="space-y-4">
                  <Label>Education</Label>
                  {formData.education.map((edu, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className={`p-4 rounded-xl ${edu.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{edu.degree}</span>
                        <ConfidenceBadge confidence={edu.confidence} />
                      </div>
                      <p className="text-sm text-muted-foreground">{edu.institution} • {edu.year}</p>
                    </motion.div>
                  ))}
                </div>

                {/* Projects */}
                <div className="space-y-4">
                  <Label>Projects</Label>
                  {formData.projects.map((project, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className={`p-4 rounded-xl ${project.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{project.name}</span>
                        <ConfidenceBadge confidence={project.confidence} />
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{project.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {project.technologies.map((tech, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleSave}
                className="w-full mt-6 py-6 rounded-xl"
                disabled={isSaving}
              >
                <CheckCircle2 className="w-5 h-5 mr-2" />
                {isSaving ? 'Saving...' : 'Confirm & Save'}
              </Button>
            </motion.div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
