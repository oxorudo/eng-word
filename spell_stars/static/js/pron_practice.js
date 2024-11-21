document.addEventListener('DOMContentLoaded', function () {
    const playButton = document.getElementById('playAudioButton');
    const audioPlayer = document.getElementById('audioPlayer');
    const micButton = document.getElementById('micButton');
    const statusText = document.querySelector('.status-text');
    const voiceLevelFill = document.querySelector('.voice-level-fill');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // beforeunload 이벤트 리스너 추가
    window.addEventListener('beforeunload', function(e) {
        fetch('/accounts/end-learning/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    });

    // 페이지 로드 후 오디오 준비 (자동 재생 X)
    window.onload = function () {
        if (audioPlayer) {
            console.log('오디오 로드:', audioPlayer.src);
            audioPlayer.load();
        }
    };

    // 오디오 재생 버튼 이벤트
    if (playButton && audioPlayer) {
        playButton.addEventListener('click', function () {
            if (audioPlayer.src) {
                console.log('오디오 재생 시도:', audioPlayer.src);
                audioPlayer.load();
                audioPlayer.play()
                    .then(() => {
                        console.log('오디오 재생 성공');
                    })
                    .catch(function (error) {
                        console.error('오디오 재생 오류:', error);
                    });
            } else {
                console.error('오디오 소스가 없습니다');
            }
        });
    }

    // 마이크 버튼 이벤트
    if (micButton) {
        micButton.addEventListener('click', async function () {
            if (!isRecording) {
                try {
                    console.log('마이크 접근 시도...');
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    console.log('마이크 접근 성공');
                    startRecording(stream);
                } catch (err) {
                    console.error('마이크 접근 오류:', err);
                    statusText.textContent = '마이크 접근이 거부되었습니다.';
                }
            } else {
                console.log('녹음 중... 녹음 종료');
                stopRecording();
            }
        });
    }

    // 녹음 시작
    function startRecording(stream) {
        console.log('녹음 시작');
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;

        mediaRecorder.addEventListener('dataavailable', event => {
            console.log('오디오 데이터 수집:', event.data);
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
            console.log('녹음 종료');
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

            const formData = new FormData();
            const targetedWord = document.getElementById('current-word').textContent; 
            formData.append('audio', audioBlob, `${targetedWord}.wav`);
            formData.append('word', targetedWord);

            const uploadAudioUrl = '/practice/upload_audio/';
            try {
                console.log('오디오 업로드 시도');
                const response = await fetch(uploadAudioUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();
                console.log('서버 응답:', data);
                if (data.status === 'success') {
                    statusText.textContent = '녹음이 성공적으로 저장되었습니다.';
                    if (audioPlayer) {
                        audioPlayer.src = '/' + data.file_path;
                    }

                    // 서버에서 점수 받기
                    if (data.score !== undefined) {
                        console.log('서버에서 받은 점수:', data.score);  // 점수 출력
                        displayFeedback(data.score);  // 점수 표시
                    }
                } else {
                    statusText.textContent = '녹음 저장에 실패했습니다.';
                }
            } catch (error) {
                console.error('녹음 저장 오류:', error);
                statusText.textContent = '녹음 저장 중 오류가 발생했습니다.';
            }
        });

        mediaRecorder.start();
        statusText.textContent = '녹음 중...';
        micButton.classList.add('recording');

        // 음성 레벨 표시
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function updateVoiceLevel() {
            if (isRecording) {
                analyser.getByteFrequencyData(dataArray);
                const average = dataArray.reduce((a, b) => a + b) / bufferLength;
                const level = (average / 128) * 100;  // 음성 레벨 계산 수정
                voiceLevelFill.style.width = `${level}%`;  // 여기도 높이로 변경
                requestAnimationFrame(updateVoiceLevel);
            }
        }
        updateVoiceLevel();
    }

    // 녹음 종료
    function stopRecording() {
        console.log('녹음 종료 함수 실행');
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            statusText.textContent = '녹음이 완료되었습니다.';
            micButton.classList.remove('recording');
            voiceLevelFill.style.width = '0%';
        }
    }

    // 피드백 표시
    function displayFeedback(score) {
        console.log(`점수: ${score}`);
        document.getElementById("score").textContent = score;  // 점수 업데이트
        document.getElementById("score-bar").style.width = score + "%";  // 점수에 맞는 프로그레스 바 업데이트

        const progressBar = document.getElementById('score-bar');
        if (score >= 80) {
            progressBar.className = 'green';  // 80점 이상은 녹색
        } else if (score >= 60) {
            progressBar.className = 'yellow';  // 60점 이상은 노란색
        } else {
            progressBar.className = 'red';  // 그 외 점수는 빨간색
        }
    }

    // 다음 단어로 이동
    function nextWord() {
        console.log('다음 단어 요청');
        fetch('/practice/next_word/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('다음 단어 응답:', data);
            if (data.success) {
                // 단어 갱신
                document.getElementById('current-word').textContent = data.nextWord;

                // 뜻 갱신
                document.getElementById('current-meaning').textContent = data.nextMeanings;

                // 오디오 파일 경로 갱신
                const audioPreview = document.getElementById('native-audio-preview');
                const source = audioPreview.querySelector('source');
                source.src = `/media/${data.nextFilePath}`;
                audioPreview.load();

                // 점수 초기화 및 갱신
                document.getElementById("score").textContent = '0';
                document.getElementById("score-bar").style.width = '0%';
                document.getElementById("feedback").textContent = '';
                document.getElementById("feedback-section").style.display = 'none';
            } else {
                console.log('새 단어를 가져오지 못했습니다.');
            }
        })
        .catch(error => {
            console.error('AJAX 요청 오류:', error);
        });
    }


    // 연습 종료
    function exitPractice() {
        console.log('연습 종료');
        window.location.href = '/';
    }

    // 이벤트 리스너 추가
    const nextWordButton = document.getElementById("nextWordButton");
    const exitPracticeButton = document.getElementById("exitPracticeButton");

    if (nextWordButton) {
        nextWordButton.addEventListener('click', nextWord);
    }

    if (exitPracticeButton) {
        exitPracticeButton.addEventListener('click', exitPractice);
    }
});
