import os
import random
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# from utils.PronunciationChecker.manage import process_audio_files
from .models import Word
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from .serializers import WordSerializer
from rest_framework import filters


def display_vocabulary_book(request):
    # words = Word.objects.all().order_by("category", "word")
    # for word in words:
    #     print(word.word, word.meanings, word.examples,word.file_path)  # 데이터 구조 확인
    # context = {"words": words, "MEDIA_URL": settings.MEDIA_URL}
    all_words = list(Word.objects.all())
    random_words = random.sample(all_words, min(len(all_words), 15))  # 단어가 15개 미만인 경우 전체를 사용
    
    context = {"words": random_words, "MEDIA_URL": settings.MEDIA_URL}
    return render(request, "vocab_mode/vocab.html", context)


@csrf_exempt
def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio"):
        try:
            audio_file = request.FILES["audio"]
            current_word = request.POST.get("word", "unknown")
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            
            # 저장 경로 설정
            save_path = f"audio_files/students/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{current_word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(audio_file.read())
            )
            
            return JsonResponse({
                "status": "success",
                "message": "녹음이 완료되었습니다.",
                "file_path": full_path
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "잘못된 요청입니다."
    }, status=400)


### API
# 단어 목록 GET API
class WordPagination(PageNumberPagination):
    page_size = 100


class WordListAPIView(ListAPIView):
    queryset = Word.objects.all().order_by("category", "word")
    serializer_class = WordSerializer
    pagination_class = WordPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["word", "meanings"]  # 정확히 일치하는 단어로 검색