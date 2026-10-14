"""Research-only coherent bivariate negative multinomial via common Gamma intensity.
H|G ~ Poisson(mu_h*G), A|G ~ Poisson(mu_a*G), G~Gamma(k,k).
Fixed k=20 is a pre-evaluation exploratory setting, NOT calibrated or selected.
No change to original Shadow predictor, saved means, or earlier forecast.
"""
import math
import numpy as np
from scipy.special import gammaln
from scipy.stats import nbinom
VERSION='SHADOW-V2-GAMMA-POISSON-RESEARCH-0.1'
K=20.0

def validate(mh,ma,k=K):
    if not all(math.isfinite(float(x)) and float(x)>0 for x in (mh,ma,k)):
        raise ValueError('positive finite means and dispersion shape required')

def logpmf(h,a,mh,ma,k=K):
    validate(mh,ma,k)
    if not (isinstance(h,(int,np.integer)) and isinstance(a,(int,np.integer)) and h>=0 and a>=0):
        raise ValueError('nonnegative integer scores required')
    den=k+mh+ma
    return float(gammaln(k+h+a)-gammaln(k)-gammaln(h+1)-gammaln(a+1)
                 +k*np.log(k/den)+h*np.log(mh/den)+a*np.log(ma/den))

def grid(mh,ma,k=K,tail=1e-10):
    validate(mh,ma,k)
    # Marginal NB(shape=k, p=k/(k+mean)); union bound controls omitted joint tail.
    high=int(max(nbinom.ppf(1-tail/2,k,k/(k+mh)),nbinom.ppf(1-tail/2,k,k/(k+ma))))
    h,a=np.meshgrid(np.arange(high+1),np.arange(high+1),indexing='ij')
    den=k+mh+ma
    log=(gammaln(k+h+a)-gammaln(k)-gammaln(h+1)-gammaln(a+1)
        +k*np.log(k/den)+h*np.log(mh/den)+a*np.log(ma/den))
    probs=np.exp(log)
    mass=float(probs.sum())
    bound=float(nbinom.sf(high,k,k/(k+mh))+nbinom.sf(high,k,k/(k+ma)))
    return {'grid':probs,'mass':mass,'tail_bound':bound,'upper_score':high}

def events(mh,ma,k=K):
    g=grid(mh,ma,k)
    h,a=np.indices(g['grid'].shape)
    return {'home_win':float(g['grid'][h>a].sum()),'tie':float(g['grid'][h==a].sum()),
            'home_loss':float(g['grid'][h<a].sum()),'tail_bound':g['tail_bound']}
