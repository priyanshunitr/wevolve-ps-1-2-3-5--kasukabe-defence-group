import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  MapPin,
  Briefcase,
  Heart,
  ExternalLink,
  Building2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import MatchScoreRing from "@/components/common/MatchScoreRing";
import { useSavedJobs } from "@/contexts/SavedJobsContext";
import type { Job } from "@/data/mockData";
import JobRoadmapPopup from "./JobRoadmapPopup";

interface JobCardProps {
  job: Job;
  view: "grid" | "list";
  index: number;
}

const JobCard: React.FC<JobCardProps> = ({ job, view, index }) => {
  const { isJobSaved, toggleSaveJob } = useSavedJobs();
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const saved = isJobSaved(job.id);

  const formatSalary = (min: number, max: number) => {
    return `₹${(min / 100000).toFixed(1)}L - ${(max / 100000).toFixed(1)}L`;
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );
    if (diff === 0) return "Today";
    if (diff === 1) return "Yesterday";
    if (diff < 7) return `${diff} days ago`;
    if (diff < 30) return `${Math.floor(diff / 7)} weeks ago`;
    return `${Math.floor(diff / 30)} months ago`;
  };

  const handleCardClick = () => {
    setIsPopupOpen(true);
  };

  const handleActionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  if (view === "list") {
    return (
      <>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.03 }}
          whileHover={{ y: -2 }}
          onClick={handleCardClick}
          className="bg-card border border-border rounded-xl p-5 hover:shadow-lg transition-all cursor-pointer group"
        >
          <div className="flex items-start gap-4">
            <div className="hidden sm:flex w-14 h-14 rounded-xl bg-primary/10 items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
              <Building2 className="w-7 h-7 text-primary" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">
                    {job.title}
                  </h3>
                  <p className="text-muted-foreground">{job.company}</p>
                </div>
                <MatchScoreRing
                  score={job.matchScore}
                  size="sm"
                  showLabel={false}
                />
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-3 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {job.location}
                </span>
                <span className="flex items-center gap-1">
                  <Briefcase className="w-4 h-4" />
                  {job.experience}+ years
                </span>
                <span className="font-medium text-foreground">
                  {formatSalary(job.salary.min, job.salary.max)}
                </span>
                <span className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground text-xs">
                  {job.type}
                </span>
              </div>

              <div className="flex flex-wrap gap-1.5 mt-3">
                {job.skills.slice(0, 5).map((skill) => (
                  <span
                    key={skill}
                    className="px-2 py-0.5 rounded bg-muted text-sm"
                  >
                    {skill}
                  </span>
                ))}
                {job.skills.length > 5 && (
                  <span className="px-2 py-0.5 rounded bg-muted text-sm text-muted-foreground">
                    +{job.skills.length - 5}
                  </span>
                )}
              </div>
            </div>

            <div
              className="flex flex-col gap-2 flex-shrink-0"
              onClick={handleActionClick}
            >
              <Button
                variant="ghost"
                size="icon"
                onClick={() => toggleSaveJob(job.id)}
                className={`rounded-full ${saved ? "text-destructive" : ""}`}
              >
                <Heart className={`w-5 h-5 ${saved ? "fill-current" : ""}`} />
              </Button>
              <Button size="sm" className="hidden sm:flex">
                Apply
                <ExternalLink className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        </motion.div>
        <JobRoadmapPopup
          job={job}
          isOpen={isPopupOpen}
          onClose={() => setIsPopupOpen(false)}
        />
      </>
    );
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.03 }}
        whileHover={{ y: -5 }}
        onClick={handleCardClick}
        className="bg-card border border-border rounded-2xl p-5 hover:shadow-xl transition-all h-full flex flex-col cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
            <Building2 className="w-6 h-6 text-primary" />
          </div>
          <MatchScoreRing score={job.matchScore} size="sm" />
        </div>

        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-1 line-clamp-2 group-hover:text-primary transition-colors">
            {job.title}
          </h3>
          <p className="text-muted-foreground mb-3">{job.company}</p>

          <div className="space-y-2 text-sm text-muted-foreground mb-4">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              <span>{job.location}</span>
            </div>
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4" />
              <span>{job.experience}+ years experience</span>
            </div>
            <p className="font-semibold text-foreground">
              {formatSalary(job.salary.min, job.salary.max)}
            </p>
          </div>

          <div className="flex flex-wrap gap-1.5 mb-4">
            {job.skills.slice(0, 4).map((skill) => (
              <span
                key={skill}
                className="px-2 py-0.5 rounded bg-muted text-xs"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 4 && (
              <span className="px-2 py-0.5 rounded bg-muted text-xs text-muted-foreground">
                +{job.skills.length - 4}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-border">
          <span className="text-xs text-muted-foreground">
            {formatDate(job.postedDate)}
          </span>
          <div className="flex items-center gap-2" onClick={handleActionClick}>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => toggleSaveJob(job.id)}
              className={`rounded-full h-9 w-9 ${
                saved ? "text-destructive" : ""
              }`}
            >
              <Heart className={`w-4 h-4 ${saved ? "fill-current" : ""}`} />
            </Button>
            <Button size="sm">Apply</Button>
          </div>
        </div>
      </motion.div>
      <JobRoadmapPopup
        job={job}
        isOpen={isPopupOpen}
        onClose={() => setIsPopupOpen(false)}
      />
    </>
  );
};

export default JobCard;
