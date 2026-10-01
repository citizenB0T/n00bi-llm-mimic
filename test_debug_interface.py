import unittest
import asyncio
from pathlib import Path
from main import (
    serve_debug,
    chat_endpoint,
    start_scenario,
    get_debug_session,
    reset_debug_session,
    ChatRequest,
    ChatMessage,
    ScenarioStartRequest,
    DebugResetRequest,
    STATIC_DIR
)

class TestDebugInterface(unittest.TestCase):
    def test_debug_file_exists_and_content(self):
        debug_html = STATIC_DIR / "debug.html"
        self.assertTrue(debug_html.exists(), "debug.html should exist in static directory")
        content = debug_html.read_text(encoding="utf-8")
        self.assertIn("n00bi API Debug Console", content)
        self.assertIn("Direct JSON (No Pacing)", content)
        self.assertIn("/api/chat", content)
        self.assertIn("/api/scenario/start", content)
        self.assertIn("stream: false", content)

    def test_serve_debug_response(self):
        async def _run():
            res = await serve_debug()
            self.assertEqual(Path(res.path), STATIC_DIR / "debug.html")
        asyncio.run(_run())

    def test_chat_stream_false_instant_response(self):
        async def _run():
            payload = ChatRequest(
                messages=[ChatMessage(role="user", content="Explique-moi les API comme à un enfant de 5 ans")],
                scenario_id="evaluation_turing",
                session_id="test_debug_session_instant",
                stream=False
            )
            bundle = await chat_endpoint(payload)
            self.assertIsInstance(bundle, dict)
            self.assertIn("content", bundle)
            self.assertIn("thought", bundle)
            self.assertIn("scenario_state", bundle)
            self.assertTrue(len(bundle["content"]) > 0)
        asyncio.run(_run())

    def test_scenario_start_stream_false(self):
        async def _run():
            payload = ScenarioStartRequest(
                scenario_id="evaluation_turing",
                session_id="test_debug_session_init",
                stream=False
            )
            bundle = await start_scenario(payload)
            self.assertIsInstance(bundle, dict)
            self.assertIn("content", bundle)
            self.assertIn("scenario_state", bundle)
            self.assertEqual(bundle["scenario_state"]["scenario_id"], "evaluation_turing")
        asyncio.run(_run())

    def test_debug_session_inspection_and_reset(self):
        async def _run():
            session_id = "test_inspect_session"
            start_payload = ScenarioStartRequest(
                scenario_id="evaluation_turing",
                session_id=session_id,
                stream=False
            )
            await start_scenario(start_payload)

            # Inspect
            info = await get_debug_session(session_id)
            self.assertTrue(info["exists"])
            self.assertEqual(info["session"]["session_id"], session_id)
            self.assertEqual(info["session"]["compliance_score"], 100)

            # Reset
            reset_res = await reset_debug_session(DebugResetRequest(session_id=session_id, scenario_id="evaluation_turing"))
            self.assertEqual(reset_res["status"], "ok")
            self.assertEqual(reset_res["session"]["compliance_score"], 100)
        asyncio.run(_run())

if __name__ == "__main__":
    unittest.main()
