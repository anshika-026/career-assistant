from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from resumes.models import Resume
from .models import AnalysisResult
from .serializers import AnalysisResultSerializer
from .scoring import score_resume


class AnalyzeResumeView(APIView):
    """
    POST /api/analysis/analyze/<resume_id>/ -- run ATS scoring on a parsed resume.
    Requires the resume to have parsing_status == 'parsed'.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, resume_id):
        try:
            resume = Resume.objects.get(pk=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

        if resume.parsing_status != Resume.ParsingStatus.PARSED:
            raise ValidationError(
                {"detail": "Resume text hasn't been successfully parsed yet. "
                            "Try /api/resumes/<id>/reparse/ first."}
            )

        result = score_resume(resume.parsed_text)

        analysis = AnalysisResult.objects.create(
            resume=resume,
            user=request.user,
            ats_score=result["ats_score"],
            word_count=result["word_count"],
            sections_found=result["sections_found"],
            contact_info=result["contact_info"],
            skills_found=result["skills_found"],
            score_breakdown=result["score_breakdown"],
            issues=result["issues"],
        )
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)


class AnalysisListView(generics.ListAPIView):
    """GET /api/analysis/ -- list all of the current user's past analyses (newest first)."""
    serializer_class = AnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AnalysisResult.objects.filter(user=self.request.user)


class AnalysisDetailView(generics.RetrieveAPIView):
    """GET /api/analysis/<id>/ -- retrieve one analysis result."""
    serializer_class = AnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AnalysisResult.objects.filter(user=self.request.user)
