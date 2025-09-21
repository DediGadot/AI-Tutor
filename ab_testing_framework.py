"""
Hebrew AI Tutor - A/B Testing Framework for Pedagogical Effectiveness
Statistically rigorous testing for educational approaches with Hebrew-speaking 5th graders
"""

import json
import asyncio
import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import hashlib
from abc import ABC, abstractmethod
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class ExperimentType(Enum):
    HINT_TIMING = "hint_timing"
    COACHING_STYLE = "coaching_style"
    DIFFICULTY_PROGRESSION = "difficulty_progression"
    FEEDBACK_FREQUENCY = "feedback_frequency"
    THEME_EFFECTIVENESS = "theme_effectiveness"
    MILESTONE_STRUCTURE = "milestone_structure"
    TTS_USAGE = "tts_usage"
    VISUAL_FEEDBACK = "visual_feedback"

class ExperimentStatus(Enum):
    DESIGN = "design"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ANALYZED = "analyzed"

class StatisticalSignificance(Enum):
    NOT_SIGNIFICANT = "not_significant"
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # p < 0.10
    SIGNIFICANT = "significant"  # p < 0.05
    HIGHLY_SIGNIFICANT = "highly_significant"  # p < 0.01

@dataclass
class ExperimentHypothesis:
    """Define the experimental hypothesis for pedagogical testing"""
    null_hypothesis: str
    alternative_hypothesis: str
    expected_effect_size: float  # Cohen's d or percentage improvement
    minimum_detectable_effect: float
    practical_significance_threshold: float

@dataclass
class ExperimentDesign:
    """Statistical design parameters for educational experiments"""
    experiment_id: str
    experiment_type: ExperimentType
    hypothesis: ExperimentHypothesis

    # Statistical parameters
    significance_level: float = 0.05  # Alpha
    statistical_power: float = 0.80   # 1 - Beta
    minimum_sample_size: int = 100
    maximum_sample_size: int = 1000

    # Educational context
    target_grade: int = 5
    target_language: str = "he"
    session_duration_minutes: int = 20

    # Experiment conditions
    control_condition: Dict[str, Any] = field(default_factory=dict)
    treatment_condition: Dict[str, Any] = field(default_factory=dict)

    # Success metrics
    primary_metric: str = "learning_effectiveness_score"
    secondary_metrics: List[str] = field(default_factory=lambda: [
        "engagement_duration",
        "milestone_completion_rate",
        "hint_usage_frequency",
        "retention_score"
    ])

    # Ethical constraints
    max_experiment_duration_days: int = 30
    harm_monitoring_enabled: bool = True
    early_stopping_rules: List[str] = field(default_factory=lambda: [
        "significant_harm_detected",
        "futility_threshold_reached",
        "overwhelming_evidence"
    ])

@dataclass
class ParticipantData:
    """Student participant data for experiments"""
    participant_id: str
    experiment_group: str  # "control" or "treatment"
    assignment_timestamp: datetime

    # Demographics (anonymized)
    grade_level: int
    prior_coding_experience: str  # "none", "basic", "intermediate"
    hebrew_proficiency: str  # "native", "fluent", "learning"

    # Baseline measurements
    baseline_scores: Dict[str, float] = field(default_factory=dict)

    # Session data
    sessions: List[Dict[str, Any]] = field(default_factory=list)

    # Outcome measurements
    post_experiment_scores: Dict[str, float] = field(default_factory=dict)

    # Metadata
    last_activity: Optional[datetime] = None
    completed_experiment: bool = False
    withdrawal_reason: Optional[str] = None

@dataclass
class ExperimentResult:
    """Results of a pedagogical A/B test"""
    experiment_id: str
    analysis_timestamp: datetime

    # Sample information
    control_sample_size: int
    treatment_sample_size: int
    total_sample_size: int

    # Primary metric results
    control_mean: float
    treatment_mean: float
    effect_size: float  # Cohen's d
    percentage_improvement: float

    # Statistical test results
    test_statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    significance_level: StatisticalSignificance

    # Secondary metrics
    secondary_results: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Educational insights
    pedagogical_recommendations: List[str] = field(default_factory=list)
    implementation_feasibility: str = ""
    potential_risks: List[str] = field(default_factory=list)

