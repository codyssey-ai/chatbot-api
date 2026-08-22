// 채팅 화면 동작.
// TODO(프론트 담당): 스레드 목록/전환 부분을 채운다. 메시지 전송 흐름은 완성되어 있다.

let currentThreadId = null;

const $messages = document.getElementById("messages");
const $form = document.getElementById("chat-form");
const $input = document.getElementById("message");
const $send = document.getElementById("send");
const $error = document.getElementById("error");

function addBubble(role, text) {
  const el = document.createElement("div");
  el.className = `bubble ${role}`;
  el.textContent = text;
  $messages.appendChild(el);
  $messages.scrollTop = $messages.scrollHeight;
  return el;
}

function showError(message) {
  $error.textContent = message;
  $error.hidden = false;
}

async function ensureThread() {
  if (currentThreadId) return currentThreadId;

  const res = await fetch("/api/threads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error("대화를 시작하지 못했습니다.");

  const thread = await res.json();
  currentThreadId = thread.id;
  return currentThreadId;
}

$form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $input.value.trim();
  if (!text) return;

  $error.hidden = true;
  // 응답을 기다리는 동안 중복 전송을 막는다.
  $send.disabled = true;
  $input.value = "";
  addBubble("user", text);

  const pending = addBubble("assistant pending", "답변을 작성하고 있어요...");

  try {
    const threadId = await ensureThread();
    const res = await fetch(`/api/threads/${threadId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const body = await res.json().catch(() => ({}));

    if (res.status === 401) {
      location.href = "/login";
      return;
    }
    if (!res.ok) {
      // 서버가 내려주는 안내 메시지를 그대로 보여 준다.
      pending.remove();
      showError(body.message || "요청을 처리하지 못했습니다.");
      return;
    }

    pending.className = "bubble assistant";
    pending.textContent = body.answer;
  } catch (err) {
    pending.remove();
    showError(err.message || "네트워크 오류가 발생했습니다.");
  } finally {
    $send.disabled = false;
    $input.focus();
  }
});

document.getElementById("logout").addEventListener("click", async () => {
  await fetch("/api/auth/logout", { method: "POST" });
  location.href = "/login";
});

// TODO(프론트 담당):
//   - GET /api/threads 로 사이드바 목록 구성
//   - 목록 클릭 시 GET /api/threads/{id}/messages 로 화면 복구
//   - "+ 새 대화" 클릭 시 currentThreadId 를 비우고 화면 초기화
document.getElementById("new-thread").addEventListener("click", () => {
  currentThreadId = null;
  $messages.innerHTML = "";
  $error.hidden = true;
  $input.focus();
});
