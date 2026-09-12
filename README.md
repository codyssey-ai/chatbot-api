# AI 챗봇 서비스

**배포 주소 — https://chatbot-api-xihh.onrender.com**

> 무료 플랜이라 15분 이상 요청이 없으면 대기 상태로 들어간다.
> 첫 접속은 깨어나는 데 1분쯤 걸릴 수 있다.

로그인한 사용자가 웹에서 질문하면 AI 가 답하고, 모든 대화가 DB 에 누적되는 서비스다.
대화별로 문맥이 이어지며, 지난 대화를 언제든 다시 열어볼 수 있다.

- **문제 정의** — 일반 챗봇 UI 는 대화가 길어지면 문맥이 끊기거나 비용이 급증한다.
  또한 대화 기록이 브라우저에만 남아 다른 기기에서 이어가기 어렵다.
- **타겟 사용자** — 여러 주제를 오가며 AI 와 길게 대화하고, 지난 논의를 다시 찾아봐야 하는 사용자.
- **핵심 시나리오**
  1. 회원가입 후 로그인한다.
  2. 새 대화를 열고 질문한다. AI 가 답한다.
  3. 대화가 길어지면 오래된 내용은 자동으로 요약되고 최근 맥락은 유지된다.
  4. 며칠 뒤 다시 접속해 그 대화를 열면 이전 내용이 그대로 복구된다.

---

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 백엔드 | FastAPI (async), uvicorn |
| 프론트엔드 | Jinja2 템플릿 + Vanilla JS |
| AI | LangGraph `create_agent` + `SummarizationMiddleware` |
| 인증 | Supabase Auth + HttpOnly 쿠키 |
| DB | Supabase PostgreSQL |
| 배포 | Render |

---

## 로컬 실행 방법

### 1. 저장소 클론 및 의존성 설치

```bash
git clone https://github.com/codyssey-ai/chatbot-api.git
cd chatbot-api

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.11 이상이 필요하다.

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 를 열어 아래 값을 채운다. **`.env` 는 저장소에 올라가지 않는다.**

| 키 | 필수 | 발급 위치 |
|---|:--:|---|
| `OPENAI_API_KEY` | O | [platform.openai.com](https://platform.openai.com/api-keys) |
| `MODEL_NAME` | | 기본값 `openai:gpt-4.1-mini` |
| `DATABASE_URL` | O | Supabase → **Connect** → `Direct` 탭 → **Session pooler** |
| `SUPABASE_URL` | O | Supabase → Settings → API Keys |
| `SUPABASE_ANON_KEY` | O | 같은 화면의 Publishable key (`sb_publishable_...`) |
| `SUPABASE_SERVICE_ROLE_KEY` | | 현재 사용처 없음. 비워 둔다 |
| `AI_TIMEOUT_SECONDS` | | 기본값 60 |
| `SUMMARY_TRIGGER_TOKENS` | | 요약 시작 임계값. 기본값 8000 |
| `SUMMARY_KEEP_TOKENS` | | 원문 유지 토큰. 기본값 4000 |
| `MAX_MESSAGE_LENGTH` | | 입력 길이 제한. 기본값 2000 |
| `COOKIE_SECURE` | | 로컬은 `false`, 배포(HTTPS)는 `true` |
| `LANGGRAPH_STRICT_MSGPACK` | | 체크포인트 역직렬화 타입 제한. `true` 로 둔다 |
| `LOG_LEVEL` | | 기본값 `INFO` |

`DATABASE_URL` 에서 주의할 점이 두 가지 있다.

- **반드시 Session pooler(5432)를 쓴다.** Transaction pooler(6543)는 prepared statement 를
  지원하지 않아 LangGraph 체크포인터에서 간헐적 오류가 난다.
- 비밀번호에 특수문자가 있으면 URL 인코딩한다. 예: `!` → `%21`

### 3. 데이터베이스 준비

Supabase 대시보드 → **SQL Editor** 에서 [`scripts/schema.sql`](scripts/schema.sql) 전체를
붙여넣고 실행한다. 여러 번 실행해도 안전하다.

이어서 **Authentication → Sign In / Providers → Email** 에서
**Confirm email 을 끈다.** 켜져 있으면 회원가입 테스트마다 메일 확인이 필요하다.

> LangGraph 체크포인트 테이블(`checkpoints` 등)은 직접 만들지 않는다.
> 서버가 처음 기동될 때 자동으로 생성된다.

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

기동에 성공하면 아래 로그가 나온다.

```
INFO  startup_complete request_id=- model=openai:gpt-4.1-mini
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 5. 동작 확인

