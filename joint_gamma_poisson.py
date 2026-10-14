"""Common-Gamma Poisson mixture for nonnegative correlated scores (research only)."""
import numpy as np
from scipy.special import gammaln

def joint_pmf(mu_h, mu_a, k, max_score=150):
    if mu_h<=0 or mu_a<=0 or k<=0: raise ValueError("positive parameters required")
    h=np.arange(max_score+1)[:,None];a=np.arange(max_score+1)[None,:]
    logp=(gammaln(k+h+a)-gammaln(k)-gammaln(h+1)-gammaln(a+1)
      +k*np.log(k/(k+mu_h+mu_a))
      +h*np.log(mu_h/(k+mu_h+mu_a))
      +a*np.log(mu_a/(k+mu_h+mu_a)))
    p=np.exp(logp)
    return p,p.sum()
