// Mock Data for AI Career Co-Pilot

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: { min: number; max: number };
  skills: string[];
  type: 'Full-time' | 'Part-time' | 'Remote' | 'Hybrid';
  experience: number;
  description: string;
  matchScore: number;
  postedDate: Date;
  logo?: string;
}

export interface TargetRole {
  id: string;
  title: string;
  requiredSkills: string[];
  typicalExperience: number;
  description: string;
}

export interface SkillTaxonomy {
  [skill: string]: {
    category: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    learningTimeMonths: number;
  };
}

export interface ParsedResume {
  name: string;
  email: string;
  phone: string;
  skills: { name: string; confidence: number }[];
  experience: {
    title: string;
    company: string;
    duration: string;
    description: string;
    confidence: number;
  }[];
  education: {
    degree: string;
    institution: string;
    year: string;
    confidence: number;
  }[];
  projects: {
    name: string;
    description: string;
    technologies: string[];
    confidence: number;
  }[];
  nameConfidence: number;
  emailConfidence: number;
  phoneConfidence: number;
}

const companies = [
  'TechCorp', 'InnovateLabs', 'DataFlow', 'CloudNine', 'DevSquad',
  'AI Solutions', 'CyberSafe', 'NextGen Tech', 'Quantum Dynamics', 'FutureWorks',
  'PixelPerfect', 'ByteBuilders', 'SmartSystems', 'DigitalEdge', 'CodeCraft',
  'TechVenture', 'AppMakers', 'SoftWorks', 'NetPro', 'WebWizards'
];

const locations = [
  'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 'Boston, MA',
  'Los Angeles, CA', 'Chicago, IL', 'Denver, CO', 'Remote', 'Atlanta, GA',
  'Miami, FL', 'Portland, OR', 'San Diego, CA', 'Phoenix, AZ', 'Dallas, TX'
];

const jobTitles = [
  'Senior Frontend Developer', 'Full Stack Engineer', 'React Developer',
  'Software Engineer', 'UI/UX Developer', 'JavaScript Developer',
  'TypeScript Engineer', 'Lead Developer', 'Tech Lead', 'Principal Engineer',
  'Staff Engineer', 'Frontend Architect', 'Application Developer',
  'Web Developer', 'Platform Engineer'
];

const allSkills = [
  'React', 'TypeScript', 'JavaScript', 'Node.js', 'Python', 'AWS', 'Docker',
  'Kubernetes', 'GraphQL', 'REST APIs', 'PostgreSQL', 'MongoDB', 'Redis',
  'Git', 'CI/CD', 'Agile', 'TDD', 'CSS', 'Tailwind CSS', 'Next.js',
  'Vue.js', 'Angular', 'Java', 'Go', 'Rust', 'C++', 'SQL', 'NoSQL',
  'Microservices', 'System Design', 'Machine Learning', 'Data Analysis'
];

const jobTypes: ('Full-time' | 'Part-time' | 'Remote' | 'Hybrid')[] = [
  'Full-time', 'Remote', 'Hybrid', 'Part-time'
];

function getRandomElement<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getRandomSubset<T>(arr: T[], min: number, max: number): T[] {
  const count = Math.floor(Math.random() * (max - min + 1)) + min;
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

function generateRandomDate(daysAgo: number): Date {
  const date = new Date();
  date.setDate(date.getDate() - Math.floor(Math.random() * daysAgo));
  return date;
}

export const generateJobs = (count: number): Job[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: `job-${i + 1}`,
    title: getRandomElement(jobTitles),
    company: getRandomElement(companies),
    location: getRandomElement(locations),
    salary: {
      min: Math.floor(Math.random() * 80000) + 80000,
      max: Math.floor(Math.random() * 80000) + 140000
    },
    skills: getRandomSubset(allSkills, 4, 8),
    type: getRandomElement(jobTypes),
    experience: Math.floor(Math.random() * 8) + 1,
    description: `We are looking for a talented professional to join our team. The ideal candidate will have strong skills and experience in modern development practices.`,
    matchScore: Math.floor(Math.random() * 39) + 60,
    postedDate: generateRandomDate(30),
    logo: undefined
  }));
};

export const mockJobs: Job[] = generateJobs(55);

