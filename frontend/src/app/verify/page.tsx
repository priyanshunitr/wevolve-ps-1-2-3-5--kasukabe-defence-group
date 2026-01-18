"use client";

import React, { useState, useEffect, useMemo } from 'react';
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
import FireEffect from '@/components/common/FireEffect';
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
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  useEffect(() => {
    if (resumeFile && resumeFile.type === 'application/pdf') {
      const url = URL.createObjectURL(resumeFile);
      setFileUrl(url);
      return () => URL.revokeObjectURL(url);
    }
    setFileUrl(null);
  }, [resumeFile]);

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
            {/* Document Preview */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-2xl p-6 h-[600px] overflow-hidden"
            >
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-primary" />
                <h2 className="font-semibold">Original Document</h2>
              </div>
              <div className="bg-muted/50 rounded-xl h-[calc(100%-40px)] overflow-hidden">
                {resumeFile ? (
                  resumeFile.type === 'application/pdf' ? (
                    // PDF Preview using object element
                    <object
                      data={fileUrl || ''}
                      type="application/pdf"
                      className="w-full h-full rounded-xl"
                    >
                      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                        <FileText className="w-16 h-16 text-muted-foreground mb-4" />
                        <p className="text-muted-foreground mb-2">Unable to display PDF</p>
                        <a
                          href={fileUrl || ''}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                        >
                          Open in new tab
                        </a>
                      </div>
                    </object>
                  ) : (
                    // DOCX Preview - can't be displayed directly in browser
                    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                      <div className="w-20 h-20 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-4">
                        <FileText className="w-10 h-10 text-blue-500" />
                      </div>
                      <p className="font-medium text-lg mb-1">{resumeFile.name}</p>
                      <p className="text-sm text-muted-foreground mb-2">
                        {(resumeFile.size / 1024 / 1024).toFixed(2)} MB • Word Document
                      </p>
                      <p className="text-xs text-muted-foreground mt-4 max-w-xs">
                        Word document preview is not available in browser.
                        The document has been parsed successfully.
                      </p>
                    </div>
                  )
                ) : (
                  // No file uploaded - show sample placeholder
                  <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                    <FileText className="w-16 h-16 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">Sample Resume Preview</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Upload a resume to see the preview
                    </p>
                  </div>
                )}
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
                  <FireEffect active={formData.nameConfidence < 60} intensity={formData.nameConfidence < 40 ? 'high' : 'medium'}>
                    <div className={`p-4 rounded-xl ${formData.nameConfidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : formData.nameConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
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
                  </FireEffect>

                  <FireEffect active={formData.emailConfidence < 60} intensity={formData.emailConfidence < 40 ? 'high' : 'medium'}>
                    <div className={`p-4 rounded-xl ${formData.emailConfidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : formData.emailConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
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
                  </FireEffect>

                  <FireEffect active={formData.phoneConfidence < 60} intensity={formData.phoneConfidence < 40 ? 'high' : 'medium'}>
                    <div className={`p-4 rounded-xl ${formData.phoneConfidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : formData.phoneConfidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}>
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
                  </FireEffect>
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
                  <div className="flex items-center justify-between">
                    <Label>Work Experience</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        experience: [...prev.experience, { title: '', company: '', duration: '', description: '', confidence: 100 }]
                      }))}
                    >
                      <Plus className="w-4 h-4 mr-1" /> Add
                    </Button>
                  </div>
                  {formData.experience.map((exp, index) => (
                    <FireEffect key={index} active={exp.confidence < 60} intensity={exp.confidence < 40 ? 'high' : 'medium'}>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={`p-4 rounded-xl space-y-3 ${exp.confidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : exp.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                      >
                        <div className="flex items-center justify-between">
                          <ConfidenceBadge confidence={exp.confidence} />
                          <button
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              experience: prev.experience.filter((_, i) => i !== index)
                            }))}
                            className="p-1 rounded hover:bg-destructive/10 text-destructive"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <Input
                            placeholder="Job Title"
                            value={exp.title}
                            onChange={(e) => setFormData(prev => ({
                              ...prev,
                              experience: prev.experience.map((ex, i) => i === index ? { ...ex, title: e.target.value } : ex)
                            }))}
                          />
                          <Input
                            placeholder="Company"
                            value={exp.company}
                            onChange={(e) => setFormData(prev => ({
                              ...prev,
                              experience: prev.experience.map((ex, i) => i === index ? { ...ex, company: e.target.value } : ex)
                            }))}
                          />
                        </div>
                        <Input
                          placeholder="Duration (e.g., 2020 - Present)"
                          value={exp.duration}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            experience: prev.experience.map((ex, i) => i === index ? { ...ex, duration: e.target.value } : ex)
                          }))}
                        />
                        <Input
                          placeholder="Description"
                          value={exp.description}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            experience: prev.experience.map((ex, i) => i === index ? { ...ex, description: e.target.value } : ex)
                          }))}
                        />
                      </motion.div>
                    </FireEffect>
                  ))}
                </div>

                {/* Education */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Education</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        education: [...prev.education, { degree: '', institution: '', year: '', confidence: 100 }]
                      }))}
                    >
                      <Plus className="w-4 h-4 mr-1" /> Add
                    </Button>
                  </div>
                  {formData.education.map((edu, index) => (
                    <FireEffect key={index} active={edu.confidence < 60} intensity={edu.confidence < 40 ? 'high' : 'medium'}>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={`p-4 rounded-xl space-y-3 ${edu.confidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : edu.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                      >
                        <div className="flex items-center justify-between">
                          <ConfidenceBadge confidence={edu.confidence} />
                          <button
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              education: prev.education.filter((_, i) => i !== index)
                            }))}
                            className="p-1 rounded hover:bg-destructive/10 text-destructive"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <Input
                          placeholder="Degree (e.g., B.S. Computer Science)"
                          value={edu.degree}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            education: prev.education.map((ed, i) => i === index ? { ...ed, degree: e.target.value } : ed)
                          }))}
                        />
                        <div className="grid grid-cols-2 gap-2">
                          <Input
                            placeholder="Institution"
                            value={edu.institution}
                            onChange={(e) => setFormData(prev => ({
                              ...prev,
                              education: prev.education.map((ed, i) => i === index ? { ...ed, institution: e.target.value } : ed)
                            }))}
                          />
                          <Input
                            placeholder="Year (e.g., 2020)"
                            value={edu.year}
                            onChange={(e) => setFormData(prev => ({
                              ...prev,
                              education: prev.education.map((ed, i) => i === index ? { ...ed, year: e.target.value } : ed)
                            }))}
                          />
                        </div>
                      </motion.div>
                    </FireEffect>
                  ))}
                </div>

                {/* Projects */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Projects</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        projects: [...prev.projects, { name: '', description: '', technologies: [], confidence: 100 }]
                      }))}
                    >
                      <Plus className="w-4 h-4 mr-1" /> Add
                    </Button>
                  </div>
                  {formData.projects.map((project, index) => (
                    <FireEffect key={index} active={project.confidence < 60} intensity={project.confidence < 40 ? 'high' : 'medium'}>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={`p-4 rounded-xl space-y-3 ${project.confidence < 60 ? 'bg-orange-500/10 border border-orange-500/30' : project.confidence < 70 ? 'bg-warning/10 border border-warning/30' : 'bg-muted/30'}`}
                      >
                        <div className="flex items-center justify-between">
                          <ConfidenceBadge confidence={project.confidence} />
                          <button
                            onClick={() => setFormData(prev => ({
                              ...prev,
                              projects: prev.projects.filter((_, i) => i !== index)
                            }))}
                            className="p-1 rounded hover:bg-destructive/10 text-destructive"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <Input
                          placeholder="Project Name"
                          value={project.name}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            projects: prev.projects.map((p, i) => i === index ? { ...p, name: e.target.value } : p)
                          }))}
                        />
                        <Input
                          placeholder="Description"
                          value={project.description}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            projects: prev.projects.map((p, i) => i === index ? { ...p, description: e.target.value } : p)
                          }))}
                        />
                        <Input
                          placeholder="Technologies (comma separated, e.g., React, Node.js, MongoDB)"
                          value={project.technologies.join(', ')}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            projects: prev.projects.map((p, i) => i === index ? { ...p, technologies: e.target.value.split(',').map(t => t.trim()).filter(t => t) } : p)
                          }))}
                        />
                      </motion.div>
                    </FireEffect>
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
