"""
Multi-Agent Quiz Generator - V3 (Batch + Reasoning)
=====================================================
Generates a FULL SESSION of 5 questions in one call.
Returns the analyzer's reasoning so the UI can show "why" these questions.
"""

from typing import List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import os, random, asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END


# ─── Models ───────────────────────────────────────────────────────────────────
class QuizState(TypedDict):
    course_title: str
    course_category: str
    history: List[Dict[str, Any]]
    weak_topic: str
    difficulty: str
    analyzer_reasoning: str
    question_draft: Optional[Dict[str, Any]]
    reviewer_feedback: str
    final_question: Optional[Dict[str, Any]]
    iterations: int


class AnalysisResult(BaseModel):
    weak_topic: str = Field(description="Chủ đề KỸ THUẬT CỤ THỂ học viên đang yếu nhất")
    difficulty: Literal["easy", "medium", "hard"] = Field(
        description="Độ khó: easy(<50% đúng), medium(50-79%), hard(>=80%)"
    )
    reasoning: str = Field(description="1-2 câu giải thích VÌ SAO chọn chủ đề và độ khó này (viết trực tiếp cho học viên)")


class QuestionModel(BaseModel):
    question: str = Field(description="Câu hỏi kỹ thuật rõ ràng, thực tế, có thể có code snippet ngắn")
    options: List[str] = Field(description="Đúng 4 đáp án. Đáp án sai phải trông rất hợp lý và dễ nhầm")
    correct_answer: str = Field(description="Phải khớp CHÍNH XÁC từng ký tự với 1 phần tử trong options")
    explanation: str = Field(description="Giải thích kỹ thuật 2-3 câu: tại sao đúng VÀ tại sao các đáp án kia sai")
    difficulty: str = Field(description="easy | medium | hard")
    topic_tag: str = Field(description="Tag ngắn, ví dụ: 'React Hooks', 'SQL Joins', 'Big-O'")


class ReviewResult(BaseModel):
    is_factually_correct: bool
    correct_answer_in_options: bool
    feedback: str


# ─── Demo bank ────────────────────────────────────────────────────────────────
DEMO_BATCH = [
    {
        "question": "Trong React, hook useEffect chạy ở thời điểm nào?",
        "options": ["Trước khi component render", "Sau mỗi lần render (theo default)", "Chỉ khi state thay đổi", "Chỉ khi props thay đổi"],
        "correct_answer": "Sau mỗi lần render (theo default)",
        "explanation": "useEffect chạy sau DOM đã được cập nhật. Bạn có thể dùng dependency array để giới hạn khi nào nó chạy: [] chỉ chạy 1 lần, [dep] chạy khi dep thay đổi.",
        "difficulty": "medium", "topic_tag": "React Hooks"
    },
    {
        "question": "Đâu là độ phức tạp thời gian của Binary Search trên mảng đã sắp xếp?",
        "options": ["O(n)", "O(n²)", "O(log n)", "O(n log n)"],
        "correct_answer": "O(log n)",
        "explanation": "Binary Search chia đôi không gian tìm kiếm mỗi bước, nên số bước tối đa là log₂(n). Linear Search là O(n), Bubble Sort O(n²), Merge Sort O(n log n).",
        "difficulty": "medium", "topic_tag": "Algorithms"
    },
    {
        "question": "Trong SQL, mệnh đề nào dùng để lọc dữ liệu SAU GROUP BY?",
        "options": ["WHERE", "HAVING", "FILTER", "SELECT"],
        "correct_answer": "HAVING",
        "explanation": "WHERE lọc trước khi nhóm (trên từng row), HAVING lọc sau khi nhóm (trên kết quả aggregate như COUNT, SUM). Đây là lỗi nhầm rất phổ biến.",
        "difficulty": "easy", "topic_tag": "SQL"
    },
    {
        "question": "Trong JavaScript, Promise.all() xử lý lỗi như thế nào?",
        "options": [
            "Bỏ qua promise lỗi, trả về các promise thành công",
            "Reject ngay khi có 1 promise reject bất kỳ",
            "Chờ tất cả promise hoàn thành rồi mới báo lỗi",
            "Tự động retry promise bị lỗi"
        ],
        "correct_answer": "Reject ngay khi có 1 promise reject bất kỳ",
        "explanation": "Promise.all() theo cơ chế 'fail-fast': chỉ cần 1 promise reject, toàn bộ Promise.all() reject ngay lập tức. Dùng Promise.allSettled() nếu muốn chờ tất cả dù có lỗi.",
        "difficulty": "hard", "topic_tag": "JavaScript Async"
    },
    {
        "question": "HTTP status code 401 và 403 khác nhau như thế nào?",
        "options": [
            "401: Server lỗi, 403: Client lỗi",
            "401: Chưa xác thực, 403: Đã xác thực nhưng không có quyền",
            "401: Không tìm thấy, 403: Hết hạn session",
            "Chúng hoàn toàn giống nhau"
        ],
        "correct_answer": "401: Chưa xác thực, 403: Đã xác thực nhưng không có quyền",
        "explanation": "401 Unauthorized nghĩa là chưa đăng nhập (hoặc token sai). 403 Forbidden nghĩa là đã đăng nhập nhưng không đủ quyền truy cập tài nguyên đó. Đây là lỗi phân biệt API rất thường gặp.",
        "difficulty": "medium", "topic_tag": "HTTP & REST"
    }
]