```bash
curl -s localhost:8000/health
# {"status":"ok"}
```

브라우저에서 http://localhost:8000 을 열면 로그인 화면으로 이동한다.

미로그인 상태에서 API 를 호출하면 차단되는지도 확인할 수 있다.

```bash
curl -i -X POST localhost:8000/api/threads \
  -H 'Content-Type: application/json' -d '{}'
# HTTP/1.1 401 Unauthorized
# {"error_code":"UNAUTHORIZED","message":"로그인이 필요합니다.","request_id":"..."}
```

### 문제가 생기면

| 증상 | 원인과 해결 |
|---|---|
| `Missing credentials` 로 기동 실패 | `.env` 의 `OPENAI_API_KEY` 가 비어 있다 |
| `ValidationError` 로 기동 실패 | 필수 환경 변수가 빠졌다. 위 표의 **필수** 항목을 확인한다 |
| DB 연결 타임아웃 | `DATABASE_URL` 이 Session pooler 주소인지, 비밀번호가 인코딩됐는지 확인한다 |
| 가입은 되는데 로그인이 안 됨 | Supabase → Authentication → Sign In / Providers → Email 에서 **Confirm email 을 끈다** |
| 로그인 후 계속 `/login` 으로 돌아감 | 로컬은 HTTP 라 `COOKIE_SECURE=false` 여야 쿠키가 심긴다 |

---

## 프로젝트 구조

기능별로 폴더를 나눠 담당자가 폴더 단위로 소유할 수 있게 했다.
한 기능을 고칠 때 그 폴더 안에서 끝나므로 여러 명이 동시에 작업해도 충돌이 적다.

```
app/
├─ main.py        진입점. lifespan 에서 풀·체크포인터·에이전트를 조립한다
├─ core/          설정, DB 풀, 로깅, 미들웨어, 예외, 전역 의존성
├─ auth/          회원가입·로그인·토큰 검증
├─ threads/       채팅방 CRUD
├─ chat/          메시지 전송, LangGraph 에이전트, 프롬프트
└─ web/           Jinja2 화면 라우터

templates/        base / login / signup / chat
static/           style.css, chat.js
scripts/          schema.sql, check_logs.sql, render-diagrams.sh
docs/             architecture.md, API_SPEC.md, 다이어그램
```

각 기능 폴더는 같은 역할 구분을 따른다.

| 파일 | 역할 |
|---|---|
| `router.py` | HTTP 계층. 요청을 받고 응답을 만든다 |
| `schemas.py` | 요청/응답 모델과 입력 검증 |
| `service.py` | 비즈니스 로직. 소유권 확인 등 여러 단계를 조립한다 |
| `repository.py` | SQL. DB 접근은 이 파일에만 둔다 |
| `deps.py` | 해당 기능의 의존성 |

## 시스템 구조

![배포 구성도](docs/images/01-deployment.png)

