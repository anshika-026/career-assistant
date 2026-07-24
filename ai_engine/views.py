from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from jobs.models import JobDescription, JobMatch
from .models import InterviewSession, LearningRecommendation
from .serializers import InterviewSessionSerializer, LearningRecommendationSerializer
from .claude_client import generate_interview_questions, generate_learning_recommendations
from analysis.scoring import extract_skills


class GenerateInterviewQuestionsView(APIView):
    """
    POST /api/ai/interview-questions/<resume_id>/
    Optional body: {"job_id": <id>} to tailor questions to a specific job.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, resume_id):
        try:
            resume = Resume.objects.get(pk=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

        if resume.parsing_status != Resume.ParsingStatus.PARSED:
            raise ValidationError({"detail": "Resume hasn't been successfully parsed yet."})

        job = None
        job_id = request.data.get("job_id")
        job_title = "the target role"
        if job_id:
            try:
                job = JobDescription.objects.get(pk=job_id, user=request.user)
                job_title = job.title
            except JobDescription.DoesNotExist:
                return Response({"detail": "Job description not found."}, status=status.HTTP_404_NOT_FOUND)

        skills = list(extract_skills(resume.parsed_text).keys())
        questions = generate_interview_questions(job_title, skills)

        session = InterviewSession.objects.create(
            user=request.user, resume=resume, job=job, questions=questions,
        )
        return Response(InterviewSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class InterviewSessionListView(generics.ListAPIView):
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user)


class GenerateLearningRecommendationsView(APIView):
    """POST /api/ai/learning-recommendations/<job_match_id>/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_match_id):
        try:
            job_match = JobMatch.objects.get(pk=job_match_id, user=request.user)
        except JobMatch.DoesNotExist:
            return Response({"detail": "Job match not found."}, status=status.HTTP_404_NOT_FOUND)

        recommendations = generate_learning_recommendations(job_match.missing_skills)

        rec = LearningRecommendation.objects.create(
            user=request.user, job_match=job_match, recommendations=recommendations,
        )
        return Response(LearningRecommendationSerializer(rec).data, status=status.HTTP_201_CREATED)


class LearningRecommendationListView(generics.ListAPIView):
    serializer_class = LearningRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningRecommendation.objects.filter(user=self.request.user)
