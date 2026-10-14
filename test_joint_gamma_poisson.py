import unittest,math
from joint_gamma_poisson import logpmf,grid,events
class Tests(unittest.TestCase):
 def test_valid(self): self.assertTrue(math.isfinite(logpmf(25,20,24,21)))
 def test_nonnegative(self):
  with self.assertRaises(ValueError):logpmf(-1,1,24,21)
 def test_fraction_rejected(self):
  with self.assertRaises(ValueError):logpmf(1.5,1,24,21)
 def test_invalid_mean(self):
  with self.assertRaises(ValueError):grid(0,10)
 def test_invalid_k(self):
  with self.assertRaises(ValueError):grid(10,10,-2)
 def test_normalized(self):
  g=grid(30,22);self.assertLess(abs(g['mass']-1),2e-10)
 def test_tail_bound(self):
  g=grid(30,22);self.assertLessEqual(1-g['mass'],g['tail_bound']+1e-10)
 def test_events(self):
  e=events(25,21);self.assertLess(abs(sum(e[k] for k in ('home_win','tie','home_loss'))-1),2e-10)
 def test_symmetry(self):
  e=events(21,21);self.assertAlmostEqual(e['home_win'],e['home_loss'],places=9)
 def test_nonnegative_variance(self):
  k=20;mu=22;self.assertGreater(mu+mu**2/k,mu)
 def test_positive_covariance(self):
  self.assertGreater(25*21/20,0)
 def test_no_market(self):self.assertNotIn('odds',logpmf.__code__.co_varnames)
if __name__=='__main__':unittest.main()