| 컴포넌트 | 역할 |
|---|---|
| 브라우저 (Jinja2 + JS) | 회원가입·로그인 폼, 채팅 화면 |
| 인증 라우터 | Supabase Auth 호출 후 토큰을 HttpOnly 쿠키로 발급 |
| `get_current_user` | 쿠키 토큰 검증. 비로그인 요청 401 차단 |
| 챗 라우터 | 입력 검증 → LangGraph 호출 → 응답 반환 → `chat_logs` 저장 |
| LangGraph Agent | 현재 질문만 받아 처리. 과거 대화는 체크포인터가 복구 |
| `SummarizationMiddleware` | 토큰 임계값 초과 시 과거 대화를 요약으로 압축 |
| `AsyncPostgresSaver` | `thread_id` 기준 State 저장·복구 |

**AI API 키는 서버에서만 사용한다.** 브라우저는 우리 FastAPI 만 호출하고,
OpenAI 호출과 Supabase 접속은 전부 서버 안에서 일어난다.

자세한 내용은 [`docs/architecture.md`](docs/architecture.md) 참고.

### 요청 처리 흐름

![요청 처리 흐름](docs/images/03-request-flow.png)

---

## API 명세

전체 명세와 요청·응답 예시는 [`docs/API_SPEC.md`](docs/API_SPEC.md) 에 있다.
서버 기동 후 http://localhost:8000/docs 에서도 확인할 수 있다.

| Method | Endpoint | 설명 | 인증 |
|---|---|---|:--:|
| `POST` | `/api/auth/signup` | 회원가입 | |
| `POST` | `/api/auth/login` | 로그인. HttpOnly 쿠키 발급 | |
| `POST` | `/api/auth/logout` | 로그아웃 | |
| `GET` | `/api/me` | 현재 사용자 확인 | O |
| `POST` | `/api/threads` | 새 채팅 생성 | O |
| `GET` | `/api/threads` | 내 채팅 목록 | O |
| `PATCH` | `/api/threads/{id}` | 제목 변경 | O |
| `DELETE` | `/api/threads/{id}` | 채팅 삭제 | O |
| `GET` | `/api/threads/{id}/messages` | 대화 내역 조회 | O |
| `POST` | `/api/threads/{id}/messages` | 메시지 전송 | O |
| `GET` | `/health` | 서버·DB 상태 확인 | |

### 예시 — 메시지 전송

```http
POST /api/threads/5aa60fa8-c927-4416-b559-f9661b7df00f/messages
Content-Type: application/json

{ "message": "내가 아까 DB 뭐 쓴다고 했지?" }
```

```json
{
  "thread_id": "5aa60fa8-c927-4416-b559-f9661b7df00f",
  "answer": "Supabase PostgreSQL 을 사용한다고 하셨습니다."
}
```

### 오류 응답

| 상황 | 코드 | `error_code` |
|---|:--:|---|
| 미로그인 | 401 | `UNAUTHORIZED` |
| 타인 소유 리소스 | 404 | `NOT_FOUND` |
| 입력 검증 실패 | 422 | `INVALID_INPUT` |
| AI 호출 타임아웃 | 504 | `AI_TIMEOUT` |
| AI 호출 실패 | 502 | `AI_UPSTREAM_ERROR` |

모든 응답에 `request_id` 가 포함되며 서버 로그와 대조할 수 있다.
오류 원문은 사용자에게 노출하지 않고 로그와 `chat_logs.error_message` 에만 남긴다.

---

## DB 구조

![ERD](docs/images/04-erd.png)

| 테이블 | 역할 |
|---|---|
| `auth.users` | 사용자 계정. **Supabase Auth 가 관리** (직접 만들지 않음) |
| `chat_threads` | 사용자별 채팅방. `id` 가 LangGraph `thread_id` 로 쓰인다 |
| `chat_logs` | 질문·응답 원본. 화면 복구·조회·감사용 |
| `checkpoints` 계열 | LangGraph Agent State. 자동 생성·관리 |

`chat_logs` 는 컨텍스트 관리용이 아니다. 미들웨어가 오래된 대화를 요약해도
`chat_logs` 의 원본은 그대로 유지된다.

### DB 확인 가이드

[`scripts/check_logs.sql`](scripts/check_logs.sql) 을 Supabase SQL Editor 에서 실행한다.
쿼리 6종이 들어 있다.

