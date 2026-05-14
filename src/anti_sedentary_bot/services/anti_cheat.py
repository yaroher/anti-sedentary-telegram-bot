from __future__ import annotations

from ..db.models import Task, User
from ..repositories import tasks as task_repo


async def assess_completion(user: User, task: Task) -> list[str]:
    """Inspect a completed task for suspicious signals. Returns list of reason codes.

    Also persists reasons to task.suspicion_reasons and sets task.suspicious if any.
    """
    reasons: list[str] = []

    # 1. Completed too fast
    ttc = task.time_to_complete_seconds
    if ttc is not None and ttc <= 0:
        reasons.append("completed_too_fast")
    else:
        recent_times = await task_repo.recent_completion_time_deltas(user, task.exercise_code, n=5)
        fast_count = sum(1 for t in recent_times if t < 5)
        if fast_count >= 3:
            reasons.append("completed_too_fast")

    # 2. Short answer
    if task.check_answer is not None and len(task.check_answer.strip()) < 6:
        reasons.append("short_answer")

    # 3. Duplicate answer
    if task.check_answer is not None:
        prev_answer = await task_repo.last_check_answer_for(user, exclude_task_id=task.id)
        if prev_answer and task.check_answer.strip().lower() == prev_answer.strip().lower():
            reasons.append("answer_duplicate")

    # 4. All recent answers short
    short_count = await task_repo.count_recent_short_answers(user, n=5)
    if short_count >= 4:
        reasons.append("all_short_recent")

    for reason in reasons:
        await task_repo.add_suspicion_reason(task, reason)

    return reasons