DEMO_REASONING = "Bạn chưa có lịch sử quiz. Mình tạo bộ 5 câu hỏi nền tảng bao gồm React, Algorithms, SQL, JavaScript Async và HTTP để đánh giá tổng quan."


# ─── Pipeline ─────────────────────────────────────────────────────────────────
def build_quiz_graph():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    s_analysis = llm.with_structured_output(AnalysisResult)
    s_question = llm.with_structured_output(QuestionModel)
    s_review = llm.with_structured_output(ReviewResult)

    def analyzer_agent(state: QuizState) -> dict:
        history = state.get("history", [])
        course_title = state.get("course_title", "Lập trình")
        course_category = state.get("course_category", "Technology")

        if not history:
            return {
                "weak_topic": f"Kiến thức nền tảng của {course_title}",
                "difficulty": "easy",
                "analyzer_reasoning": f"Bạn chưa có lịch sử quiz cho khóa '{course_title}'. Mình sẽ bắt đầu với các câu hỏi cơ bản để đánh giá nền tảng."
            }

        history_str = "\n".join([
            f"- Lần {i+1}: {h.get('score',0)}/{h.get('total',1)} điểm"
            f"{', chủ đề: ' + h['topic'] if h.get('topic') else ''}"
            for i, h in enumerate(history[-8:])
        ])
        avg = sum(h.get("score",0)/max(h.get("total",1),1) for h in history) / len(history)

        msgs = [
            SystemMessage(content=(
                f"Bạn là AI phân tích học tập cho khóa '{course_title}' ({course_category}).\n"
                "Xác định chủ đề kỹ thuật cụ thể học viên yếu nhất và độ khó phù hợp.\n"
                "Viết reasoning ngắn gọn, trực tiếp cho học viên biết AI đang nghĩ gì."
            )),
            HumanMessage(content=f"Lịch sử:\n{history_str}\n\nTỷ lệ đúng TB: {avg:.0%}")
        ]
        res = s_analysis.invoke(msgs)
        return {
            "weak_topic": res.weak_topic,
            "difficulty": res.difficulty,
            "analyzer_reasoning": res.reasoning
        }

    def generator_agent(state: QuizState) -> dict:
        weak_topic = state.get("weak_topic", "lập trình cơ bản")
        difficulty = state.get("difficulty", "medium")
        course_title = state.get("course_title", "lập trình")
        feedback = state.get("reviewer_feedback", "")

        difficulty_guide = {
            "easy": "Hỏi về định nghĩa, cú pháp cơ bản, hoặc use-case đơn giản nhất.",
            "medium": "Hỏi về cách hoạt động nội bộ, so sánh kỹ thuật, hoặc tình huống thực tế.",
            "hard": "Hỏi về edge case, performance trade-off, pitfall, hoặc debugging phức tạp."
        }

        feedback_block = f"\n\n⚠️ SỬA LỖI TỪ LẦN TRƯỚC:\n{feedback}\nTạo lại câu hỏi hoàn toàn mới." if feedback else ""

        msgs = [
            SystemMessage(content=(
                f"Bạn là chuyên gia thiết kế câu hỏi kỹ thuật cho khóa '{course_title}'.\n"
                f"Hướng dẫn độ khó '{difficulty}': {difficulty_guide.get(difficulty,'')}\n"
                "QUAN TRỌNG: correct_answer phải khớp CHÍNH XÁC (kể cả spaces, caps) với 1 phần tử trong options."
            )),
            HumanMessage(content=f"Tạo câu hỏi về: **{weak_topic}**{feedback_block}")
        ]
        res = s_question.invoke(msgs)
        return {"question_draft": res.model_dump(), "iterations": state.get("iterations", 0) + 1}

    def reviewer_agent(state: QuizState) -> dict:
        draft = state.get("question_draft", {})
        msgs = [
            SystemMessage(content=(
                "Thẩm định nghiêm khắc:\n"
                "1. Câu hỏi và đáp án có chính xác kỹ thuật không?\n"
                "2. correct_answer có khớp chính xác (kể cả khoảng trắng) với 1 option không?"
            )),
            HumanMessage(content=(
                f"Câu hỏi: {draft.get('question','')}\n"
                f"Options: {draft.get('options',[])}\n"
                f"Đáp án: '{draft.get('correct_answer','')}'\n"
                f"Giải thích: {draft.get('explanation','')}"
            ))
        ]
        res = s_review.invoke(msgs)
        if res.is_factually_correct and res.correct_answer_in_options:
            return {"final_question": draft, "reviewer_feedback": ""}
        return {"reviewer_feedback": res.feedback or "Cần tạo lại."}

    def route(state: QuizState) -> str:
        if state.get("final_question") or state.get("iterations", 0) >= 3:
            return END
        return "generator_agent"

    wf = StateGraph(QuizState)
    wf.add_node("analyzer_agent", analyzer_agent)
    wf.add_node("generator_agent", generator_agent)
    wf.add_node("reviewer_agent", reviewer_agent)
    wf.set_entry_point("analyzer_agent")
    wf.add_edge("analyzer_agent", "generator_agent")
    wf.add_edge("generator_agent", "reviewer_agent")
    wf.add_conditional_edges("reviewer_agent", route)
    return wf.compile()