class ExperimentDatabase:
    """SQLite database for experiment data management"""

    def __init__(self, db_path: str = "/home/fiod/ai-tutor2/experiments.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    design_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    participant_id TEXT,
                    experiment_id TEXT,
                    participant_data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (participant_id, experiment_id),
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiment_results (
                    experiment_id TEXT PRIMARY KEY,
                    result_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)

    def save_experiment_design(self, design: ExperimentDesign, status: ExperimentStatus):
        """Save experiment design to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO experiments (experiment_id, design_json, status)
                VALUES (?, ?, ?)
            """, (design.experiment_id, json.dumps(asdict(design)), status.value))

    def save_participant_data(self, participant: ParticipantData, experiment_id: str):
        """Save participant data to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO participants (participant_id, experiment_id, participant_data_json)
                VALUES (?, ?, ?)
            """, (participant.participant_id, experiment_id, json.dumps(asdict(participant))))

    def get_experiment_participants(self, experiment_id: str) -> List[ParticipantData]:
        """Retrieve all participants for an experiment"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT participant_data_json FROM participants WHERE experiment_id = ?
            """, (experiment_id,))

            participants = []
            for row in cursor.fetchall():
                data = json.loads(row[0])
                # Convert datetime strings back to datetime objects
                if data.get('assignment_timestamp'):
                    data['assignment_timestamp'] = datetime.fromisoformat(data['assignment_timestamp'])
                if data.get('last_activity'):
                    data['last_activity'] = datetime.fromisoformat(data['last_activity'])
                participants.append(ParticipantData(**data))

            return participants

class HebrewPedagogyExperiments:
    """Predefined experiments for Hebrew coding education"""

    @staticmethod
    def create_hint_timing_experiment() -> ExperimentDesign:
        """Test optimal timing for providing coding hints"""
        hypothesis = ExperimentHypothesis(
            null_hypothesis="התזמון של הרמזים אינו משפיע על יעילות הלמידה",
            alternative_hypothesis="מתן רמזים מיידי משפר את יעילות הלמידה לעומת רמזים מעוכבים",
            expected_effect_size=0.3,  # Small to medium effect
            minimum_detectable_effect=0.2,
            practical_significance_threshold=0.25
        )

        return ExperimentDesign(
            experiment_id="hint_timing_immediate_vs_delayed",
            experiment_type=ExperimentType.HINT_TIMING,
            hypothesis=hypothesis,
            control_condition={
                "hint_timing": "delayed",
                "delay_seconds": 30,
                "description": "רמזים מופיעים אחרי 30 שניות של מאמץ"
            },
            treatment_condition={
                "hint_timing": "immediate",
                "delay_seconds": 5,
                "description": "רמזים מופיעים מיידי אחרי כישלון"
            },
            primary_metric="time_to_milestone_completion",
            secondary_metrics=[
                "frustration_score",
                "help_seeking_behavior",
                "code_quality_score",
                "self_efficacy_rating"
            ]
        )

    @staticmethod
    def create_coaching_style_experiment() -> ExperimentDesign:
        """Test different coaching communication styles"""
        hypothesis = ExperimentHypothesis(
            null_hypothesis="סגנון התקשורת של המאמן אינו משפיע על מעורבות התלמיד",
            alternative_hypothesis="סגנון תקשורת מעודד ותומך משפר מעורבות ולמידה",
            expected_effect_size=0.4,
            minimum_detectable_effect=0.25,
            practical_significance_threshold=0.3
        )

        return ExperimentDesign(
            experiment_id="coaching_style_supportive_vs_directive",
            experiment_type=ExperimentType.COACHING_STYLE,
            hypothesis=hypothesis,
            control_condition={
                "style": "directive",
                "tone": "instructional",
                "example_message": "הוסף משתנה vx לתנועה אופקית",
                "feedback_type": "corrective"
            },
            treatment_condition={
                "style": "supportive",
                "tone": "encouraging",
                "example_message": "אתה על הדרך הנכונה! בוא ננסה להוסיף משתנה למהירות",
                "feedback_type": "growth_oriented"
            },
            primary_metric="engagement_duration",
            secondary_metrics=[
                "positive_emotion_indicators",
                "persistence_after_failure",
                "voluntary_exploration_time",
                "help_request_frequency"
            ]
        )

    @staticmethod
    def create_theme_effectiveness_experiment() -> ExperimentDesign:
        """Test which game themes are most engaging for Hebrew-speaking students"""
        hypothesis = ExperimentHypothesis(
            null_hypothesis="נושא המשחק אינו משפיע על מעורבות ולמידה",
            alternative_hypothesis="נושא כדורגל מעורר יותר עניין ומעורבות מנושא חלל",
            expected_effect_size=0.35,
            minimum_detectable_effect=0.2,
            practical_significance_threshold=0.25
        )

        return ExperimentDesign(
            experiment_id="theme_football_vs_space",
            experiment_type=ExperimentType.THEME_EFFECTIVENESS,
            hypothesis=hypothesis,
            control_condition={
                "theme": "space",
                "visual_elements": ["rockets", "planets", "stars"],
                "vocabulary_hebrew": ["חללית", "כוכב", "מסלול"],
                "context": "משחקי חלל ואסטרונאוטיקה"
            },
            treatment_condition={
                "theme": "football",
                "visual_elements": ["ball", "goal", "field"],
                "vocabulary_hebrew": ["כדור", "שער", "מגרש"],
                "context": "משחקי כדורגל ובעיטות"
            },
            primary_metric="session_completion_rate",
            secondary_metrics=[
                "time_spent_in_game",
                "voluntary_return_rate",
                "creative_exploration_score",
                "theme_preference_rating"
            ]
        )

