import base64

import pytest


@pytest.mark.asyncio
async def test_get_profile(auth_client, test_user):
    resp = await auth_client.get("/api/user/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openid"] == test_user.openid
    assert data["nickname"] == "测试用户"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_profile_no_auth(client):
    resp = await client.get("/api/user/profile")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_nickname(auth_client):
    resp = await auth_client.put("/api/user/profile", json={"nickname": "新名字"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["nickname"] == "新名字"


@pytest.mark.asyncio
async def test_update_profile_avatar(auth_client):
    resp = await auth_client.put(
        "/api/user/profile",
        json={"avatar_url": "https://example.com/avatar.png"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["avatar_url"] == "https://example.com/avatar.png"


@pytest.mark.asyncio
async def test_update_profile_partial(auth_client):
    resp = await auth_client.put("/api/user/profile", json={"nickname": "只改名字"})
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "只改名字"

    resp2 = await auth_client.put("/api/user/profile", json={"avatar_url": "https://img.com/a.png"})
    assert resp2.status_code == 200
    assert resp2.json()["nickname"] == "只改名字"
    assert resp2.json()["avatar_url"] == "https://img.com/a.png"


@pytest.mark.asyncio
async def test_update_profile_no_auth(client):
    resp = await client.put("/api/user/profile", json={"nickname": "no"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_rejects_blank_nickname(auth_client):
    resp = await auth_client.put("/api/user/profile", json={"nickname": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_upload_avatar_persists_valid_image(auth_client, tmp_path, monkeypatch):
    from routers import user as user_router

    avatar_dir = tmp_path / "avatars"
    monkeypatch.setattr(user_router, "AVATAR_DIR", avatar_dir)
    png = b"\x89PNG\r\n\x1a\n" + b"test-image-content"
    resp = await auth_client.post("/api/user/profile/avatar", json={
        "data": base64.b64encode(png).decode("ascii"),
        "file_type": "png",
    })

    assert resp.status_code == 200
    assert "/uploads/avatars/" in resp.json()["avatar_url"]
    saved_files = list(avatar_dir.glob("*.png"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == png


@pytest.mark.asyncio
async def test_upload_avatar_rejects_non_image(auth_client):
    resp = await auth_client.post("/api/user/profile/avatar", json={
        "data": base64.b64encode(b"not-an-image").decode("ascii"),
        "file_type": "png",
    })
    assert resp.status_code == 400


# ── Stats ──

@pytest.mark.asyncio
async def test_get_stats_empty(auth_client):
    resp = await auth_client.get("/api/user/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_quizzes"] == 0
    assert data["total_questions"] == 0
    assert data["avg_accuracy"] == 0.0
    assert data["best_streak"] == 0
    assert data["learning_days"] == 0


@pytest.mark.asyncio
async def test_get_stats_with_records(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "s1",
        "topic": "主题1",
        "accuracy": 0.8,
        "total_questions": 10,
        "correct_count": 8,
        "duration_seconds": 120,
    })
    await auth_client.post("/api/user/history", json={
        "session_id": "s2",
        "topic": "主题2",
        "accuracy": 0.6,
        "total_questions": 5,
        "correct_count": 3,
        "duration_seconds": 60,
    })

    resp = await auth_client.get("/api/user/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_quizzes"] == 2
    assert data["total_questions"] == 15
    assert abs(data["avg_accuracy"] - 0.7) < 0.01
    assert data["best_streak"] == 8


@pytest.mark.asyncio
async def test_get_stats_no_auth(client):
    resp = await client.get("/api/user/stats")
    assert resp.status_code == 401


# ── History CRUD ──

@pytest.mark.asyncio
async def test_save_history(auth_client):
    resp = await auth_client.post("/api/user/history", json={
        "session_id": "sess_001",
        "topic": "三国人物关系",
        "accuracy": 0.85,
        "total_questions": 10,
        "correct_count": 8,
        "duration_seconds": 300,
        "summary": "掌握不错",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "sess_001"
    assert data["topic"] == "三国人物关系"
    assert data["accuracy"] == 0.85
    assert data["total_questions"] == 10
    assert data["summary"] == "掌握不错"


@pytest.mark.asyncio
async def test_save_history_update_existing(auth_client):
    payload = {
        "session_id": "sess_002",
        "topic": "原主题",
        "accuracy": 0.5,
        "total_questions": 5,
        "correct_count": 2,
        "duration_seconds": 60,
    }
    resp1 = await auth_client.post("/api/user/history", json=payload)
    assert resp1.status_code == 200

    payload["topic"] = "更新主题"
    payload["accuracy"] = 0.8
    resp2 = await auth_client.post("/api/user/history", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["topic"] == "更新主题"
    assert resp2.json()["accuracy"] == 0.8


@pytest.mark.asyncio
async def test_list_history(auth_client):
    for i in range(3):
        await auth_client.post("/api/user/history", json={
            "session_id": f"list_sess_{i}",
            "topic": f"主题{i}",
            "accuracy": 0.5 + i * 0.1,
            "total_questions": 10,
            "correct_count": 5 + i,
            "duration_seconds": 100,
        })

    resp = await auth_client.get("/api/user/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_history_empty(auth_client):
    resp = await auth_client.get("/api/user/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_delete_history(auth_client):
    save_resp = await auth_client.post("/api/user/history", json={
        "session_id": "del_sess_001",
        "topic": "要删除的主题",
        "accuracy": 0.7,
        "total_questions": 10,
        "correct_count": 7,
        "duration_seconds": 120,
    })
    record_id = save_resp.json()["id"]

    del_resp = await auth_client.delete(f"/api/user/history/{record_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "已删除"

    list_resp = await auth_client.get("/api/user/history")
    assert list_resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_delete_history_not_found(auth_client):
    resp = await auth_client.delete("/api/user/history/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_history_other_user(test_user, db_session, client):
    from auth import create_access_token
    from models.orm import User, LearningRecord
    other_user = User(openid="other_user", nickname="其他用户")
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    record = LearningRecord(
        user_id=other_user.id,
        session_id="other_sess",
        topic="别人的记录",
        accuracy=0.9,
        total_questions=5,
        correct_count=4,
        duration_seconds=60,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)

    resp = await client.delete(
        f"/api/user/history/{record.id}",
        headers={"Authorization": f"Bearer {create_access_token(test_user)}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_history_no_auth(client):
    resp = await client.post("/api/user/history", json={
        "session_id": "no_auth",
        "topic": "t",
        "accuracy": 0.5,
        "total_questions": 1,
        "correct_count": 0,
        "duration_seconds": 10,
    })
    assert resp.status_code == 401

    resp2 = await client.get("/api/user/history")
    assert resp2.status_code == 401


# ── Level ──

@pytest.mark.asyncio
async def test_get_level(auth_client):
    resp = await auth_client.get("/api/user/level")
    assert resp.status_code == 200
    data = resp.json()
    assert data["xp"] == 0
    assert data["level"] == 1
    assert data["level_name"] == "知识新手"
    assert "progress" in data


@pytest.mark.asyncio
async def test_level_up_after_save(auth_client):
    for i in range(5):
        await auth_client.post("/api/user/history", json={
            "session_id": f"level_sess_{i}",
            "topic": "测试主题",
            "accuracy": 1.0,
            "total_questions": 10,
            "correct_count": 10,
            "duration_seconds": 60,
        })
    resp = await auth_client.get("/api/user/level")
    assert resp.status_code == 200
    data = resp.json()
    assert data["xp"] > 0
    assert data["level"] >= 1


# ── Learning Calendar ──

@pytest.mark.asyncio
async def test_learning_calendar(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "cal_sess",
        "topic": "日历测试",
        "accuracy": 0.8,
        "total_questions": 10,
        "correct_count": 8,
        "duration_seconds": 120,
    })
    from datetime import date
    today = date.today()
    resp = await auth_client.get(f"/api/user/learning-calendar?year={today.year}&month={today.month}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["year"] == today.year
    assert data["month"] == today.month
    assert len(data["days"]) > 0


@pytest.mark.asyncio
async def test_learning_calendar_no_auth(client):
    resp = await client.get("/api/user/learning-calendar?year=2026&month=8")
    assert resp.status_code == 401


# ── Achievements ──

@pytest.mark.asyncio
async def test_get_achievements(auth_client):
    resp = await auth_client.get("/api/user/achievements")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 10
    assert data["unlocked_count"] == 0
    assert len(data["items"]) == 10


@pytest.mark.asyncio
async def test_achievement_unlock_first_quiz(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "ach_first",
        "topic": "成就测试",
        "accuracy": 0.8,
        "total_questions": 10,
        "correct_count": 8,
        "duration_seconds": 120,
    })
    resp = await auth_client.get("/api/user/achievements")
    data = resp.json()
    unlocked = [a for a in data["items"] if a["unlocked"]]
    assert len(unlocked) >= 1
    assert any(a["key"] == "first_quiz" for a in unlocked)


# ── Wrong Questions ──

@pytest.mark.asyncio
async def test_wrong_questions(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "wq_sess",
        "topic": "错题测试",
        "accuracy": 0.5,
        "total_questions": 2,
        "correct_count": 1,
        "duration_seconds": 60,
        "questions": [
            {"id": 1, "type": "single_choice", "question": "问题1？", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "解释1"},
            {"id": 2, "type": "single_choice", "question": "问题2？", "options": ["A", "B", "C", "D"], "answer": 2, "explanation": "解释2"},
        ],
        "user_answers": [
            {"question_id": 1, "selected": 0, "is_correct": True},
            {"question_id": 2, "selected": 1, "is_correct": False},
        ],
    })
    resp = await auth_client.get("/api/user/wrong-questions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["topic_count"] >= 1


@pytest.mark.asyncio
async def test_wrong_questions_empty(auth_client):
    resp = await auth_client.get("/api/user/wrong-questions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_remove_wrong_question(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "wq_del",
        "topic": "删除测试",
        "accuracy": 0.0,
        "total_questions": 1,
        "correct_count": 0,
        "duration_seconds": 30,
        "questions": [
            {"id": 1, "type": "single_choice", "question": "Q?", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "E"},
        ],
        "user_answers": [
            {"question_id": 1, "selected": 1, "is_correct": False},
        ],
    })
    resp = await auth_client.delete("/api/user/wrong-questions/1/1")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_wrong_questions_quiz(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "wq_quiz_sess",
        "topic": "错题练习测试",
        "accuracy": 0.5,
        "total_questions": 2,
        "correct_count": 1,
        "duration_seconds": 60,
        "questions": [
            {"id": 10, "type": "single_choice", "question": "Q10？", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "E10"},
            {"id": 11, "type": "single_choice", "question": "Q11？", "options": ["A", "B", "C", "D"], "answer": 2, "explanation": "E11"},
        ],
        "user_answers": [
            {"question_id": 10, "selected": 0, "is_correct": True},
            {"question_id": 11, "selected": 1, "is_correct": False},
        ],
    })
    resp = await auth_client.get("/api/user/wrong-questions/quiz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["topic"] == "错题练习"
    assert data["session_id"].startswith("wrong-")
    assert len(data["questions"]) >= 1
    q = data["questions"][0]
    assert "id" in q and "type" in q and "options" in q and "answer" in q


@pytest.mark.asyncio
async def test_wrong_questions_quiz_empty(auth_client):
    resp = await auth_client.get("/api/user/wrong-questions/quiz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["topic"] == "错题练习"
    assert data["questions"] == []


# ── Trends ──

@pytest.mark.asyncio
async def test_get_trends(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "trend_sess",
        "topic": "趋势测试",
        "accuracy": 0.7,
        "total_questions": 10,
        "correct_count": 7,
        "duration_seconds": 120,
    })
    resp = await auth_client.get("/api/user/trends?days=7")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["days"]) == 7


# ── Domains ──

@pytest.mark.asyncio
async def test_get_domains(auth_client):
    await auth_client.post("/api/user/history", json={
        "session_id": "domain_sess",
        "topic": "三国人物关系",
        "accuracy": 0.8,
        "total_questions": 10,
        "correct_count": 8,
        "duration_seconds": 120,
    })
    resp = await auth_client.get("/api/user/domains")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["domains"]) >= 1


# ── Preferences ──

@pytest.mark.asyncio
async def test_preferences_crud(auth_client):
    resp = await auth_client.get("/api/user/preferences")
    assert resp.status_code == 200
    assert resp.json()["preferences"] == []

    resp2 = await auth_client.put("/api/user/preferences", json={"preferences": ["历史", "科学"]})
    assert resp2.status_code == 200
    assert resp2.json()["preferences"] == ["历史", "科学"]

    resp3 = await auth_client.get("/api/user/preferences")
    assert resp3.json()["preferences"] == ["历史", "科学"]


# ── Goal ──

@pytest.mark.asyncio
async def test_goal_crud(auth_client):
    resp = await auth_client.get("/api/user/goal")
    assert resp.status_code == 200
    data = resp.json()
    assert data["daily_goal"] == 3
    assert data["today_count"] == 0

    resp2 = await auth_client.put("/api/user/goal", json={"daily_goal": 5})
    assert resp2.status_code == 200
    assert resp2.json()["daily_goal"] == 5


# ── History Save Response ──

@pytest.mark.asyncio
async def test_save_history_returns_xp_and_achievements(auth_client):
    resp = await auth_client.post("/api/user/history", json={
        "session_id": "xp_sess",
        "topic": "XP测试",
        "accuracy": 0.9,
        "total_questions": 10,
        "correct_count": 9,
        "duration_seconds": 120,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["xp_earned"] > 0
    assert "new_achievements" in data
    assert isinstance(data["new_achievements"], list)