export const targetRoles: TargetRole[] = [
  {
    id: 'senior-frontend',
    title: 'Senior Frontend Developer',
    requiredSkills: ['React', 'TypeScript', 'CSS', 'JavaScript', 'Testing', 'Performance Optimization', 'Accessibility', 'State Management'],
    typicalExperience: 5,
    description: 'Lead frontend development initiatives and mentor junior developers.'
  },
  {
    id: 'fullstack-engineer',
    title: 'Full Stack Engineer',
    requiredSkills: ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'REST APIs', 'Docker', 'AWS', 'Git'],
    typicalExperience: 4,
    description: 'Build and maintain both frontend and backend systems.'
  },
  {
    id: 'tech-lead',
    title: 'Technical Lead',
    requiredSkills: ['System Design', 'Architecture', 'Team Leadership', 'Code Review', 'Agile', 'Communication', 'React', 'Node.js'],
    typicalExperience: 7,
    description: 'Lead technical decisions and guide the engineering team.'
  },
  {
    id: 'data-engineer',
    title: 'Data Engineer',
    requiredSkills: ['Python', 'SQL', 'ETL', 'Data Pipelines', 'AWS', 'Spark', 'Kafka', 'Data Modeling'],
    typicalExperience: 4,
    description: 'Design and implement data infrastructure and pipelines.'
  },
  {
    id: 'devops-engineer',
    title: 'DevOps Engineer',
    requiredSkills: ['Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Terraform', 'Linux', 'Monitoring', 'Security'],
    typicalExperience: 4,
    description: 'Build and maintain infrastructure and deployment pipelines.'
  },
  {
    id: 'ml-engineer',
    title: 'Machine Learning Engineer',
    requiredSkills: ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Analysis', 'Statistics', 'MLOps', 'SQL'],
    typicalExperience: 5,
    description: 'Develop and deploy machine learning models at scale.'
  },
  {
    id: 'staff-engineer',
    title: 'Staff Engineer',
    requiredSkills: ['System Design', 'Architecture', 'Cross-team Collaboration', 'Mentorship', 'Technical Strategy', 'Performance', 'Security', 'Documentation'],
    typicalExperience: 8,
    description: 'Drive technical excellence across the organization.'
  },
  {
    id: 'mobile-dev',
    title: 'Mobile Developer',
    requiredSkills: ['React Native', 'TypeScript', 'iOS', 'Android', 'Mobile UI', 'App Store', 'Testing', 'Performance'],
    typicalExperience: 4,
    description: 'Build cross-platform mobile applications.'
  },
  {
    id: 'security-engineer',
    title: 'Security Engineer',
    requiredSkills: ['Security', 'Penetration Testing', 'OWASP', 'Encryption', 'Compliance', 'Incident Response', 'Network Security', 'Cloud Security'],
    typicalExperience: 5,
    description: 'Protect systems and data from security threats.'
  },
  {
    id: 'platform-engineer',
    title: 'Platform Engineer',
    requiredSkills: ['Kubernetes', 'Docker', 'Terraform', 'CI/CD', 'Cloud Platforms', 'Microservices', 'Observability', 'SRE'],
    typicalExperience: 5,
    description: 'Build and maintain the platform that powers applications.'
  }
];

export const skillTaxonomy: SkillTaxonomy = {
  'React': { category: 'Frontend', difficulty: 'Medium', learningTimeMonths: 3 },
  'TypeScript': { category: 'Language', difficulty: 'Medium', learningTimeMonths: 2 },
  'JavaScript': { category: 'Language', difficulty: 'Easy', learningTimeMonths: 2 },
  'Node.js': { category: 'Backend', difficulty: 'Medium', learningTimeMonths: 3 },
  'Python': { category: 'Language', difficulty: 'Easy', learningTimeMonths: 2 },
  'AWS': { category: 'Cloud', difficulty: 'Hard', learningTimeMonths: 4 },
  'Docker': { category: 'DevOps', difficulty: 'Medium', learningTimeMonths: 2 },
  'Kubernetes': { category: 'DevOps', difficulty: 'Hard', learningTimeMonths: 4 },
  'PostgreSQL': { category: 'Database', difficulty: 'Medium', learningTimeMonths: 2 },
  'MongoDB': { category: 'Database', difficulty: 'Easy', learningTimeMonths: 1 },
  'GraphQL': { category: 'API', difficulty: 'Medium', learningTimeMonths: 2 },
  'REST APIs': { category: 'API', difficulty: 'Easy', learningTimeMonths: 1 },
  'Git': { category: 'Tools', difficulty: 'Easy', learningTimeMonths: 1 },
  'CI/CD': { category: 'DevOps', difficulty: 'Medium', learningTimeMonths: 2 },
  'System Design': { category: 'Architecture', difficulty: 'Hard', learningTimeMonths: 6 },
  'Machine Learning': { category: 'AI/ML', difficulty: 'Hard', learningTimeMonths: 6 },
  'Testing': { category: 'Quality', difficulty: 'Medium', learningTimeMonths: 2 },
  'CSS': { category: 'Frontend', difficulty: 'Easy', learningTimeMonths: 1 },
  'Tailwind CSS': { category: 'Frontend', difficulty: 'Easy', learningTimeMonths: 1 },
  'Next.js': { category: 'Frontend', difficulty: 'Medium', learningTimeMonths: 2 },
  'Vue.js': { category: 'Frontend', difficulty: 'Medium', learningTimeMonths: 2 },
  'Angular': { category: 'Frontend', difficulty: 'Hard', learningTimeMonths: 4 },
  'SQL': { category: 'Database', difficulty: 'Easy', learningTimeMonths: 2 },
  'Terraform': { category: 'DevOps', difficulty: 'Medium', learningTimeMonths: 3 },
  'Security': { category: 'Security', difficulty: 'Hard', learningTimeMonths: 4 },
  'Agile': { category: 'Methodology', difficulty: 'Easy', learningTimeMonths: 1 },
  'Performance Optimization': { category: 'Engineering', difficulty: 'Hard', learningTimeMonths: 3 },
  'Accessibility': { category: 'Frontend', difficulty: 'Medium', learningTimeMonths: 2 },
  'State Management': { category: 'Frontend', difficulty: 'Medium', learningTimeMonths: 2 },
  'Architecture': { category: 'Architecture', difficulty: 'Hard', learningTimeMonths: 6 },
  'Team Leadership': { category: 'Soft Skills', difficulty: 'Medium', learningTimeMonths: 3 },
  'Code Review': { category: 'Engineering', difficulty: 'Easy', learningTimeMonths: 1 },
  'Communication': { category: 'Soft Skills', difficulty: 'Medium', learningTimeMonths: 2 }
};

export const sampleParsedResume: ParsedResume = {
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
  nameConfidence: 98,
  emailConfidence: 95,
  phoneConfidence: 72
};
