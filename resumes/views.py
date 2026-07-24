from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Resume
from .serializers import ResumeSerializer
from .parsing import extract_resume_text, UnsupportedFileTypeError, EmptyResumeError

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class ResumeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/resumes/       -- list current user's resumes
    POST /api/resumes/       -- upload a new resume (multipart/form-data, field: 'file')
                                 Text is extracted synchronously on upload.
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            raise ValidationError({"file": "No file was uploaded."})

        file_type = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
        if file_type not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                {"file": f"Unsupported file type '.{file_type}'. Only PDF and DOCX are allowed."}
            )
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            raise ValidationError({"file": "File too large. Max size is 5MB."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resume = serializer.save(
            user=request.user,
            original_filename=uploaded_file.name,
            file_type=file_type,
        )

        # Parse synchronously for now. For large files or scale, move this
        # to a Celery task and return parsing_status=PENDING immediately.
        self._parse_and_save(resume, uploaded_file)

        resume.refresh_from_db()
        out_serializer = self.get_serializer(resume)
        headers = self.get_success_headers(out_serializer.data)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _parse_and_save(self, resume, uploaded_file):
        try:
            text = extract_resume_text(uploaded_file, resume.file_type)
        except (UnsupportedFileTypeError, EmptyResumeError) as exc:
            resume.parsing_status = Resume.ParsingStatus.FAILED
            resume.parsing_error = str(exc)
            resume.save(update_fields=["parsing_status", "parsing_error"])
            return

        resume.parsed_text = text
        resume.word_count = len(text.split())
        resume.parsing_status = Resume.ParsingStatus.PARSED
        resume.parsing_error = ""
        resume.save(update_fields=["parsed_text", "word_count", "parsing_status", "parsing_error"])


class ResumeReparseView(APIView):
    """
    POST /api/resumes/<id>/reparse/ -- re-run text extraction on an existing
    resume (useful if parsing failed the first time, or the parser improved).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            resume = Resume.objects.get(pk=pk, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            text = extract_resume_text(resume.file, resume.file_type)
        except (UnsupportedFileTypeError, EmptyResumeError) as exc:
            resume.parsing_status = Resume.ParsingStatus.FAILED
            resume.parsing_error = str(exc)
            resume.save(update_fields=["parsing_status", "parsing_error"])
            return Response(ResumeSerializer(resume).data, status=status.HTTP_200_OK)

        resume.parsed_text = text
        resume.word_count = len(text.split())
        resume.parsing_status = Resume.ParsingStatus.PARSED
        resume.parsing_error = ""
        resume.save(update_fields=["parsed_text", "word_count", "parsing_status", "parsing_error"])
        return Response(ResumeSerializer(resume).data, status=status.HTTP_200_OK)


class ResumeDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/resumes/<id>/ -- retrieve one resume (includes parsed_text)
    DELETE /api/resumes/<id>/ -- delete a resume
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
