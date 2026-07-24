from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from .models import JobDescription, JobMatch
from .serializers import JobDescriptionSerializer, JobMatchSerializer
from .matching import match_resume_to_job
from analysis.scoring import extract_skills


class JobDescriptionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/jobs/               -- list your saved job descriptions
    POST /api/jobs/               -- save a new job description (title, company, raw_text)
    """
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        raw_text = serializer.validated_data["raw_text"]
        required_skills = extract_skills(raw_text)
        serializer.save(user=self.request.user, required_skills=required_skills)


class JobDescriptionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)


class MatchResumeToJobView(APIView):
    """
    POST /api/jobs/<job_id>/match/<resume_id>/ -- compare a resume against a
    saved job description, store and return the match result (score, matched
    skills, missing skills / skill gap).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id, resume_id):
        try:
            job = JobDescription.objects.get(pk=job_id, user=request.user)
            resume = Resume.objects.get(pk=resume_id, user=request.user)
        except JobDescription.DoesNotExist:
            return Response({"detail": "Job description not found."}, status=status.HTTP_404_NOT_FOUND)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

        if resume.parsing_status != Resume.ParsingStatus.PARSED:
            raise ValidationError({"detail": "Resume hasn't been successfully parsed yet."})

        result = match_resume_to_job(resume.parsed_text, job.raw_text)

        match = JobMatch.objects.create(
            resume=resume,
            job=job,
            user=request.user,
            match_score=result["match_score"],
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"],
        )
        return Response(JobMatchSerializer(match).data, status=status.HTTP_201_CREATED)


class JobMatchListView(generics.ListAPIView):
    """GET /api/jobs/matches/ -- list all past job matches for the current user."""
    serializer_class = JobMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user)
