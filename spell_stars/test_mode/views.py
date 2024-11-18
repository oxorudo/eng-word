import os
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import TestResult  # TestResult 모델을 import
from vocab_mode.models import Word
from sent_mode.models import Sentence
from accounts.models import StudentInfo
import warnings
from django.apps import apps
from django.core.files.base import ContentFile
from accounts.views import start_learning_session

warnings.filterwarnings("ignore", category=FutureWarning)

model = apps.get_app_config('spell_stars').whisper_model

# 문제 수와 총점
TOTAL_QUESTIONS = 20
MAX_SCORE = 100
POINTS_PER_QUESTION = MAX_SCORE / TOTAL_QUESTIONS  # 1문제당 점수 계산


def calculate_score(
    correct_answers, total_questions=TOTAL_QUESTIONS, max_score=MAX_SCORE
):
    # 맞힌 문제 수에 따라 점수를 계산
    score = correct_answers * (max_score / total_questions)
    return round(score, 2)


def test_mode_view(request):
    print("test_mode_view called")

    # 단어 선택 동적으로 처리
    random_word_ids = Word.objects.values_list("id", flat=True).order_by("?")[:TOTAL_QUESTIONS]

    if random_word_ids:
        sentences = []
        for word_id in random_word_ids:
            sentence = Sentence.objects.filter(word_id=word_id).order_by("?").first()
            word = Word.objects.get(id=word_id)
            if sentence:
                sentence_with_blank = sentence.sentence.replace(word.word, "_____")
                sentences.append(
                    {
                        "sentence": sentence_with_blank,
                        "word": word.word,
                        "question_id": sentence.id,
                        "sentence_meaning": sentence.sentence_meaning
                    }
                )

        if not sentences:
            return JsonResponse(
                {"error": "No sentences found for the selected words."}, status=404
            )

        # 첫 번째 문제 세션에 저장
        request.session["questions"] = sentences
        request.session["current_question_index"] = 0

        # 첫 번째 문제 렌더링
        current_question = sentences[0]
        request.session["target_word"] = current_question["word"]  # target_word 설정
        
        # 학습 시작 로그 생성
        start_learning_session(request, learning_mode=1)  # test 1번
        
        return render(
            request,
            "test_mode/test_page.html",
            {
                "sentence": current_question["sentence"],
                "word": current_question["word"],
                "question_id": current_question["question_id"],
                "sentence_meaning": current_question["sentence_meaning"],
            },
        )
    else:
        return JsonResponse(
            {"error": "No words available in the database."}, status=404
        )


def submit_audio(request, question_id):
    print(f"submit_audio called for question_id: {question_id}")
    
    if request.method == "POST" and request.FILES.get("audio"):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        try:
            student_info = StudentInfo.objects.get(user=request.user)  # 현재 로그인한 사용자의 정보를 가져옴
            user_id = student_info.user.id  # user_id를 가져옴 (User 모델의 id)

            word = request.POST.get("word")
            if not word:
                return JsonResponse(
                    {"status": "error", "message": "Word is required"}, status=400
                )

            # 저장 경로 설정
            save_path = f"test_mode/user_{user_id}/"
            os.makedirs(os.path.join(settings.MEDIA_ROOT, save_path), exist_ok=True)

            # 파일 이름 설정
            file_name = f"{word}_student.wav"
            file_path = os.path.join(save_path, file_name)

            # 기존 파일이 있으면 삭제
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

            # 새 파일 저장
            full_path = default_storage.save(
                file_path, ContentFile(request.FILES["audio"].read())
            )

            # Whisper 모델로 음성 텍스트 변환
            result = model.transcribe(file_path, language="en")
            transcript = result["text"]
            print(f"Transcript from Whisper: {transcript}")

            # 예문에서 정답 단어와 비교하여 점수 계산
            target_word = request.session.get("target_word")
            is_correct = target_word.lower() in transcript.lower()

            # 점수 업데이트
            user = request.user
            correct_answers = 1 if is_correct else 0
            test_date = request.POST.get("test_date", None)  # 시험 날짜는 요청으로 받음

            # 시험 결과 저장
            save_test_result(user, correct_answers, test_date)

            # 음성 파일 URL 반환
            audio_url = os.path.join(settings.MEDIA_URL, "test_mode", file_name)
            return JsonResponse(
                {
                    "transcript": transcript,
                    "audio_url": audio_url,
                    "is_correct": is_correct,
                }
            )

        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
            return JsonResponse(
                {"error": f"Failed to transcribe audio: {str(e)}"}, status=500
            )

    # 파일이 없을 경우
    print("No audio file received in request")
    return JsonResponse({"error": "No audio file received"}, status=400)


def save_test_result(user, correct_answers, test_date):
    # 점수 계산
    score = calculate_score(correct_answers)

    # 시험 결과 저장
    result = TestResult(user=user, score=score, test_date=test_date)
    result.save()
    print(f"Test result saved: {result}")


def next_question(request):
    print("next_question called")

    # 세션에서 현재 질문 인덱스와 질문 목록 가져오기
    current_index = request.session.get("current_question_index", 0)
    questions = request.session.get("questions", [])

    if not questions:
        return JsonResponse({"error": "No questions available."}, status=404)

    if current_index < len(questions) - 1:
        # 다음 문제로 이동
        next_index = current_index + 1
        next_question = questions[next_index]

        # 세션에 현재 질문 인덱스 업데이트
        request.session["current_question_index"] = next_index

        return JsonResponse(
            {
                "success": True,
                "sentence": next_question["sentence"],
                "word": next_question["word"],
                "question_id": next_question["question_id"],
            }
        )
    else:
        # 문제가 모두 끝났으면 종료 메시지
        return JsonResponse(
            {"success": False, "message": "All questions have been answered."}
        )
