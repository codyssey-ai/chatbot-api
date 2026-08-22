-- ============================================================================
-- 대화 로그 확인용 스크립트 (평가자용)
--
-- 실행 방법
--   Supabase 대시보드 → SQL Editor → 아래 쿼리를 하나씩 실행
--
-- 과제 산출물 요건인 "DB 확인 가이드"에 해당한다.
-- 웹에서 확인하려면 로그인 후 GET /api/threads/{thread_id}/messages 를 사용해도 된다.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. 최근 대화 로그 20건
--    질문, 응답, 생성 시각, 사용자 식별자가 한 번에 보인다.
-- ----------------------------------------------------------------------------
SELECT l.created_at,
       u.email                        AS user_email,
       t.title                        AS thread_title,
       left(l.question, 60)           AS question,
       left(coalesce(l.answer, ''), 60) AS answer,
       l.status,
       l.latency_ms
  FROM public.chat_logs l
  JOIN public.chat_threads t ON t.id = l.thread_id
  JOIN auth.users         u ON u.id = l.user_id
 ORDER BY l.created_at DESC
 LIMIT 20;


-- ----------------------------------------------------------------------------
-- 2. 사용자별 누적 현황
--    로그가 사용자 기준으로 쌓이고 있는지 확인한다.
-- ----------------------------------------------------------------------------
SELECT u.email,
       count(DISTINCT t.id)                                AS thread_count,
       count(l.id)                                         AS message_count,
       count(*) FILTER (WHERE l.status = 'error')          AS error_count,
       round(avg(l.latency_ms) FILTER (WHERE l.status = 'success')) AS avg_latency_ms,
       max(l.created_at)                                   AS last_message_at
  FROM auth.users u
  LEFT JOIN public.chat_threads t ON t.user_id = u.id
  LEFT JOIN public.chat_logs    l ON l.user_id = u.id
 GROUP BY u.email
 ORDER BY message_count DESC;


-- ----------------------------------------------------------------------------
-- 3. 특정 사용자의 대화 전체 조회
--    아래 이메일을 확인하려는 계정으로 바꿔서 실행한다.
-- ----------------------------------------------------------------------------
SELECT t.title      AS thread_title,
       l.created_at,
       l.question,
       l.answer,
       l.status
  FROM public.chat_logs l
  JOIN public.chat_threads t ON t.id = l.thread_id
  JOIN auth.users         u ON u.id = l.user_id
 WHERE u.email = 'test@example.com'      -- << 여기를 바꾼다
 ORDER BY t.created_at, l.created_at;


-- ----------------------------------------------------------------------------
-- 4. 실패한 호출 확인
--    AI API 실패나 타임아웃이 로그로 추적되는지 보여준다.
-- ----------------------------------------------------------------------------
SELECT l.created_at,
       u.email        AS user_email,
       left(l.question, 60) AS question,
       l.error_message
  FROM public.chat_logs l
  JOIN auth.users u ON u.id = l.user_id
 WHERE l.status = 'error'
 ORDER BY l.created_at DESC
 LIMIT 20;


-- ----------------------------------------------------------------------------
-- 5. LangGraph 체크포인트 적재 확인
--    thread 별로 Agent State 가 저장되고 있는지 본다.
--    checkpoints 테이블은 애플리케이션이 한 번 실행된 뒤에 생성된다.
-- ----------------------------------------------------------------------------
SELECT t.id            AS thread_id,
       t.title,
       count(c.thread_id) AS checkpoint_count
  FROM public.chat_threads t
  LEFT JOIN public.checkpoints c ON c.thread_id::uuid = t.id
 GROUP BY t.id, t.title
 ORDER BY checkpoint_count DESC
 LIMIT 20;


-- ----------------------------------------------------------------------------
-- 6. 저장 용량 확인
--    Supabase 무료 플랜은 500MB 다.
--    체크포인트 테이블이 chat_logs 보다 빠르게 커지므로 주기적으로 확인한다.
-- ----------------------------------------------------------------------------
SELECT relname                                        AS table_name,
       pg_size_pretty(pg_total_relation_size(relid))  AS total_size
  FROM pg_catalog.pg_statio_user_tables
 ORDER BY pg_total_relation_size(relid) DESC
 LIMIT 10;
