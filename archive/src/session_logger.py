"""Session logging for improv jam plans."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
import csv


class SessionLogger:
    """Logs jam session outcomes to a human-readable CSV file."""

    def __init__(self, log_path: str = "data/session_logs.csv"):
        """
        Initialize session logger.

        Args:
            log_path: Path to session log CSV file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_csv()

    def _initialize_csv(self):
        """Create CSV file with header if it does not exist."""
        if not self.log_path.exists():
            with open(self.log_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "SessionID",
                        "Date",
                        "JamPlanFile",
                        "Chapters",
                        "DurationMinutes",
                        "GroupSize",
                        "FrameworksUsed",
                        "ExercisesUsed",
                        "WhatWorked",
                        "WhatDidntWork",
                        "TimingIssues",
                        "ParticipantFeedback",
                        "FacilitatorNotes",
                        "RecordingDate",
                        "RecordingPath",
                        "TranscriptPath",
                    ]
                )

    def log_session(
        self,
        session_id: Optional[str] = None,
        date: Optional[str] = None,
        jam_plan_file: Optional[str] = None,
        chapters: Optional[List[int]] = None,
        duration_minutes: Optional[int] = None,
        group_size: Optional[str] = None,
        frameworks_used: Optional[List[str]] = None,
        exercises_used: Optional[List[str]] = None,
        what_worked: Optional[str] = None,
        what_didnt_work: Optional[str] = None,
        timing_issues: Optional[str] = None,
        participant_feedback: Optional[str] = None,
        facilitator_notes: Optional[str] = None,
        recording_date: Optional[str] = None,
        recording_path: Optional[str] = None,
        transcript_path: Optional[str] = None,
    ):
        """
        Append a single session record to the CSV log.

        Args:
            session_id: Optional explicit session identifier (default: timestamp)
            date: Session date in YYYY-MM-DD format (default: today)
            jam_plan_file: Path or filename of the jam plan used
            chapters: List of chapter numbers used as basis
            duration_minutes: Duration of the main working part in minutes
            group_size: Text description of group size (e.g., "6-10")
            frameworks_used: List of framework names
            exercises_used: List of exercise names
            what_worked: Free-form notes about what worked well
            what_didnt_work: Free-form notes about what did not work
            timing_issues: Notes about timing problems
            participant_feedback: Summary of participant feedback
            facilitator_notes: Extra notes / lessons learned
            recording_date: Date of any recording made
            recording_path: Path or link to recording file
            transcript_path: Path to transcript of recording (future)
        """
        # Defaults
        now = datetime.now()
        if session_id is None:
            session_id = now.strftime("%Y%m%d-%H%M%S")
        if date is None:
            date = now.strftime("%Y-%m-%d")

        chapters_str = ", ".join(str(ch) for ch in chapters) if chapters else ""
        frameworks_str = "; ".join(frameworks_used) if frameworks_used else ""
        exercises_str = "; ".join(exercises_used) if exercises_used else ""

        row = [
            session_id,
            date,
            jam_plan_file or "",
            chapters_str,
            duration_minutes if duration_minutes is not None else "",
            group_size or "",
            frameworks_str,
            exercises_str,
            what_worked or "",
            what_didnt_work or "",
            timing_issues or "",
            participant_feedback or "",
            facilitator_notes or "",
            recording_date or "",
            recording_path or "",
            transcript_path or "",
        ]

        with open(self.log_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)


def log_session_result(
    session_id: Optional[str] = None,
    date: Optional[str] = None,
    jam_plan_file: Optional[str] = None,
    chapters: Optional[List[int]] = None,
    duration_minutes: Optional[int] = None,
    group_size: Optional[str] = None,
    frameworks_used: Optional[List[str]] = None,
    exercises_used: Optional[List[str]] = None,
    what_worked: Optional[str] = None,
    what_didnt_work: Optional[str] = None,
    timing_issues: Optional[str] = None,
    participant_feedback: Optional[str] = None,
    facilitator_notes: Optional[str] = None,
    recording_date: Optional[str] = None,
    recording_path: Optional[str] = None,
    transcript_path: Optional[str] = None,
):
    """
    Convenience wrapper to log a session using the default logger.

    This allows: from session_logger import log_session_result
    and then a single call with keyword arguments.
    """
    logger = SessionLogger()
    logger.log_session(
        session_id=session_id,
        date=date,
        jam_plan_file=jam_plan_file,
        chapters=chapters,
        duration_minutes=duration_minutes,
        group_size=group_size,
        frameworks_used=frameworks_used,
        exercises_used=exercises_used,
        what_worked=what_worked,
        what_didnt_work=what_didnt_work,
        timing_issues=timing_issues,
        participant_feedback=participant_feedback,
        facilitator_notes=facilitator_notes,
        recording_date=recording_date,
        recording_path=recording_path,
        transcript_path=transcript_path,
    )