quiz_graph = None
if os.environ.get("OPENAI_API_KEY"):
    quiz_graph = build_quiz_graph()


def _generate_one(base_state: dict, topic_override: Optional[str] = None) -> dict:
    """Generate a single question. Reuses analyzer result from base_state."""
    state = {**base_state, "question_draft": None, "reviewer_feedback": "", "final_question": None, "iterations": 0}
    if topic_override:
        state["weak_topic"] = topic_override

    # Skip analyzer (already ran), jump straight to generator
    # Build a mini-graph without analyzer
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
    s_question = llm.with_structured_output(QuestionModel)
    s_review = llm.with_structured_output(ReviewResult)

    difficulty_guide = {
        "easy": "Hỏi về định nghĩa, cú pháp cơ bản, hoặc use-case đơn giản nhất.",
        "medium": "Hỏi về cách hoạt động nội bộ, so sánh kỹ thuật, hoặc tình huống thực tế.",
        "hard": "Hỏi về edge case, performance trade-off, pitfall, hoặc debugging phức tạp."
    }

    difficulty = state.get("difficulty", "medium")
    weak_topic = state.get("weak_topic", "lập trình")
    course_title = state.get("course_title", "")

    for attempt in range(3):
        feedback = state.get("reviewer_feedback", "")
        feedback_block = f"\n\n⚠️ SỬA LỖI:\n{feedback}\nTạo câu hỏi hoàn toàn mới." if feedback else ""
        
        q_msgs = [
            SystemMessage(content=(
                f"Chuyên gia tạo câu hỏi cho khóa '{course_title}'. "
                f"Độ khó '{difficulty}': {difficulty_guide.get(difficulty,'')}\n"
                "correct_answer PHẢI khớp chính xác với 1 option."
            )),
            HumanMessage(content=f"Câu hỏi về: **{weak_topic}**{feedback_block}")
        ]
        draft = s_question.invoke(q_msgs).model_dump()

        r_msgs = [
            SystemMessage(content="Thẩm định: 1) Chính xác kỹ thuật? 2) correct_answer khớp options chính xác?"),
            HumanMessage(content=f"Q: {draft['question']}\nOptions: {draft['options']}\nAnswer: '{draft['correct_answer']}'")
        ]
        review = s_review.invoke(r_msgs)

        if review.is_factually_correct and review.correct_answer_in_options:
            return draft
        state["reviewer_feedback"] = review.feedback

    # Failsafe: fix correct_answer mismatch
    if draft.get("correct_answer") not in draft.get("options", []):
        draft["options"] = list(dict.fromkeys(draft.get("options", [])[:3] + [draft["correct_answer"]]))
    return draft