class StatisticalAnalyzer:
    """Statistical analysis tools for educational experiments"""

    @staticmethod
    def calculate_sample_size(
        effect_size: float,
        significance_level: float = 0.05,
        power: float = 0.80,
        two_sided: bool = True
    ) -> int:
        """Calculate required sample size using Cohen's conventions"""
        # Simplified sample size calculation (would use scipy.stats in practice)
        # For Cohen's d = 0.3 (small-medium effect), alpha=0.05, power=0.80
        # Approximate sample sizes per group:
        effect_to_n = {
            0.2: 393,  # Small effect
            0.3: 175,  # Small-medium effect
            0.5: 63,   # Medium effect
            0.8: 25    # Large effect
        }

        # Find closest effect size
        closest_effect = min(effect_to_n.keys(), key=lambda x: abs(x - effect_size))
        base_n = effect_to_n[closest_effect]

        # Adjust for actual effect size
        adjustment_factor = (closest_effect / effect_size) ** 2
        required_n = int(base_n * adjustment_factor)

        # Add 20% for dropout
        return int(required_n * 1.2)

    @staticmethod
    def perform_t_test(
        control_group: List[float],
        treatment_group: List[float],
        significance_level: float = 0.05
    ) -> Dict[str, float]:
        """Perform two-sample t-test (simplified implementation)"""

        n1, n2 = len(control_group), len(treatment_group)
        mean1, mean2 = np.mean(control_group), np.mean(treatment_group)
        var1, var2 = np.var(control_group, ddof=1), np.var(treatment_group, ddof=1)

        # Pooled standard error
        pooled_se = np.sqrt(var1/n1 + var2/n2)

        # T-statistic
        t_stat = (mean2 - mean1) / pooled_se

        # Degrees of freedom (Welch's approximation)
        df = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        cohens_d = (mean2 - mean1) / pooled_std

        # Simplified p-value calculation (would use scipy.stats.t.cdf in practice)
        # For demonstration, using approximation
        p_value = 2 * (1 - abs(t_stat) / (abs(t_stat) + np.sqrt(df)))

        # Confidence interval (95%)
        margin_error = 1.96 * pooled_se  # Approximation
        ci_lower = (mean2 - mean1) - margin_error
        ci_upper = (mean2 - mean1) + margin_error

        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "cohens_d": cohens_d,
            "mean_difference": mean2 - mean1,
            "confidence_interval": (ci_lower, ci_upper),
            "control_mean": mean1,
            "treatment_mean": mean2
        }

    @staticmethod
    def determine_significance(p_value: float) -> StatisticalSignificance:
        """Determine statistical significance level"""
        if p_value < 0.01:
            return StatisticalSignificance.HIGHLY_SIGNIFICANT
        elif p_value < 0.05:
            return StatisticalSignificance.SIGNIFICANT
        elif p_value < 0.10:
            return StatisticalSignificance.MARGINALLY_SIGNIFICANT
        else:
            return StatisticalSignificance.NOT_SIGNIFICANT