1. 최근 대화 로그 20건 (질문·응답·시각·사용자)
2. 사용자별 누적 현황 (스레드 수, 메시지 수, 실패 수, 평균 지연)
3. 특정 사용자의 대화 전체 조회
4. 실패한 호출 확인
5. 체크포인트 적재 확인
6. 저장 용량 확인

로그인 후 `GET /api/threads/{id}/messages` 로 화면에서도 확인할 수 있다.

---

## 민감정보 관리

- API 키, DB 비밀번호 등은 **코드와 문서에 직접 쓰지 않는다.** 전부 `.env` 로 관리한다.
- `.env` 는 [`.gitignore`](.gitignore) 에 등록되어 저장소에 올라가지 않는다.
  DB 파일, 로그, 가상환경, 키 파일도 함께 제외한다.
- 저장소에는 [`.env.example`](.env.example) 만 포함한다. **키 이름과 설명만 있고 실제 값은 없다.**
- Supabase 접속 키는 서버에서만 사용하며 클라이언트로 내보내지 않는다.
- `chat_threads`, `chat_logs` 와 LangGraph 체크포인트 테이블에 **RLS 를 켜 두었다.**
  Supabase 는 `public` 스키마를 REST API 로 자동 노출하는데, 정책을 만들지 않은 채
  RLS 만 켜면 외부 직접 접근이 차단된다. 서버는 소유자 역할로 접속해 영향받지 않는다.

---

## 배포

배포 URL: **https://chatbot-api-xihh.onrender.com**

Render 에 GitHub 저장소를 연결한다. 빌드·시작 명령과 환경 변수 목록은
[`render.yaml`](render.yaml) 에 정의되어 있어, Blueprint 로 가져오면 그대로 재현된다.
대시보드에서 직접 설정한다면 아래와 같다.

```
Build Command      pip install -r requirements.txt
Start Command      uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path  /health
```

Python 버전은 [`.python-version`](.python-version) 으로 고정한다.

### 환경 변수

`.env` 의 키를 Render 환경 변수로 등록한다. **로컬과 달라지는 값은 하나뿐이다.**

| 키 | 배포 값 |
|---|---|
| `COOKIE_SECURE` | **`true`** — Render 는 HTTPS 를 제공하므로 세션 쿠키에 Secure 를 켠다 |

비밀값(`OPENAI_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`, `SUPABASE_URL`,
`SUPABASE_ANON_KEY`)은 `render.yaml` 에 값을 두지 않고 대시보드에서 입력한다.

### 배포 후 확인

1. `GET /health` 가 `{"status":"ok"}` 를 반환하는지
2. 기동 로그에 `startup_complete main_model=... summary_model=...` 이 찍히는지
3. Supabase → Authentication → Sign In / Providers → Email 에서 Confirm email 이 꺼져 있는지
4. 회원가입 → 로그인 → 대화 전송이 배포 환경에서 동작하는지

### 유휴 정지 주의

무료 플랜에는 유휴 정지가 있다.

| 대상 | 정지 조건 | 결과 |
|---|---|---|
| Render | 15분 무활동 | spin down. 다음 요청 시 약 1분 뒤 자동으로 깨어난다 |
| Supabase | **7일 무활동** | **프로젝트 일시정지. 앱 전체가 동작하지 않는다** |

Render 는 요청이 오면 스스로 깨어나지만, **Supabase 는 그렇지 않다.**
따라서 오래 사용하지 않았다면 **시연이나 평가 전에 서비스에 한 번 접속해 깨워 둔다.**
`/health` 를 호출하면 DB 에 `SELECT 1` 이 나가 Render 와 Supabase 가 함께 깨어난다.

```bash
curl -s https://chatbot-api-xihh.onrender.com/health
```

---

## 구현 현황

모든 기능이 구현되어 배포까지 완료되었다.

