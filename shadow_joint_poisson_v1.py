"""Research-only bivariate Poisson H=A+C, V=B+C.
Shared intensity = 10% of smaller mean; fixed exploratory setting, not calibrated.
"""
from math import isfinite
import numpy as np
from scipy.special import logsumexp
from scipy.stats import poisson,skellam
VERSION='NCAAF-SHADOW-V2-JOINT-POISSON-DIAGNOSTIC-0.1'
SHARED_FRACTION=0.10

def parameters(home_mean,away_mean,fraction=SHARED_FRACTION):
 if not all(isfinite(float(x)) and float(x)>0 for x in (home_mean,away_mean)):
  raise ValueError('invalid positive football score means')
 if not 0<=fraction<1:raise ValueError('shared fraction out of range')
 c=float(fraction*min(home_mean,away_mean))
 return float(home_mean-c),float(away_mean-c),c

def joint_logpmf(home_score,away_score,home_mean,away_mean,fraction=SHARED_FRACTION):
 if any(int(x)!=x or x<0 for x in (home_score,away_score)):
  raise ValueError('scores must be nonnegative integers')
 a,b,c=parameters(home_mean,away_mean,fraction)
 k=np.arange(min(int(home_score),int(away_score))+1)
 terms=poisson.logpmf(int(home_score)-k,a)+poisson.logpmf(int(away_score)-k,b)+poisson.logpmf(k,c)
 return float(logsumexp(terms))

def win_tie_loss(home_mean,away_mean,fraction=SHARED_FRACTION):
 a,b,_=parameters(home_mean,away_mean,fraction)
 return {'home_win':float(skellam.sf(0,a,b)),'tie':float(skellam.pmf(0,a,b)),
         'home_loss':float(skellam.cdf(-1,a,b))}