class ExperimentOrchestrator:
    """Main class for managing pedagogical A/B tests"""

    def __init__(self, db_path: str = "/home/fiod/ai-tutor2/experiments.db"):
        self.db = ExperimentDatabase(db_path)
        self.active_experiments: Dict[str, ExperimentDesign] = {}
        self.hebrew_pedagogy = HebrewPedagogyExperiments()
        self.analyzer = StatisticalAnalyzer()

    def create_experiment(self, design: ExperimentDesign) -> bool:
        """Create and initialize a new experiment"""
        try:
            # Validate experiment design
            if not self._validate_experiment_design(design):
                return False

            # Calculate required sample size
            required_n = self.analyzer.calculate_sample_size(
                design.hypothesis.expected_effect_size,
                design.significance_level,
                design.statistical_power
            )

            # Update design with calculated sample size
            design.minimum_sample_size = required_n

            # Save to database
            self.db.save_experiment_design(design, ExperimentStatus.DESIGN)

            logger.info(f"Created experiment: {design.experiment_id}")
            logger.info(f"Required sample size: {required_n} per group")

            return True

        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            return False

    def assign_participant(
        self,
        student_id: str,
        experiment_id: str,
        baseline_data: Dict[str, Any]
    ) -> Optional[str]:
        """Assign student to control or treatment group"""

        # Generate consistent assignment based on student ID
        assignment_hash = hashlib.md5(f"{student_id}_{experiment_id}".encode()).hexdigest()
        assignment = "treatment" if int(assignment_hash, 16) % 2 else "control"

        participant = ParticipantData(
            participant_id=student_id,
            experiment_group=assignment,
            assignment_timestamp=datetime.now(),
            grade_level=baseline_data.get("grade_level", 5),
            prior_coding_experience=baseline_data.get("prior_experience", "none"),
            hebrew_proficiency=baseline_data.get("hebrew_proficiency", "native"),
            baseline_scores=baseline_data.get("baseline_scores", {})
        )

        self.db.save_participant_data(participant, experiment_id)

        logger.info(f"Assigned student {student_id} to {assignment} group in {experiment_id}")
        return assignment

    def record_session_data(
        self,
        student_id: str,
        experiment_id: str,
        session_data: Dict[str, Any]
    ) -> bool:
        """Record session data for experiment participant"""

        try:
            participants = self.db.get_experiment_participants(experiment_id)
            participant = next((p for p in participants if p.participant_id == student_id), None)

            if not participant:
                logger.error(f"Participant {student_id} not found in experiment {experiment_id}")
                return False

            # Add session data
            session_data["timestamp"] = datetime.now().isoformat()
            participant.sessions.append(session_data)
            participant.last_activity = datetime.now()

            # Update database
            self.db.save_participant_data(participant, experiment_id)

            return True

        except Exception as e:
            logger.error(f"Failed to record session data: {e}")
            return False

    def analyze_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Perform statistical analysis of experiment results"""

        try:
            participants = self.db.get_experiment_participants(experiment_id)

            if len(participants) < 20:  # Minimum for meaningful analysis
                logger.warning(f"Insufficient sample size for {experiment_id}")
                return None

            # Separate control and treatment groups
            control_group = [p for p in participants if p.experiment_group == "control"]
            treatment_group = [p for p in participants if p.experiment_group == "treatment"]

            # Extract primary metric values
            control_scores = self._extract_metric_scores(control_group, "learning_effectiveness_score")
            treatment_scores = self._extract_metric_scores(treatment_group, "learning_effectiveness_score")

            if not control_scores or not treatment_scores:
                logger.error("Insufficient data for statistical analysis")
                return None

            # Perform statistical test
            test_results = self.analyzer.perform_t_test(control_scores, treatment_scores)

            # Create result object
            result = ExperimentResult(
                experiment_id=experiment_id,
                analysis_timestamp=datetime.now(),
                control_sample_size=len(control_group),
                treatment_sample_size=len(treatment_group),
                total_sample_size=len(participants),
                control_mean=test_results["control_mean"],
                treatment_mean=test_results["treatment_mean"],
                effect_size=test_results["cohens_d"],
                percentage_improvement=(test_results["mean_difference"] / test_results["control_mean"]) * 100,
                test_statistic=test_results["t_statistic"],
                p_value=test_results["p_value"],
                confidence_interval=test_results["confidence_interval"],
                significance_level=self.analyzer.determine_significance(test_results["p_value"])
            )

            # Generate pedagogical recommendations
            result.pedagogical_recommendations = self._generate_recommendations(result)

            # Save results
            with sqlite3.connect(self.db.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO experiment_results (experiment_id, result_json)
                    VALUES (?, ?)
                """, (experiment_id, json.dumps(asdict(result), default=str)))

            logger.info(f"Analysis completed for {experiment_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze experiment {experiment_id}: {e}")
            return None

    def _validate_experiment_design(self, design: ExperimentDesign) -> bool:
        """Validate experiment design for educational ethics and feasibility"""

        # Check if experiment duration is reasonable
        if design.max_experiment_duration_days > 60:
            logger.error("Experiment duration too long for student participants")
            return False

        # Ensure harm monitoring is enabled
        if not design.harm_monitoring_enabled:
            logger.error("Harm monitoring must be enabled for student experiments")
            return False

        # Validate sample size constraints
        if design.minimum_sample_size > design.maximum_sample_size:
            logger.error("Minimum sample size exceeds maximum")
            return False

        return True

    def _extract_metric_scores(self, participants: List[ParticipantData], metric: str) -> List[float]:
        """Extract metric scores from participant data"""
        scores = []

        for participant in participants:
            # Calculate metric based on session data
            if metric == "learning_effectiveness_score":
                # Composite score based on multiple factors
                session_scores = []
                for session in participant.sessions:
                    milestones_completed = session.get("milestones_completed", 0)
                    session_duration = session.get("duration_minutes", 20)
                    hints_used = session.get("hints_used", 0)

                    # Learning effectiveness formula
                    effectiveness = (milestones_completed / session_duration) * 20
                    effectiveness -= (hints_used * 0.1)  # Penalty for excessive hints
                    session_scores.append(max(0, effectiveness))

                if session_scores:
                    scores.append(np.mean(session_scores))

        return scores

    def _generate_recommendations(self, result: ExperimentResult) -> List[str]:
        """Generate pedagogical recommendations based on experiment results"""
        recommendations = []

        if result.significance_level in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]:
            if result.percentage_improvement > 10:
                recommendations.append(f"התערבות הטיפול הראתה שיפור של {result.percentage_improvement:.1f}% - מומלץ ליישום")
                recommendations.append("יש לבחון את ההשפעה על תתי-קבוצות שונות של תלמידים")
            else:
                recommendations.append("השיפור סטטיסטית מובהק אך קטן מבחינה מעשית")
        else:
            recommendations.append("לא נמצא הבדל מובהק בין הקבוצות")
            recommendations.append("יש לבחון אם גודל המדגם מספיק או לשנות את התערבות הטיפול")

        # Effect size interpretation
        if abs(result.effect_size) < 0.2:
            recommendations.append("גודל האפקט קטן - השפעה מוגבלת על הלמידה")
        elif abs(result.effect_size) < 0.5:
            recommendations.append("גודל אפקט בינוני - שיפור ניכר בלמידה")
        else:
            recommendations.append("גודל אפקט גדול - השפעה משמעותית על הלמידה")

        return recommendations

