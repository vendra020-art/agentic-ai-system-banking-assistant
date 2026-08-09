import asyncio
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.coordinator import Coordinator  # noqa: E402
from app.models import Principal  # noqa: E402
from tests.fakes import FakeToolClient  # noqa: E402


async def main() -> int:
    cases = json.loads((Path(__file__).parent / "cases.json").read_text())
    principal = Principal(subject="eval", customer_id="CUST-1042", scopes={"accounts:read", "transactions:read", "service:write"})
    passed = 0
    for case in cases:
        response = await Coordinator(FakeToolClient()).handle(case["input"], f"eval-{case['name']}", principal)
        actual = {"intent": response.data["kind"], "agents": response.agents, "tools": response.tools}
        expected = {key: case[key] for key in actual}
        ok = actual == expected
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} {case['name']}: {actual}")
    print(f"\n{passed}/{len(cases)} evaluation cases passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
