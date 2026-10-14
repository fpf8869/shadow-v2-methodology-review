import unittest, hashlib, json, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import shadow_v2_research as s
S='cfb_schedule_2026.csv';B='team_box_2026.csv';P='adv_passing_2026.csv'
class TestShadowV2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not all(Path(x).exists() for x in (S,B,P)):raise unittest.SkipTest('Publisher-hash-matched CSV assets not present; download from the sources in README')
  cls.games,cls.stats,cls.hashes=s.load(S,B,P)
 def test_all_game_team_pairs(self):
  self.assertEqual(len(self.games),448);self.assertEqual(len(self.stats),896)
 def test_same_source_verified(self):
  self.assertEqual(self.hashes,s.PUBLISHED_HASHES)
 def test_strict_prior_four(self):
  v,ids=s.feature_for(self.games,self.stats,'84','194',pd.Timestamp('2026-10-12T00:00:00Z'))
  self.assertEqual(len(ids['home']),4);self.assertEqual(len(ids['away']),4)
  self.assertEqual(v.shape,(2,8))
 def test_no_future_games_enter_history(self):
  v,ids=s.feature_for(self.games,self.stats,'84','194',pd.Timestamp('2026-10-12T00:00:00Z'))
  dates=self.games.set_index('game_id').date
  self.assertTrue(all(dates[g]<pd.Timestamp('2026-10-12T00:00:00Z') for ids2 in ids.values() for g in ids2))
 def test_cutoff_does_not_accept_target_results(self):
  self.assertNotIn('401858488',set(self.games.game_id))
 def test_predict_replay_exact(self):
  cut=pd.Timestamp('2026-10-12T00:00:00Z')
  m,t,c,z,meta=s.fit(self.games,self.stats,cut)
  p1,ids,f=s.predict(self.games,self.stats,m,t,c,z,'84','194',cut)
  m2,t2,c2,z2,meta2=s.fit(self.games,self.stats,cut)
  p2,_,_=s.predict(self.games,self.stats,m2,t2,c2,z2,'84','194',cut)
  self.assertEqual(p1,p2);self.assertEqual(meta,meta2)
 def test_early_season_missing_history_blocks(self):
  v,_=s.feature_for(self.games,self.stats,'84','194',pd.Timestamp('2026-09-01T00:00:00Z'))
  self.assertIsNone(v)
 def test_source_hash_tampering_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'tampered.csv';p.write_bytes(Path(P).read_bytes()+b'\n')
   with self.assertRaisesRegex(ValueError,'SOURCE_HASH_MISMATCH'):s.load(S,B,p)
 def test_no_market_columns_in_contract(self):
  self.assertTrue(set(s.FIELDS).isdisjoint({'spread','moneyline','odds','total_line'}))
if __name__=='__main__':unittest.main()
