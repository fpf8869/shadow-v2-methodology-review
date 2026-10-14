"""Reproducibility regression test for published source and exposed cohort.
Requires three original publisher-hash-matched CSVs supplied as environment variables:
NCAAF_SCHEDULE_CSV, NCAAF_BOX_CSV, NCAAF_PASSING_CSV.
No independent timestamp attestation, no production approval.
"""
import os,unittest
import pandas as pd
import shadow_v2_research as sh
class Reproduction(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  paths=[os.environ.get(k) for k in ('NCAAF_SCHEDULE_CSV','NCAAF_BOX_CSV','NCAAF_PASSING_CSV')]
  if not all(paths):raise unittest.SkipTest('Set all three source CSV paths to run source-backed test')
  cls.games,cls.stats,cls.hashes=sh.load(*paths)
 def test_2026_snapshot_counts(self):
  self.assertEqual(len(self.games),448)
  self.assertEqual(len(self.stats),896)
 def test_exposed_cohort_reproducible(self):
  cut=pd.Timestamp('2026-10-05T00:00:00Z')
  m,teams,c,s,meta=sh.fit(self.games,self.stats,cut)
  self.assertEqual(meta['training_games'],390)
  self.assertEqual(meta['complete_feature_games'],48)
  g=self.games[(self.games.date>=cut)&(self.games.date<pd.Timestamp('2026-10-12T00:00:00Z'))]
  self.assertEqual(len(g),58)
  for r in g.itertuples():
   mu,ids,_=sh.predict(self.games,self.stats,m,teams,c,s,str(r.home_id),str(r.away_id),cut)
   self.assertEqual(len(mu),2)
   self.assertGreater(min(mu),0)
   self.assertNotIn(r.game_id,ids['home'])
   self.assertNotIn(r.game_id,ids['away'])
if __name__=='__main__':unittest.main()