# Example usage and experiment templates
async def run_sample_experiment():
    """Demonstrate the A/B testing framework"""

    # Initialize orchestrator
    orchestrator = ExperimentOrchestrator()

    # Create hint timing experiment
    hint_experiment = HebrewPedagogyExperiments.create_hint_timing_experiment()
    success = orchestrator.create_experiment(hint_experiment)

    if success:
        print(f"Created experiment: {hint_experiment.experiment_id}")
        print(f"Required sample size: {hint_experiment.minimum_sample_size} per group")

        # Simulate participant assignment and data collection
        for i in range(50):
            student_id = f"student_{i:03d}"
            baseline_data = {
                "grade_level": 5,
                "prior_experience": random.choice(["none", "basic"]),
                "hebrew_proficiency": "native",
                "baseline_scores": {"pre_test": random.normalvariate(50, 10)}
            }

            assignment = orchestrator.assign_participant(
                student_id, hint_experiment.experiment_id, baseline_data
            )

            # Simulate session data
            session_data = {
                "milestones_completed": random.randint(2, 5),
                "duration_minutes": random.randint(15, 22),
                "hints_used": random.randint(0, 3) if assignment == "control" else random.randint(0, 2),
                "theme": "football"
            }

            orchestrator.record_session_data(
                student_id, hint_experiment.experiment_id, session_data
            )

        # Analyze results
        result = orchestrator.analyze_experiment(hint_experiment.experiment_id)

        if result:
            print(f"\nExperiment Results:")
            print(f"Control group mean: {result.control_mean:.2f}")
            print(f"Treatment group mean: {result.treatment_mean:.2f}")
            print(f"Effect size (Cohen's d): {result.effect_size:.3f}")
            print(f"P-value: {result.p_value:.4f}")
            print(f"Significance: {result.significance_level.value}")
            print(f"Percentage improvement: {result.percentage_improvement:.1f}%")
            print(f"\nRecommendations:")
            for rec in result.pedagogical_recommendations:
                print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(run_sample_experiment())