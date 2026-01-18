"use client";

import React, { useState, useMemo, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Filter,
  LayoutGrid,
  List,
  SlidersHorizontal,
  X,
  Briefcase,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import Layout from "@/components/layout/Layout";
import JobCard from "@/components/jobs/JobCard";
import JobFilters, { FilterState } from "@/components/jobs/JobFilters";
import { mockJobs, Job } from "@/data/mockData";
import { getJobs, calculateMatches, APIError } from "@/services/api";
import { JobAPI } from "@/types/api";
import { useResume } from "@/contexts/ResumeContext";

// Transform API job to frontend Job format
function transformApiJobToFrontend(apiJob: JobAPI, matchResult?: any): Job {
  return {
    id: String(apiJob.id),
    title: apiJob.title,
    company: apiJob.company,
    location: apiJob.location,
    salary: {
      min: apiJob.salary_min,
      max: apiJob.salary_max,
    },
    skills: [...apiJob.required_skills, ...apiJob.nice_to_have_skills],
    type: apiJob.is_remote ? "Remote" : "Full-time",
    experience: apiJob.min_experience_years,
    description: apiJob.description,
    matchScore: matchResult?.match_score || 70,
    postedDate: new Date(),
    missingSkills: matchResult?.missing_skills,
    explanation: matchResult?.explanation,
    topReason: matchResult?.top_reason_for_match,
    topImprovement: matchResult?.top_area_to_improve,
  };
}

export default function JobsPage() {
  const { parsedResume } = useResume();
  const [search, setSearch] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [sortBy, setSortBy] = useState("match");
  const [showFilters, setShowFilters] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    locations: [],
    experience: [0, 10],
    salary: [0, 300000],
    skills: [],
    jobTypes: [],
    postedDate: "all",
  });

  // Fetch jobs from API on mount
  useEffect(() => {
    async function fetchJobs() {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch jobs from backend
        const response = await getJobs();

        // Get candidate skills for matching
        const candidateSkills = parsedResume?.skills.map((s) => s.name) || [];

        // If we have candidate skills, calculate match scores
        let jobsWithScores: Job[] = [];

        if (candidateSkills.length > 0 && response.jobs.length > 0) {
          try {
            const matchResponse = await calculateMatches({
              full_name: parsedResume?.name || "Candidate",
              skills: candidateSkills,
              experience_years: parsedResume?.yearsOfExperience || 0,
            });

            // Map match results to jobs
            jobsWithScores = response.jobs.map((apiJob) => {
              const matchResult = matchResponse.matches.find(
                (m: any) => m.job_id === apiJob.id
              );
              return transformApiJobToFrontend(apiJob, matchResult);
            });
          } catch {
            // If matching fails, just use default scores
            jobsWithScores = response.jobs.map((apiJob) =>
              transformApiJobToFrontend(apiJob, 70)
            );
          }
        } else {
          // No resume parsed, use default scores
          jobsWithScores = response.jobs.map((apiJob) =>
            transformApiJobToFrontend(apiJob, 70)
          );
        }

        // If API returned no jobs, fall back to mock data
        if (jobsWithScores.length === 0) {
          setJobs(mockJobs);
        } else {
          setJobs(jobsWithScores);
        }
      } catch (err) {
        console.error("Failed to fetch jobs:", err);
        // Fall back to mock data on error
        setJobs(mockJobs);
        if (err instanceof APIError) {
          setError(err.message);
        }
      } finally {
        setIsLoading(false);
      }
    }

    fetchJobs();
  }, [parsedResume]);

  const filteredJobs = useMemo(() => {
    let result = [...jobs];

    // Search filter
    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter(
        (job) =>
          job.title.toLowerCase().includes(searchLower) ||
          job.company.toLowerCase().includes(searchLower) ||
          job.description.toLowerCase().includes(searchLower) ||
          job.skills.some((s) => s.toLowerCase().includes(searchLower))
      );
    }

    // Location filter
    if (filters.locations.length > 0) {
      result = result.filter((job) => filters.locations.includes(job.location));
    }

    // Experience filter
    result = result.filter(
      (job) =>
        job.experience >= filters.experience[0] &&
        job.experience <= filters.experience[1]
    );

    // Salary filter (convert to same unit - assuming backend uses INR)
    result = result.filter(
      (job) =>
        job.salary.min >= filters.salary[0] &&
        job.salary.max <= filters.salary[1] * 100
    );

    // Skills filter
    if (filters.skills.length > 0) {
      result = result.filter((job) =>
        filters.skills.some((skill) => job.skills.includes(skill))
      );
    }

    // Job type filter
    if (filters.jobTypes.length > 0) {
      result = result.filter((job) => filters.jobTypes.includes(job.type));
    }

    // Sort
    switch (sortBy) {
      case "match":
        result.sort((a, b) => b.matchScore - a.matchScore);
        break;
      case "salary":
        result.sort((a, b) => b.salary.max - a.salary.max);
        break;
      case "date":
        result.sort((a, b) => b.postedDate.getTime() - a.postedDate.getTime());
        break;
      case "experience":
        result.sort((a, b) => a.experience - b.experience);
        break;
    }

    return result;
  }, [search, filters, sortBy, jobs]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.locations.length > 0) count++;
    if (filters.skills.length > 0) count++;
    if (filters.jobTypes.length > 0) count++;
    if (filters.experience[0] > 0 || filters.experience[1] < 10) count++;
    if (filters.salary[0] > 0 || filters.salary[1] < 300000) count++;
    if (filters.postedDate !== "all") count++;
    return count;
  }, [filters]);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearch(e.target.value);
    },
    []
  );

  return (
    <Layout>
      <div className="py-8">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-10"
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Discover Your Next Role
            </h1>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Browse {jobs.length}+ opportunities matched to your profile
            </p>
          </motion.div>

          {/* Search & Controls */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8 space-y-4"
          >
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  placeholder="Search jobs, companies, or skills..."
                  value={search}
                  onChange={handleSearchChange}
                  className="pl-12 py-6 rounded-xl"
                />
                {search && (
                  <button
                    onClick={() => setSearch("")}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-muted rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              <div className="flex gap-2">
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-[160px] rounded-xl">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="match">Match Score</SelectItem>
                    <SelectItem value="salary">Salary</SelectItem>
                    <SelectItem value="date">Date Posted</SelectItem>
                    <SelectItem value="experience">Experience</SelectItem>
                  </SelectContent>
                </Select>

                <div className="hidden md:flex border border-border rounded-xl overflow-hidden">
                  <Button
                    variant={view === "grid" ? "default" : "ghost"}
                    size="icon"
                    onClick={() => setView("grid")}
                    className="rounded-none"
                  >
                    <LayoutGrid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={view === "list" ? "default" : "ghost"}
                    size="icon"
                    onClick={() => setView("list")}
                    className="rounded-none"
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>

                <Sheet open={showFilters} onOpenChange={setShowFilters}>
                  <SheetTrigger asChild>
                    <Button
                      variant="outline"
                      className="md:hidden rounded-xl relative"
                    >
                      <SlidersHorizontal className="w-4 h-4 mr-2" />
                      Filters
                      {activeFilterCount > 0 && (
                        <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center">
                          {activeFilterCount}
                        </span>
                      )}
                    </Button>
                  </SheetTrigger>
                  <SheetContent
                    side="left"
                    className="w-full sm:w-[400px] overflow-y-auto"
                  >
                    <JobFilters
                      filters={filters}
                      onFilterChange={setFilters}
                      onClose={() => setShowFilters(false)}
                      isMobile
                    />
                  </SheetContent>
                </Sheet>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing{" "}
                <span className="font-medium text-foreground">
                  {filteredJobs.length}
                </span>{" "}
                jobs
              </p>
              {activeFilterCount > 0 && (
                <button
                  onClick={() =>
                    setFilters({
                      locations: [],
                      experience: [0, 10],
                      salary: [0, 300000],
                      skills: [],
                      jobTypes: [],
                      postedDate: "all",
                    })
                  }
                  className="text-sm text-primary hover:underline"
                >
                  Clear filters ({activeFilterCount})
                </button>
              )}
            </div>
          </motion.div>

          <div className="flex gap-8">
            {/* Desktop Sidebar */}
            <motion.aside
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="hidden md:block w-72 flex-shrink-0"
            >
              <div className="sticky top-24 bg-card border border-border rounded-2xl p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <Filter className="w-4 h-4" />
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs">
                      {activeFilterCount}
                    </span>
                  )}
                </h2>
                <JobFilters filters={filters} onFilterChange={setFilters} />
              </div>
            </motion.aside>

            {/* Job Listings */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex-1"
            >
              {isLoading ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <span className="ml-3 text-muted-foreground">
                    Loading jobs...
                  </span>
                </div>
              ) : (
                <AnimatePresence mode="wait">
                  {filteredJobs.length === 0 ? (
                    <motion.div
                      key="empty"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="text-center py-16"
                    >
                      <Briefcase className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-xl font-semibold mb-2">
                        No jobs found
                      </h3>
                      <p className="text-muted-foreground mb-4">
                        Try adjusting your search or filters
                      </p>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setSearch("");
                          setFilters({
                            locations: [],
                            experience: [0, 10],
                            salary: [0, 300000],
                            skills: [],
                            jobTypes: [],
                            postedDate: "all",
                          });
                        }}
                      >
                        Clear all
                      </Button>
                    </motion.div>
                  ) : (
                    <motion.div
                      key={`${view}-${sortBy}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className={
                        view === "grid"
                          ? "grid sm:grid-cols-2 xl:grid-cols-3 gap-5"
                          : "space-y-4"
                      }
                    >
                      {filteredJobs.map((job, index) => (
                        <JobCard
                          key={job.id}
                          job={job}
                          view={view}
                          index={index}
                        />
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
