from app.services.db_service import DBService
from app.services.limiter_service import LimiterService


def test_limiter_resets_and_blocks():
    db = DBService()
    limiter = LimiterService(db)

    # create a user in memory
    user = {
        "telegram_id": 12345,
        "nome": "Test",
        "plano": "Free",
        "limite_diario": 2,
        "geracoes_hoje": 0,
        "ultima_geracao": None,
    }
    db.create_user(user)

    ok, msg = limiter.can_generate(12345)
    assert ok

    limiter.increment(12345)
    ok, msg = limiter.can_generate(12345)
    assert ok

    limiter.increment(12345)
    ok, msg = limiter.can_generate(12345)
    assert not ok
    assert "limite diário" in msg
