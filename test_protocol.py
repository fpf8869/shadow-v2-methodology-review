import unittest,json
from pathlib import Path
P=Path(__file__).parent
class TestProtocol(unittest.TestCase):
 def setUp(self):
  self.p=json.loads((P/'prospective_protocol.json').read_text())
 def test_paper_only(self):self.assertEqual(self.p['operating_state'],'PAPER_ONLY_NO_MGM_EV_NO_FIRE')
 def test_no_automatic_release(self):self.assertIn('never automatic',self.p['evaluation']['release_gate'])
 def test_pre_kickoff(self):self.assertTrue(self.p['prospective_capture']['before_kickoff'])
 def test_external_timestamp(self):self.assertTrue(self.p['prospective_capture']['external_timestamp_attestation_required'])
 def test_no_retrofreeze(self):self.assertTrue(self.p['prospective_capture']['no_postgame_reconstruction'])
 def test_enough_games(self):self.assertGreaterEqual(self.p['evaluation']['minimum_eligible_games_before_release_review'],100)
 def test_unapproved(self):self.assertIn('NOT_APPROVED',self.p['status'])
if __name__=='__main__':unittest.main()
