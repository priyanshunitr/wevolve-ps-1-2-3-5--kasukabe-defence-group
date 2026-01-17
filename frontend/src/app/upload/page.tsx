"use client";

import React, { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload as UploadIcon, FileText, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import Layout from '@/components/layout/Layout';
import { useResume, transformApiToFrontend } from '@/contexts/ResumeContext';
import { parseResume, APIError } from '@/services/api';

export default function UploadPage() {
    const router = useRouter();
    const { setResumeFile, setParsedResume, setCandidateId, setError } = useResume();
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setLocalError] = useState<string | null>(null);

    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const validateFile = (file: File) => {
        if (!validTypes.includes(file.type)) {
            setLocalError('Please upload a PDF or DOCX file');
            return false;
        }
        if (file.size > 10 * 1024 * 1024) {
            setLocalError('File size must be less than 10MB');
            return false;
        }
        return true;
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setLocalError(null);

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && validateFile(droppedFile)) {
            setFile(droppedFile);
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        setLocalError(null);
        const selectedFile = e.target.files?.[0];
        if (selectedFile && validateFile(selectedFile)) {
            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setUploadProgress(0);
        setLocalError(null);

        const progressInterval = setInterval(() => {
            setUploadProgress(prev => {
                if (prev >= 80) {
                    clearInterval(progressInterval);
                    return 80;
                }
                return prev + Math.random() * 15;
            });
        }, 200);

        try {
            const apiResponse = await parseResume(file);

            clearInterval(progressInterval);
            setUploadProgress(100);

            const frontendResume = transformApiToFrontend(apiResponse);
            setResumeFile(file);
            setParsedResume(frontendResume);
            setCandidateId(apiResponse.id || null);

            setTimeout(() => {
                router.push('/verify');
            }, 500);
        } catch (err) {
            clearInterval(progressInterval);
            setUploadProgress(0);
            setIsUploading(false);

            if (err instanceof APIError) {
                setLocalError(err.message);
                setError(err.message);
            } else {
                const message = 'Failed to parse resume. Please try again.';
                setLocalError(message);
                setError(message);
            }
        }
    };

    const removeFile = () => {
        setFile(null);
        setUploadProgress(0);
        setLocalError(null);
    };

    return (
        <Layout>
            <div className="min-h-[80vh] flex items-center justify-center py-16">
                <div className="container mx-auto px-4 max-w-2xl">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center mb-10"
                    >
                        <h1 className="text-3xl md:text-4xl font-bold mb-4">Upload Your Resume</h1>
                        <p className="text-muted-foreground">
                            Our AI will parse your resume and extract key information for analysis
                        </p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-card border border-border rounded-2xl p-8 shadow-lg"
                    >
                        <AnimatePresence mode="wait">
                            {!file ? (
                                <motion.div
                                    key="dropzone"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    onDragOver={handleDragOver}
                                    onDragLeave={handleDragLeave}
                                    onDrop={handleDrop}
                                    className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${isDragging
                                            ? 'border-primary bg-primary/5'
                                            : 'border-border hover:border-primary/50 hover:bg-muted/50'
                                        }`}
                                >
                                    <input
                                        type="file"
                                        accept=".pdf,.docx"
                                        onChange={handleFileSelect}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    <motion.div
                                        animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                                        className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-6"
                                    >
                                        <UploadIcon className="w-8 h-8 text-primary" />
                                    </motion.div>
                                    <h3 className="text-lg font-semibold mb-2">
                                        {isDragging ? 'Drop your file here' : 'Drag & Drop your resume'}
                                    </h3>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        or click to browse
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        Supports PDF, DOCX • Max 10MB
                                    </p>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="file-preview"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    className="space-y-6"
                                >
                                    <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-xl">
                                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                                            <FileText className="w-6 h-6 text-primary" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium truncate">{file.name}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                        {!isUploading && (
                                            <button
                                                onClick={removeFile}
                                                className="p-2 rounded-lg hover:bg-muted transition-colors"
                                            >
                                                <X className="w-5 h-5 text-muted-foreground" />
                                            </button>
                                        )}
                                    </div>

                                    {isUploading && (
                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-muted-foreground">
                                                    {uploadProgress < 100 ? 'Uploading & parsing...' : 'Complete!'}
                                                </span>
                                                <span className="font-medium">{Math.min(100, Math.round(uploadProgress))}%</span>
                                            </div>
                                            <Progress value={Math.min(100, uploadProgress)} className="h-2" />
                                        </div>
                                    )}

                                    {!isUploading && (
                                        <Button
                                            onClick={handleUpload}
                                            className="w-full py-6 text-base rounded-xl"
                                        >
                                            Parse Resume
                                        </Button>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-4 flex items-center gap-2 text-destructive text-sm"
                            >
                                <AlertCircle className="w-4 h-4" />
                                <span>{error}</span>
                            </motion.div>
                        )}
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="mt-8 grid md:grid-cols-3 gap-4 text-center"
                    >
                        {[
                            { icon: CheckCircle2, text: 'AI-powered parsing' },
                            { icon: CheckCircle2, text: 'Privacy protected' },
                            { icon: CheckCircle2, text: '99% accuracy' }
                        ].map((item, index) => (
                            <div key={index} className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                                <item.icon className="w-4 h-4 text-success" />
                                <span>{item.text}</span>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </Layout>
    );
}
