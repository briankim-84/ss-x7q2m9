# Scroll & Speak (S&S) — 클립 추가 작업 지침

학생용 영어 학습 피드. 유튜브 토크쇼·인터뷰 클립에 한/영 자막과 핵심 표현 3개를 붙여 추가한다.
Brian이 "링크 + 구간(+ 인물)"을 주면 아래 순서대로 끝까지 진행하고, 표현 후보 확인만 Brian에게 받는다.

## 준비 (최초 1회)
- ffmpeg, python 3.10+ 가 PATH에 있어야 함
- `pip install -r tools/requirements.txt`
- 번호는 feed.json 마지막 id 다음 번호 (예: ss042 → 043)

## 클립 선정 (Brian이 "다음 클립 찾아줘"라고 할 때)

1. 최근 1~2주 안에 올라온 토크쇼·인터뷰 영상을 찾는다. 우선 채널: The Tonight Show, Jimmy Kimmel Live, Late Night with Seth Meyers, Vogue, Zane Lowe. 웹 검색이나 `yt-dlp --flat-playlist --playlist-end 30 --print "%(id)s | %(duration_string)s | %(title)s" <채널 URL>/videos`로 목록을 뽑는다.
2. 인물 기준: **한국 사람이 얼굴만 봐도 멈추는 사람** (K-pop, 한국계 배우, 할리우드 A급). 인지도 낮은 인물은 내용이 좋아도 뒤로.
3. 후보 영상의 자동 자막을 받는다: `yt-dlp --skip-download --write-auto-subs --sub-langs "en.*" --sub-format vtt -o work/sub_<id> <url>`. 자막을 읽고 **15~90초짜리 대화 구간**을 고른다.
   - 좋은 구간: 짧은 질문–대답이 오가고, 일상·업무에서 쓸 chunk가 3개 이상 나오는 곳. 작은 반전이나 웃음이 있으면 더 좋다.
   - 피할 구간: 등장 직후 환호·인사, 게임 코너, 외국어 섞인 부분, 음식 시식 같은 리액션 위주 구간.
4. Brian에게 이렇게 보고하고 멈춘다 — 영상 링크, 구간(분:초~분:초), 왜 좋은지 두세 줄, 뽑힐 chunk 후보. 후보는 2~3개, 순위를 매겨서.
5. Brian이 고르면 위 "순서"의 1번부터 진행한다.

이미 feed.json에 있는 인물·영상은 다시 고르지 않는다 (source와 cues 내용으로 확인).

## 순서

1. **내려받기** `python tools/fetch.py <id> <url> <start> <end>` → work/<id>_raw.mp4 (앞뒤 1초 여유 포함)
2. **전사** `python tools/transcribe.py <id>` → 세그먼트 출력. 여기서 실제 컷 지점을 정한다.
   - 첫 발화 0.3초 전부터, 마지막 단어가 다 끝나고 0.4초 뒤까지. 단어가 잘리면 상대 대사까지 포함해 자연스럽게 끝나는 지점으로 늘린다.
   - raw 파일 기준 초로 계산 (fetch가 1초 여유를 뒀으므로 보통 시작은 1.0 부근).
3. **표현 후보 3개를 Brian에게 보여주고 확인받는다.** 확인 전엔 인코딩하지 않는다.
   - chunk 단위 (완성 문장 아님). 일상·업무에서 바로 쓸 수 있는 것.
   - Whisper 오인식은 영상 맥락과 상식으로 바로잡는다 (예: "my route" → "my roots").
4. **인코딩** `python tools/encode.py <id> <컷시작> <컷끝>` → videos/<id>.mp4, posters/<id>.jpg
5. **클립 json 작성** → work/<id>_clip.json (형식은 아래)
   - cues의 t는 **컷시작을 뺀 값**, 첫 큐는 반드시 0.0
   - 큐는 전사 세그먼트 단위. 두 사람 대사가 한 큐에 섞이면 ` — `로 구분
6. **검증** `python tools/verify.py <id>` — 통과할 때까지 json을 고친다
7. **병합** `python tools/merge_feed.py <id>` (여러 편이면 id를 나열) — 버전이 자동으로 올라간다
8. **커밋·푸시** `git add -A && git commit -m "v<버전> <id> <인물> 추가" && git push`
9. 1~2분 뒤 https://briankim-84.github.io/ss-x7q2m9/feed.json 의 version이 올라갔는지 확인하고 보고

## 클립 json 형식 (work/<id>_clip.json)
```json
{
  "id": "ss043",
  "src": "videos/043.mp4",
  "source": "토크쇼",
  "band": {"top": 0.294, "bottom": 0.706},
  "tags": ["#토크쇼영어", "#주제태그"],
  "poster": "posters/043.jpg",
  "cues": [
    {"t": 0.0, "en": "First of all, congratulations.", "ko": "먼저 축하해요."}
  ],
  "picks": [
    {"chunk": "the real deal", "ko": "진짜배기",
     "why": "명성이나 소문만큼 진짜라는 칭찬입니다. 사람·물건·실력 모두에 쓰고, 소문으로 듣던 걸 직접 확인했을 때 딱 맞습니다.",
     "use": "This chef is the real deal.", "useKo": "이 셰프 진짜배기야."}
  ]
}
```
- `source`: 토크쇼 / 인터뷰 / 아카데미 수상 소감 등 기존 값을 그대로 쓴다 (feed.json 참고)
- `tags`: 첫 번째는 출처 태그(#토크쇼영어 등), 두 번째는 주제 태그(#거절표현, #축하표현 …)
- `picks`는 정확히 3개

## 한국어 규칙
- 자막 ko는 **구어체**. 실제 한국 사람이 그 상황에서 하는 말로 옮긴다. 번역투 금지 ("~하는 것 같아요"가 아니라 "~인 것 같아요", "매우"보다 "진짜·너무").
- why는 3문장 안팎, 설명조 길게 늘이지 않는다. 비슷한 영어 표현과 어떻게 다른지, 어떤 그림(이미지)인지 짚는다.
- "A가 아니라 B" 식 대구 문장, 매번 같은 마무리 문구는 쓰지 않는다.
- useKo도 구어체. 존댓말·반말은 use의 상황에 맞춘다.

## 하지 말 것
- 영화·드라마 대사 (그건 Listen & Shadow 영역)
- 표현 확인 없이 인코딩·푸시
- 기존 클립의 cues/picks 수정 (요청이 있을 때만)
- videos/·posters/ 안의 기존 파일 삭제
