"""
Roadmap Generator Service
Generates personalized learning paths based on skill gaps
"""
from typing import List

from ..schemas.roadmap import LearningResource, SkillNode, LearningPhase


class RoadmapGenerator:
    """Service for generating personalized learning roadmaps"""
    
    # Phase metadata
    PHASE_TITLES = ["Foundation", "Core Skills", "Advanced Topics", "Specialization", "Mastery"]
    PHASE_MILESTONES = [
        "You'll have the fundamentals to start building",
        "You can contribute to real projects",
        "You'll be comfortable with complex implementations",
        "You'll be an expert in key areas",
        "You'll be ready for senior-level responsibilities"
    ]
    
    # Skill resources database
    SKILL_RESOURCES = {
        "python": {
            "category": "Programming", "difficulty": 2, "prerequisites": [], "estimated_weeks": 4,
            "resources": [
                {"title": "Python for Everybody", "type": "course", "url": "https://www.coursera.org/specializations/python",
                 "provider": "Coursera", "estimated_hours": 40, "is_free": True},
                {"title": "Automate the Boring Stuff", "type": "course", "url": "https://automatetheboringstuff.com/",
                 "provider": "Al Sweigart", "estimated_hours": 20, "is_free": True}
            ]
        },
        "fastapi": {
            "category": "Backend Framework", "difficulty": 3, "prerequisites": ["python"], "estimated_weeks": 2,
            "resources": [
                {"title": "FastAPI Official Tutorial", "type": "documentation", "url": "https://fastapi.tiangolo.com/tutorial/",
                 "provider": "FastAPI", "estimated_hours": 10, "is_free": True}
            ]
        },
        "postgresql": {
            "category": "Database", "difficulty": 3, "prerequisites": ["sql"], "estimated_weeks": 3,
            "resources": [
                {"title": "PostgreSQL Tutorial", "type": "tutorial", "url": "https://www.postgresqltutorial.com/",
                 "provider": "PostgreSQL Tutorial", "estimated_hours": 15, "is_free": True}
            ]
        },
        "sql": {
            "category": "Database", "difficulty": 2, "prerequisites": [], "estimated_weeks": 2,
            "resources": [
                {"title": "SQLZoo", "type": "tutorial", "url": "https://sqlzoo.net/",
                 "provider": "SQLZoo", "estimated_hours": 8, "is_free": True}
            ]
        },
        "docker": {
            "category": "DevOps", "difficulty": 3, "prerequisites": [], "estimated_weeks": 2,
            "resources": [
                {"title": "Docker Getting Started", "type": "documentation", "url": "https://docs.docker.com/get-started/",
                 "provider": "Docker", "estimated_hours": 5, "is_free": True}
            ]
        },
        "kubernetes": {
            "category": "DevOps", "difficulty": 4, "prerequisites": ["docker"], "estimated_weeks": 4,
            "resources": [
                {"title": "Kubernetes Basics", "type": "tutorial", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
                 "provider": "Kubernetes", "estimated_hours": 10, "is_free": True}
            ]
        },
        "aws": {
            "category": "Cloud", "difficulty": 4, "prerequisites": [], "estimated_weeks": 6,
            "resources": [
                {"title": "AWS Cloud Practitioner Essentials", "type": "course",
                 "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/",
                 "provider": "AWS", "estimated_hours": 6, "is_free": True}
            ]
        },
        "react": {
            "category": "Frontend", "difficulty": 3, "prerequisites": ["javascript"], "estimated_weeks": 4,
            "resources": [
                {"title": "React Official Tutorial", "type": "documentation", "url": "https://react.dev/learn",
                 "provider": "React", "estimated_hours": 15, "is_free": True}
            ]
        },
        "javascript": {
            "category": "Programming", "difficulty": 2, "prerequisites": [], "estimated_weeks": 4,
            "resources": [
                {"title": "JavaScript.info", "type": "tutorial", "url": "https://javascript.info/",
                 "provider": "JavaScript.info", "estimated_hours": 30, "is_free": True}
            ]
        },
        "typescript": {
            "category": "Programming", "difficulty": 3, "prerequisites": ["javascript"], "estimated_weeks": 2,
            "resources": [
                {"title": "TypeScript Handbook", "type": "documentation", "url": "https://www.typescriptlang.org/docs/handbook/",
                 "provider": "TypeScript", "estimated_hours": 10, "is_free": True}
            ]
        },
        "mongodb": {
            "category": "Database", "difficulty": 2, "prerequisites": [], "estimated_weeks": 2,
            "resources": [
                {"title": "MongoDB University", "type": "course", "url": "https://university.mongodb.com/",
                 "provider": "MongoDB", "estimated_hours": 20, "is_free": True}
            ]
        },
        "redis": {
            "category": "Database", "difficulty": 2, "prerequisites": [], "estimated_weeks": 1,
            "resources": [
                {"title": "Redis University", "type": "course", "url": "https://university.redis.com/",
                 "provider": "Redis", "estimated_hours": 8, "is_free": True}
            ]
        },
        "spark": {
            "category": "Big Data", "difficulty": 4, "prerequisites": ["python", "sql"], "estimated_weeks": 4,
            "resources": [
                {"title": "Apache Spark Documentation", "type": "documentation", "url": "https://spark.apache.org/docs/latest/",
                 "provider": "Apache", "estimated_hours": 20, "is_free": True}
            ]
        },
        "airflow": {
            "category": "Orchestration", "difficulty": 3, "prerequisites": ["python"], "estimated_weeks": 2,
            "resources": [
                {"title": "Apache Airflow Tutorial", "type": "documentation",
                 "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/",
                 "provider": "Apache", "estimated_hours": 10, "is_free": True}
            ]
        }
    }
    
    def topological_sort_skills(self, missing_skills: List[str]) -> List[List[str]]:
        """Sort skills into phases based on dependencies using Kahn's algorithm"""
        missing_lower = {s.lower() for s in missing_skills}
        
        # Build dependency graph
        dependencies = {}
        for skill in missing_lower:
            skill_data = self.SKILL_RESOURCES.get(skill, {})
            prereqs = skill_data.get('prerequisites', [])
            dependencies[skill] = {p for p in prereqs if p.lower() in missing_lower}
        
        phases = []
        remaining = set(missing_lower)
        
        while remaining:
            phase = [s for s in remaining if not (dependencies.get(s, set()) & remaining)]
            if not phase:
                phases.append(list(remaining))
                break
            phases.append(phase)
            remaining -= set(phase)
        
        return phases
    
    def get_skill_node(self, skill_name: str, job_required_skills: List[str]) -> SkillNode:
        """Create a SkillNode with full details"""
        skill_data = self.SKILL_RESOURCES.get(skill_name.lower(), {})
        is_required = skill_name.lower() in [s.lower() for s in job_required_skills]
        
        resources = [LearningResource(**res) for res in skill_data.get('resources', [])]
        if not resources:
            resources = [LearningResource(
                title=f"Learn {skill_name.title()}", type="tutorial",
                provider="Various", estimated_hours=10, is_free=True
            )]
        
        return SkillNode(
            name=skill_name.title(),
            category=skill_data.get('category', 'Technical'),
            difficulty=skill_data.get('difficulty', 3),
            estimated_weeks=skill_data.get('estimated_weeks', 2),
            prerequisites=[p.title() for p in skill_data.get('prerequisites', [])],
            resources=resources,
            why_needed="Required skill for this role" if is_required else "Nice-to-have skill"
        )
    
    def calculate_phase_weeks(self, skills: List[SkillNode], pace: str) -> float:
        """Calculate total weeks for a phase based on learning pace"""
        base_weeks = sum(s.estimated_weeks for s in skills)
        parallel_factor = 0.7
        
        pace_multipliers = {"intensive": 0.6, "moderate": 1.0, "relaxed": 1.5}
        multiplier = pace_multipliers.get(pace, 1.0)
        
        return round(base_weeks * parallel_factor * multiplier, 1)
    
    def build_phases(
        self, skill_phases: List[List[str]], required_skills: List[str], pace: str
    ) -> tuple[List[LearningPhase], float, int]:
        """Build detailed learning phases"""
        phases = []
        total_weeks = 0
        total_hours = 0
        
        for i, phase_skills in enumerate(skill_phases):
            skill_nodes = [self.get_skill_node(s, required_skills) for s in phase_skills]
            phase_weeks = self.calculate_phase_weeks(skill_nodes, pace)
            phase_hours = sum(sum(r.estimated_hours for r in s.resources) for s in skill_nodes)
            
            phases.append(LearningPhase(
                phase_number=i + 1,
                title=self.PHASE_TITLES[min(i, len(self.PHASE_TITLES) - 1)],
                description=f"Learn {', '.join(s.name for s in skill_nodes)}",
                skills=skill_nodes,
                total_weeks=phase_weeks,
                milestone=self.PHASE_MILESTONES[min(i, len(self.PHASE_MILESTONES) - 1)]
            ))
            
            total_weeks += phase_weeks
            total_hours += phase_hours
        
        return phases, total_weeks, total_hours
    
    @staticmethod
    def get_motivation_message(missing_count: int, weeks: float) -> str:
        """Generate encouraging message based on gap size"""
        if missing_count <= 2:
            return "🚀 You're almost there! Just a few skills to learn."
        elif missing_count <= 5:
            return "💪 A solid learning journey ahead! You'll be job-ready soon."
        elif weeks <= 8:
            return "📚 This is achievable! Many developers have bridged similar gaps."
        return "🎯 A significant but rewarding journey. Celebrate each milestone!"
