from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from analysis.models import AnalysisResult
from jobs.models import JobMatch
from ai_engine.models import InterviewSession


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    One-stop endpoint for the frontend dashboard: latest score, score
    history for a trend chart, resume/job-match counts, and top skill gaps
    across all job matches (useful for "what should I learn next").
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        analyses = AnalysisResult.objects.filter(user=user).order_by("created_at")
        score_history = [
            {"date": a.created_at.strftime("%Y-%m-%d"), "score": a.ats_score}
            for a in analyses
        ]
        latest_score = analyses.last().ats_score if analyses.exists() else None

        job_matches = JobMatch.objects.filter(user=user)
        match_history = [
            {"date": m.created_at.strftime("%Y-%m-%d"), "score": m.match_score, "job_title": m.job.title}
            for m in job_matches.order_by("created_at")
        ]

        # Tally how often each missing skill shows up across all job matches
        skill_gap_counts = {}
        for match in job_matches:
            for skill in match.missing_skills:
                skill_gap_counts[skill] = skill_gap_counts.get(skill, 0) + 1
        top_skill_gaps = sorted(skill_gap_counts.items(), key=lambda kv: -kv[1])[:10]

        return Response({
            "resume_count": Resume.objects.filter(user=user).count(),
            "analysis_count": analyses.count(),
            "job_match_count": job_matches.count(),
            "interview_session_count": InterviewSession.objects.filter(user=user).count(),
            "latest_ats_score": latest_score,
            "ats_score_history": score_history,
            "job_match_history": match_history,
            "top_skill_gaps": [{"skill": s, "count": c} for s, c in top_skill_gaps],
        })
