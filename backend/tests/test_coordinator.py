import pytest

from app.coordinator import Coordinator, plan_request
from app.models import Principal
from app.session import SessionStore
from tests.fakes import FakeToolClient


PRINCIPAL = Principal(subject="tester", customer_id="CUST-1042", scopes={"accounts:read", "transactions:read", "service:write"})


def test_plans_multi_agent_request():
    plan = plan_request("Show my balance and recent transactions")
    assert plan.intent == "balance_and_transactions"
    assert plan.actions == ("balance", "recent")


@pytest.mark.asyncio
async def test_balance_calls_accounts_service():
    tools = FakeToolClient()
    response = await Coordinator(tools).handle("What is my balance?", "session-a", PRINCIPAL)
    assert response.agents == ["accounts-agent"]
    assert response.tools == ["accounts.get_balance"]
    assert tools.calls[0][:2] == ("accounts", "get-balance")


@pytest.mark.asyncio
async def test_multi_agent_request_runs_two_tools():
    tools = FakeToolClient()
    response = await Coordinator(tools).handle("Balance and last 5 transactions", "session-b", PRINCIPAL)
    assert response.agents == ["accounts-agent", "transactions-agent"]
    assert set(response.tools) == {"accounts.get_balance", "transactions.list_recent"}
    assert len(tools.calls) == 2


@pytest.mark.asyncio
async def test_card_number_is_redacted_before_routing():
    tools = FakeToolClient()
    response = await Coordinator(tools).handle("My card is 4111 1111 1111 1111", "session-c", PRINCIPAL)
    assert "4111" not in response.redacted_input
    assert response.tools == []
    assert tools.calls == []


@pytest.mark.asyncio
async def test_session_history_is_scoped():
    tools = FakeToolClient()
    store = SessionStore()
    coordinator = Coordinator(tools, store=store)
    await coordinator.handle("Get my May statement", "session-d", PRINCIPAL)
    history = store.get("session-d")
    assert [entry["role"] for entry in history] == ["user", "assistant"]
    assert store.get("another-session") == []
