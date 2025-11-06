import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_cannot_access_other_history(async_client, other_user_token):
    resp = await async_client.get(
        "/simulations_history", headers={"Authorization": f"Bearer {other_user_token}"}
    )
    assert all(s["user_id"] == 2 for s in resp.json())
