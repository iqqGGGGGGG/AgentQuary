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
