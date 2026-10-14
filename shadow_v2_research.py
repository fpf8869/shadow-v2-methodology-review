"""NCAAF Shadow V2 research candidate: coherent 2026-only source snapshot.
Separate versioned experimental model. NEVER modifies/replaces NCAAF-CORE-COVERAGE-DEV-2.
No market inputs, no wager authority, no independent publication-vintage attestation.
"""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import PoissonRegressor

VERSION='NCAAF-SHADOW-V2-RESEARCH-0.1.0'
PUBLISHED_HASHES={
 'schedule':'56707a541720854b4b362b8879231adb9eb633c0829e1065a75aa59441752d80',
 'box':'4e612b2056707d0cccdb8e6db69047e286e39316d561e4d686c59e5e85261b18',
 'passing':'b5c174db6e50481b67aee40f5c24faa93c489b75d330db004e66339646eccaf4',
}
FIELDS=['attempts','passing_yards','carries','rushing_yards','sacks_suffered','passing_interceptions']

def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load(schedule_path,box_path,passing_path):
 paths={'schedule':Path(schedule_path),'box':Path(box_path),'passing':Path(passing_path)}
 for k,path in paths.items():
  if sha(path)!=PUBLISHED_HASHES[k]:raise ValueError('SOURCE_HASH_MISMATCH:'+k)
 sched=pd.read_csv(paths['schedule'],dtype={'game_id':str,'home_id':str,'away_id':str})
 box=pd.read_csv(paths['box'],dtype={'game_id':str,'team_id':str})
 passing=pd.read_csv(paths['passing'],dtype={'game_id':str,'pos_team_id':str})
 if sched.game_id.duplicated().any() or box.duplicated(['game_id','team_id']).any():raise ValueError('DUPLICATE_GAME_OR_TEAM')
 if sched.status.ne('STATUS_FINAL').any():raise ValueError('UNFINALIZED_GAME')
 if sched[['home_score','away_score']].isna().any().any():raise ValueError('MISSING_SCORES')
 if passing[['Att','Yds','Sck','Int']].isna().any().any():raise ValueError('MISSING_PLAYER_STAT')
 p=passing.groupby(['game_id','pos_team_id'],as_index=False)[['Att','Yds','Sck','Int']].sum()
 b=box.merge(p,left_on=['game_id','team_id'],right_on=['game_id','pos_team_id'],how='left',validate='one_to_one',indicator=True)
 if len(b)!=2*len(sched) or not b['_merge'].eq('both').all() or not b.groupby('game_id').size().eq(2).all():raise ValueError('INCOMPLETE_PAIRING')
 b['attempts']=b.completionAttempts.str.split('/').str[-1].astype(int)
 b['passing_yards']=b.netPassingYards.astype(float) # Explicit net team passing yards, NOT old Shadow gross yards
 b['carries']=b.rushingAttempts.astype(int)
 b['rushing_yards']=b.rushingYards.astype(float)
 b['sacks_suffered']=b.Sck.astype(int) # Player Sck from same 2026 ESPN snapshot; no old source mixing
 b['passing_interceptions']=b.interceptions.astype(int)
 if not np.isfinite(b[FIELDS].to_numpy(dtype=float)).all():raise ValueError('NONFINITE_FEATURE')
 if (b[['attempts','carries','sacks_suffered','passing_interceptions']]<0).any().any():raise ValueError('NEGATIVE_COUNT')
 if (b['attempts']==0).any() or (b['carries']==0).any():raise ValueError('ZERO_ATTEMPT_DENOMINATOR')
 if not set(b.game_id)==set(sched.game_id):raise ValueError('SCHEDULE_STATS_MISMATCH')
 sched['date']=pd.to_datetime(sched.game_date,utc=True)
 sched=sched.sort_values(['date','game_id']).reset_index(drop=True)
 # Source version 2026 alone; no archived 2022-25 feature or score rows enter this fit.
 stats={(r.game_id,str(r.team_id)):r for r in b.itertuples()}
 return sched,stats,{k:sha(v) for k,v in paths.items()}

def history_rates(games,stats,team,cutoff,season=2026):
 prior=games[(games.date<cutoff)&(games.season==season)&((games.home_id==team)|(games.away_id==team))].tail(4)
 if len(prior)!=4:return None,prior.game_id.tolist()
 own=np.zeros(6);opp=np.zeros(6)
 for r in prior.itertuples():
  rival=str(r.away_id if r.home_id==team else r.home_id)
  k=(r.game_id,team);v=(r.game_id,rival)
  if k not in stats or v not in stats:raise ValueError('MISSING_TEAM_OR_OPPONENT_STATS')
  own+=np.array([getattr(stats[k],f) for f in FIELDS],dtype=float)
  opp+=np.array([getattr(stats[v],f) for f in FIELDS],dtype=float)
 def rates(a):
  attempts,passing,carries,rushing,sacks,ints=a
  if attempts<=0 or carries<=0:return None
  return [passing/attempts,rushing/carries,sacks/(attempts+sacks),ints/attempts]
 o,d=rates(own),rates(opp)
 return (o,d) if o is not None and d is not None else None,prior.game_id.tolist()

