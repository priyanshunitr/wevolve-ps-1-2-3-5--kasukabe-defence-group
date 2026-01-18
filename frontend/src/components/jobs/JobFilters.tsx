import React from 'react';
import { motion } from 'framer-motion';
import { X, MapPin, Briefcase, Clock, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';


export interface FilterState {
  locations: string[];
  experience: [number, number];
  salary: [number, number];
  skills: string[];
  jobTypes: string[];
  postedDate: string;
}

interface JobFiltersProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  onClose?: () => void;
  isMobile?: boolean;
}

const locations = [
  'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 'Remote',
  'Boston, MA', 'Los Angeles, CA', 'Chicago, IL', 'Denver, CO', 'Atlanta, GA'
];

const allSkills = [
  'React', 'TypeScript', 'JavaScript', 'Node.js', 'Python', 'AWS', 'Docker',
  'Kubernetes', 'GraphQL', 'PostgreSQL', 'MongoDB', 'Git', 'CSS', 'Next.js'
];

const jobTypes = ['Full-time', 'Part-time', 'Remote', 'Hybrid'];
const dateFilters = [
  { value: 'all', label: 'Any time' },
  { value: '24h', label: 'Last 24 hours' },
  { value: 'week', label: 'Last week' },
  { value: 'month', label: 'Last month' }
];

const JobFilters: React.FC<JobFiltersProps> = ({
  filters,
  onFilterChange,
  onClose,
  isMobile = false
}) => {
  const toggleLocation = (location: string) => {
    const updated = filters.locations.includes(location)
      ? filters.locations.filter(l => l !== location)
      : [...filters.locations, location];
    onFilterChange({ ...filters, locations: updated });
  };

  const toggleSkill = (skill: string) => {
    const updated = filters.skills.includes(skill)
      ? filters.skills.filter(s => s !== skill)
      : [...filters.skills, skill];
    onFilterChange({ ...filters, skills: updated });
  };

  const toggleJobType = (type: string) => {
    const updated = filters.jobTypes.includes(type)
      ? filters.jobTypes.filter(t => t !== type)
      : [...filters.jobTypes, type];
    onFilterChange({ ...filters, jobTypes: updated });
  };

  const clearFilters = () => {
    onFilterChange({
      locations: [],
      experience: [0, 10],
      salary: [0, 300000],
      skills: [],
      jobTypes: [],
      postedDate: 'all'
    });
  };

  const hasActiveFilters = 
    filters.locations.length > 0 ||
    filters.skills.length > 0 ||
    filters.jobTypes.length > 0 ||
    filters.experience[0] > 0 ||
    filters.experience[1] < 10 ||
    filters.salary[0] > 0 ||
    filters.salary[1] < 300000 ||
    filters.postedDate !== 'all';

  return (
    <div className="space-y-6">
      {isMobile && (
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            <h2 className="font-semibold text-lg">Filters</h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>
      )}

      {hasActiveFilters && (
        <Button variant="outline" size="sm" onClick={clearFilters} className="w-full">
          Clear all filters
        </Button>
      )}

      {/* Location Filter */}
      <div>
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-primary" />
          Location
        </h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {locations.map((location) => (
            <label
              key={location}
              className="flex items-center gap-2 cursor-pointer hover:bg-muted/50 rounded p-1 transition-colors"
            >
              <Checkbox
                checked={filters.locations.includes(location)}
                onCheckedChange={() => toggleLocation(location)}
              />
              <span className="text-sm">{location}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Filter */}
      <div>
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-primary" />
          Experience (years)
        </h3>
        <div className="px-2">
          <Slider
            min={0}
            max={10}
            step={1}
            value={filters.experience}
            onValueChange={(value) => onFilterChange({ ...filters, experience: value as [number, number] })}
            className="mb-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{filters.experience[0]} years</span>
            <span>{filters.experience[1]}+ years</span>
          </div>
        </div>
      </div>

      {/* Salary Filter */}
      <div>
        <h3 className="font-medium mb-3">Salary Range</h3>
        <div className="px-2">
          <Slider
            min={0}
            max={300000}
            step={10000}
            value={filters.salary}
            onValueChange={(value) => onFilterChange({ ...filters, salary: value as [number, number] })}
            className="mb-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>${Math.round(filters.salary[0] / 1000)}k</span>
            <span>${Math.round(filters.salary[1] / 1000)}k</span>
          </div>
        </div>
      </div>

      {/* Skills Filter */}
      <div>
        <h3 className="font-medium mb-3">Skills</h3>
        <div className="flex flex-wrap gap-2">
          {allSkills.map((skill) => (
            <button
              key={skill}
              onClick={() => toggleSkill(skill)}
              className={`px-3 py-1 rounded-full text-sm transition-all ${
                filters.skills.includes(skill)
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted hover:bg-muted/80'
              }`}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>

      {/* Job Type Filter */}
      <div>
        <h3 className="font-medium mb-3">Job Type</h3>
        <div className="space-y-2">
          {jobTypes.map((type) => (
            <label
              key={type}
              className="flex items-center gap-2 cursor-pointer hover:bg-muted/50 rounded p-1 transition-colors"
            >
              <Checkbox
                checked={filters.jobTypes.includes(type)}
                onCheckedChange={() => toggleJobType(type)}
              />
              <span className="text-sm">{type}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Posted Date Filter */}
      <div>
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary" />
          Posted Date
        </h3>
        <div className="space-y-2">
          {dateFilters.map((option) => (
            <label
              key={option.value}
              className="flex items-center gap-2 cursor-pointer hover:bg-muted/50 rounded p-1 transition-colors"
            >
              <input
                type="radio"
                name="postedDate"
                checked={filters.postedDate === option.value}
                onChange={() => onFilterChange({ ...filters, postedDate: option.value })}
                className="text-primary"
              />
              <span className="text-sm">{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      {isMobile && (
        <Button onClick={onClose} className="w-full py-6">
          Apply Filters
        </Button>
      )}
    </div>
  );
};

export default JobFilters;
