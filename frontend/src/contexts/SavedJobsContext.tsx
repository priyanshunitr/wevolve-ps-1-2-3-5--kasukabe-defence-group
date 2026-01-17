import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SavedJobsContextType {
  savedJobs: string[];
  toggleSaveJob: (jobId: string) => void;
  isJobSaved: (jobId: string) => boolean;
}

const SavedJobsContext = createContext<SavedJobsContextType | undefined>(undefined);

export const SavedJobsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [savedJobs, setSavedJobs] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('savedJobs');
      return stored ? JSON.parse(stored) : [];
    }
    return [];
  });

  useEffect(() => {
    localStorage.setItem('savedJobs', JSON.stringify(savedJobs));
  }, [savedJobs]);

  const toggleSaveJob = (jobId: string) => {
    setSavedJobs(prev =>
      prev.includes(jobId)
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    );
  };

  const isJobSaved = (jobId: string) => savedJobs.includes(jobId);

  return (
    <SavedJobsContext.Provider value={{ savedJobs, toggleSaveJob, isJobSaved }}>
      {children}
    </SavedJobsContext.Provider>
  );
};

export const useSavedJobs = () => {
  const context = useContext(SavedJobsContext);
  if (!context) {
    throw new Error('useSavedJobs must be used within a SavedJobsProvider');
  }
  return context;
};