def feature_for(games,stats,home,away,cutoff):
 h,hids=history_rates(games,stats,home,cutoff)
 a,aids=history_rates(games,stats,away,cutoff)
 if h is None or a is None:return None,{'home':hids,'away':aids}
 return np.array([h[0]+a[1],a[0]+h[1]],dtype=float),{'home':hids,'away':aids}

def training_rows(games,stats,cutoff):
 train=games[games.date<cutoff]
 # Monday UTC cutoff as registered research policy; only earlier completed games.
 items=[]
 for r in train.itertuples():
  wk=r.date.normalize()-pd.Timedelta(days=r.date.weekday())
  vec,ids=feature_for(games,stats,str(r.home_id),str(r.away_id),wk)
  items.append((r,vec,ids,wk))
 return items

def encode(items,teams,center=None,scale=None):
 teams=sorted(teams);ix={t:i for i,t in enumerate(teams)}
 base=np.zeros((2*len(items),2*len(teams)+1),dtype=float)
 f=np.zeros((2*len(items),9),dtype=float)
 raw=[]
 for i,(r,vec,ids,wk) in enumerate(items):
  home,away=str(r.home_id),str(r.away_id)
  if home not in ix or away not in ix:raise ValueError('UNKNOWN_TEAM_IN_TRAINING')
  for row,off,defn,venue in [(2*i,home,away,float(not r.neutral_site)),(2*i+1,away,home,0.)]:
   base[row,ix[off]]=1.;base[row,len(teams)+ix[defn]]=1.;base[row,-1]=venue
  raw.append(vec)
  if vec is not None:f[2*i:2*i+2,:8]=vec
  else:f[2*i:2*i+2,8]=1.
 if center is None:
  present=[v for v in raw if v is not None]
  if len(present)<10:raise ValueError('TOO_FEW_COMPLETE_PRIOR_FOUR_FEATURES')
  matrix=np.concatenate(present,axis=0)
  center=matrix.mean(axis=0);scale=matrix.std(axis=0)
  if (scale<=1e-10).any():raise ValueError('DEGENERATE_FEATURE_SCALE')
 f[:,:8]=(f[:,:8]-center)/scale
 f[f[:,8]==1,:8]=0.
 return hstack([csr_matrix(base),csr_matrix(f)],format='csr'),np.array(center),np.array(scale),int(sum(v is not None for v in raw))

def fit(games,stats,cutoff,alpha=0.01):
 items=training_rows(games,stats,cutoff)
 teams=sorted(set(games.loc[games.date<cutoff,'home_id'])|set(games.loc[games.date<cutoff,'away_id']))
 x,center,scale,complete=encode(items,teams)
 y=np.array([[float(r.home_score),float(r.away_score)] for r,_,_,_ in items]).reshape(-1)
 model=PoissonRegressor(alpha=alpha,max_iter=2000,tol=1e-8).fit(x,y)
 return model,teams,center,scale,{'training_games':len(items),'complete_feature_games':complete,'cutoff':cutoff.isoformat(),'alpha':alpha,'model_features':x.shape[1]}

def predict(games,stats,model,teams,center,scale,home,away,cutoff):
 vec,ids=feature_for(games,stats,home,away,cutoff)
 if vec is None:raise ValueError('INCOMPLETE_PRIOR_FOUR_FOR_TARGET')
 class Target:pass
 t=Target();t.home_id=home;t.away_id=away;t.neutral_site=False
 x,_,_,_=encode([(t,vec,ids,cutoff)],teams,center,scale)
 pred=model.predict(x)
 if not np.isfinite(pred).all() or (pred<=0).any():raise ValueError('INVALID_PREDICTION')
 return pred.tolist(),ids,vec.tolist()

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--schedule',required=True);a.add_argument('--box',required=True);a.add_argument('--passing',required=True);a.add_argument('--output',required=True);args=a.parse_args()
 sched,stats,source=load(args.schedule,args.box,args.passing)
 cutoff=pd.Timestamp('2026-10-12T00:00:00Z')
 m,teams,center,scale,meta=fit(sched,stats,cutoff)
 pred,ids,vec=predict(sched,stats,m,teams,center,scale,'84','194',cutoff)
 obj={'version':VERSION,'game_id':'401858488','home':'Indiana','away':'Ohio State','cutoff':cutoff.isoformat(),
      'created_at_utc':pd.Timestamp.now(tz='UTC').isoformat(),'source_sha256':source,'model_code_sha256':sha(__file__),
      'fit':meta,'prior_game_ids':ids,'feature_vector':vec,'feature_center':center.tolist(),'feature_scale':scale.tolist(),
      'coefficients_sha256':hashlib.sha256(np.asarray(m.coef_,dtype='<f8').tobytes()+np.asarray([m.intercept_],dtype='<f8').tobytes()).hexdigest(),
      'pred_home':pred[0],'pred_away':pred[1],'status':'NEW_SEPARATE_SHADOW_V2_RESEARCH_UNAPPROVED',
      'source_vintage':'Uploaded Oct 13 publisher-hash-matched source; original per-game publication timestamps not independently attested',
      'training_source':'2026 only, no old-version statistical features or historical scores','market_used':False,'production_approved':False,'fire_authorized':False}
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(obj,indent=2))
 print(json.dumps({'home':pred[0],'away':pred[1],**meta,'complete':True}))