| 항목 | 상태 |
|---|---|
| 프로젝트 구조, 설정, 로깅, 예외 처리 | 완료 |
| DB 스키마, 체크포인트 테이블 RLS | 완료 |
| 인증 (회원가입 · 로그인 · 로그아웃 · 토큰 검증) | 완료 |
| 채팅방 CRUD (생성 · 목록 · 제목 변경 · 삭제) | 완료 |
| 멀티턴 메시지 전송, LangGraph 에이전트, 요약 미들웨어 | 완료 |
| 대화 로그 저장 및 조회, 실패 로그 기록 | 완료 |
| 장애 처리 (타임아웃 · 업스트림 실패 · 동시 요청 차단 · 모델 폴백) | 완료 |
| 화면 (회원가입 · 로그인 · 채팅 · 채팅방 관리) | 완료 |
| 배포 (Render) | 완료 |

---

## 팀 구성원 및 역할

| 이름 | 역할 | 커밋 |
|---|---|---|
| 정재윤 ([@whitecy01](https://github.com/whitecy01)) | API · 공통 기반 | 18 |
| 김현중 ([@stnguswnd](https://github.com/stnguswnd)) | AI 파이프라인 · 채팅 API | 14 |
| 백예지 ([@yejibaek12](https://github.com/yejibaek12)) | 프론트엔드 | 19 |

### 정재윤 — API · 공통 기반

- 프로젝트 구조 설계. 기능별 패키지와 라우터 → 서비스 → 리포지토리 3계층 고정
- 설정(`pydantic-settings`), DB 커넥션 풀, 구조화 로깅, 공통 예외 처리
- 요청마다 `request_id` 를 발급해 모든 로그와 오류 응답에 싣는 미들웨어
- Supabase 스키마 작성, 체크포인트 테이블 RLS 적용
- 인증 API — 회원가입 · 로그인 · 로그아웃 · 토큰 검증. HttpOnly 쿠키 세션
- Render 배포 설정(`render.yaml`)과 기동 로그 정정
- 시스템 구조 문서, API 명세, 아키텍처 다이어그램, README

### 김현중 — AI 파이프라인 · 채팅 API

- 채팅방 CRUD API. 요청마다 소유권 확인, 삭제 시 체크포인트까지 정리
- `thread_id` 기반 멀티턴 메시지 처리. 과거 대화는 체크포인터가 복구한다
- LangGraph 에이전트 구성과 `SummarizationMiddleware` 요약 전략
- 메인 · 요약 모델 분리, OpenAI 실패 시 Gemini 자동 폴백
- 대화 로그 저장과 이력 조회. 실패도 `status='error'` 로 기록
- 장애 처리 — AI 타임아웃(504), 업스트림 오류(502), 동일 대화 동시 요청 차단(409)
- 설정 · 스키마 · 에이전트 · 리포지토리 · 서비스 테스트

### 백예지 — 프론트엔드

- 채팅 화면과 채팅방 목록 사이드바, 선택 상태 표시, 반응형 레이아웃
- 채팅방 생성 · 제목 변경 · 삭제 UI
- 이전 대화 복구. 요약되지 않은 원본이 필요해 `chat_logs` 를 읽는다
- 채팅방 전환 시 경쟁 조건 처리 — 이전 응답 렌더링 방지, 이전 오류 무시,
  전환 중 전송 차단, 404 응답 시 목록 갱신
- 오류 안내 — 인증 만료 시 로그인 페이지 이동, 409 · 502 · 504 상황별 문구,
  5xx 오류에 `request_id` 표시
- `chat.js` 코드 구조 재배치

---

## 문서

| 문서 | 내용 |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | 시스템 구조, 배포 파이프라인, 요청 흐름, ERD |
| [`docs/API_SPEC.md`](docs/API_SPEC.md) | API 전체 명세, 테이블 정의, 에이전트 구성 |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | 브랜치 전략, 커밋·이슈·PR 컨벤션 |
