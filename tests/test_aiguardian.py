# =============================================================================
#  test_aiguardian.py - AIGuardian Contract Unit Test Suite
# =============================================================================

import sys
import os
import json
import unittest
import py_compile
from unittest.mock import MagicMock

# --- Mocking structure to simulate the GenLayer SDK runtime ------------------
class MockContractBase:
    pass

class MockMessage:
    def __init__(self, sender="0x1111111111111111111111111111111111111111", value=0):
        self.sender_address = sender
        self.value = value

class MockWeb:
    def __init__(self):
        self.url_to_content = {}
        self.fail_on_next = False
    def render(self, url):
        if self.fail_on_next:
            raise Exception("Simulated evidence scrape failure")
        if "404" in url:
            raise Exception("404 Link Blocked")
        if "empty" in url:
            return ""
        if "short" in url:
            return "short"
        return self.url_to_content.get(url, "LEAKED MANIFEST AUDIT: Tech Giant scraped LAION-5B-Subset without permission to train Commercial-GenAI-v3.")

class MockNondet:
    def __init__(self):
        self.web = MockWeb()
        self.exec_prompt_responses = []
        self.response_index = 0
    def exec_prompt(self, prompt):
        if self.exec_prompt_responses:
            res = self.exec_prompt_responses[self.response_index % len(self.exec_prompt_responses)]
            self.response_index += 1
            if isinstance(res, Exception):
                raise res
            return res
        return json.dumps({
            "infringement_detected": True,
            "severity_score": 92,
            "legal_analysis": "Clear evidence of unauthorized scraping found in leak logs for LAION-5B-Subset."
        })

class MockVM:
    def run_nondet_unsafe(self, leader_fn, validator_fn):
        leader_res = leader_fn()
        valid = validator_fn(leader_res)
        if not valid:
            return json.dumps({"error": "VALIDATOR_REJECTED_CONSENSUS"})
        return leader_res

class MockContractRef:
    def __init__(self, addr):
        self.addr = addr
    def emit_transfer(self, value=0):
        return True

class MockGL:
    def __init__(self):
        self.Contract = MockContractBase
        self.message = MockMessage()
        self.nondet = MockNondet()
        self.vm = MockVM()
        self.public = MagicMock()
        self.public.write = lambda f: f
        self.public.write.payable = lambda f: f
        self.public.view = lambda f: f
    def get_contract_at(self, addr):
        return MockContractRef(addr)

class MockAddress:
    def __init__(self, val):
        self.val = str(val)
    def __str__(self):
        return self.val
    def __repr__(self):
        return f"Address('{self.val}')"

mock_gl = MockGL()
mock_gl.gl = mock_gl
sys.modules['genlayer'] = mock_gl
mock_gl.Contract = MockContractBase
mock_gl.Address = MockAddress
mock_gl.bigint = lambda v: int(v)
mock_gl.TreeMap = dict

# Add contracts directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../contracts')))
import aiguardian

class TestAIGuardian(unittest.TestCase):
    def setUp(self):
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=1000000000000000000)
        mock_gl.nondet = MockNondet()
        self.contract = aiguardian.Contract()

    def test_reproducible_compilation(self):
        """Verify contract file syntax and compilation."""
        contract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../contracts/aiguardian.py'))
        compiled_file = py_compile.compile(contract_path, doraise=True)
        self.assertTrue(os.path.exists(compiled_file))

    def test_create_guild_payable_funding(self):
        """Verify create_guild attaches value and stores defense fund state."""
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=2000000000000000000)
        counsel = "0x2222222222222222222222222222222222222222"
        
        gid = self.contract.create_guild(counsel, "LAION-5B-Subset")
        self.assertEqual(gid, 0)

        guild_json = self.contract.get_guild(0)
        guild = json.loads(guild_json)

        self.assertEqual(guild["id"], 0)
        self.assertEqual(guild["dataset_name"], "LAION-5B-Subset")
        self.assertEqual(guild["counsel"], counsel)
        self.assertEqual(guild["amount"], 2000000000000000000)
        self.assertEqual(guild["status"], "ACTIVE")
        self.assertEqual(self.contract.get_guilds_count(), 1)

    def test_audit_access_control_unauthorized_sender(self):
        """Verify audit scan rejects unauthorized non-participant callers."""
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=1000000000000000000)
        counsel = "0x2222222222222222222222222222222222222222"
        self.contract.create_guild(counsel, "Protected-Art-V1")

        # Change sender to unauthorized third party
        mock_gl.message = MockMessage(sender="0x9999999999999999999999999999999999999999")
        
        with self.assertRaises(Exception) as ctx:
            self.contract.scan_for_infringement(0, "https://ai-guardian-nine.vercel.app/mock_infringement_breached.txt")
        self.assertIn("Only the guild creator or legal counsel can trigger a copyright audit", str(ctx.exception))

    def test_audit_infringement_payout_success(self):
        """Verify confirmed infringement releases escrow funds to counsel."""
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=5000000000000000000)
        counsel = "0x2222222222222222222222222222222222222222"
        self.contract.create_guild(counsel, "ConceptArt-Dataset")

        # Run scan from creator address
        self.contract.scan_for_infringement(0, "https://ai-guardian-nine.vercel.app/mock_infringement_breached.txt")

        guild_json = self.contract.get_guild(0)
        guild = json.loads(guild_json)

        self.assertTrue(guild["infringement_detected"])
        self.assertEqual(guild["severity_score"], 92)
        self.assertEqual(guild["status"], "BREACHED")
        self.assertEqual(guild["amount"], 0) # Released to counsel

    def test_audit_no_infringement_active(self):
        """Verify non-infringed audit retains funds in active state."""
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=3000000000000000000)
        counsel = "0x2222222222222222222222222222222222222222"
        self.contract.create_guild(counsel, "Public-Domain-Archive")

        mock_gl.nondet.web.url_to_content["https://ai-guardian-nine.vercel.app/mock_infringement_clean.txt"] = \
            "PUBLIC STATEMENT: All training data was licensed under CC0 public domain terms."

        mock_gl.nondet.exec_prompt_responses = [
            json.dumps({
                "infringement_detected": False,
                "severity_score": 0,
                "legal_analysis": "No copyright infringement found. Data usage was fully licensed under CC0 terms."
            })
        ]

        self.contract.scan_for_infringement(0, "https://ai-guardian-nine.vercel.app/mock_infringement_clean.txt")

        guild_json = self.contract.get_guild(0)
        guild = json.loads(guild_json)

        self.assertFalse(guild["infringement_detected"])
        self.assertEqual(guild["status"], "ACTIVE")
        self.assertEqual(guild["amount"], 3000000000000000000)

    def test_validator_rerun_scrape_failure_rejects_consensus(self):
        """Verify validator rerun failure returns False and rejects consensus."""
        mock_gl.message = MockMessage(sender="0x1111111111111111111111111111111111111111", value=1000000000000000000)
        counsel = "0x2222222222222222222222222222222222222222"
        self.contract.create_guild(counsel, "Flaky-Scrape-Dataset")

        mock_gl.nondet.web.fail_on_next = True

        self.contract.scan_for_infringement(0, "https://flaky-server.com/evidence")

        guild_json = self.contract.get_guild(0)
        guild = json.loads(guild_json)

        self.assertEqual(guild["status"], "FAILED")

if __name__ == '__main__':
    unittest.main()