def generate_adaptive_quiz_batch(
    history: List[Dict[str, Any]],
    course_title: str = "Lập trình Web",
    course_category: str = "Technology",
    batch_size: int = 5
) -> Dict[str, Any]:
    """
    Generates a full batch of questions.
    Returns: { questions: [...], analyzer_reasoning: str, weak_topic: str, difficulty: str }
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "questions": DEMO_BATCH,
            "analyzer_reasoning": DEMO_REASONING,
            "weak_topic": "Kiến thức nền tảng",
            "difficulty": "medium"
        }

    # Step 1: Run analyzer once
    initial_state: QuizState = {
        "course_title": course_title,
        "course_category": course_category,
        "history": history,
        "weak_topic": "",
        "difficulty": "medium",
        "analyzer_reasoning": "",
        "question_draft": None,
        "reviewer_feedback": "",
        "final_question": None,
        "iterations": 0
    }

    # Run full pipeline for first question (includes analyzer)
    first_result = quiz_graph.invoke(initial_state)
    weak_topic = first_result.get("weak_topic", "lập trình cơ bản")
    difficulty = first_result.get("difficulty", "medium")
    analyzer_reasoning = first_result.get("analyzer_reasoning", "")
    first_q = first_result.get("final_question") or first_result.get("question_draft")

    questions = [first_q] if first_q else []

    # Step 2: Generate remaining questions in parallel
    base_state = {
        "course_title": course_title,
        "course_category": course_category,
        "weak_topic": weak_topic,
        "difficulty": difficulty,
        "history": history
    }

    # Related subtopics to add variety
    subtopic_variations = [
        f"{weak_topic} - ứng dụng thực tế",
        f"{weak_topic} - edge case và pitfall",
        f"{weak_topic} - so sánh với kỹ thuật tương tự",
        f"Chủ đề liên quan đến {weak_topic}"
    ]

    remaining_count = batch_size - len(questions)
    with ThreadPoolExecutor(max_workers=min(remaining_count, 4)) as executor:
        futures = [
            executor.submit(_generate_one, base_state, subtopic_variations[i % len(subtopic_variations)])
            for i in range(remaining_count)
        ]
        for future in futures:
            try:
                q = future.result(timeout=25)
                if q:
                    questions.append(q)
            except Exception:
                pass  # Skip failed questions

    # Deduplicate by question text
    seen = set()
    unique_questions = []
    for q in questions:
        key = q.get("question", "")[:60]
        if key not in seen:
            seen.add(key)
            unique_questions.append(q)

    return {
        "questions": unique_questions[:batch_size],
        "analyzer_reasoning": analyzer_reasoning,
        "weak_topic": weak_topic,
        "difficulty": difficulty
    }
