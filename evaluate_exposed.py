"""Reproduce exposed Oct 5-11 research diagnostic from publisher-hash-matched CSVs.
Historical diagnostics only: do NOT treat these 58 games as untouched validation.
No refitting of frozen Ohio State–Indiana pregame record.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
import shadow_v2_research as sh
from shadow_joint_poisson_v1 import joint_logpmf,win_tie_loss
from joint_gamma_poisson import logpmf,events

def run(schedule,box,passing,out):
 games,stats,hashes=sh.load(schedule,box,passing)
 cut=pd.Timestamp('2026-10-05T00:00:00Z')
 stop=pd.Timestamp('2026-10-12T00:00:00Z')
 model,teams,center,scale,fit=sh.fit(games,stats,cut)
 test=games[(games.date>=cut)&(games.date<stop)]
 rows=[]
 for r in test.itertuples():
  mu,ids,_=sh.predict(games,stats,model,teams,center,scale,str(r.home_id),str(r.away_id),cut)
  yh,ya=int(r.home_score),int(r.away_score)
  # The game itself must never appear in either team history.
  if r.game_id in ids['home'] or r.game_id in ids['away']:
   raise AssertionError('target leakage')
  for method,fraction in [('independent_poisson',0.),('shared_poisson_10pct',0.1),('gamma_poisson_fixed_k20',None)]:
   if fraction is None:
    lp=logpmf(yh,ya,*mu)
    ph=events(*mu)['home_win']
   else:
    lp=joint_logpmf(yh,ya,*mu,fraction)
    ph=win_tie_loss(*mu,fraction)['home_win']
   rows.append({'game_id':r.game_id,'method':method,'home_mean':mu[0],'away_mean':mu[1],
     'actual_home':yh,'actual_away':ya,'log_loss':-lp,'home_win_brier':(ph-int(yh>ya))**2,
     'pred_home_win':ph,'observed_home_win':int(yh>ya),'train_cutoff':cut.isoformat()})
 scores=pd.DataFrame(rows)
 summary={name:{'games':len(g),'joint_log_loss':float(g.log_loss.mean()),
  'home_win_brier':float(g.home_win_brier.mean()),
  'pred_home_win':float(g.pred_home_win.mean()),
  'observed_home_win':float(g.observed_home_win.mean())} for name,g in scores.groupby('method')}
 result={'status':'EXPOSED_HISTORICAL_DIAGNOSTIC_NOT_UNTOUCHED',
  'train_cutoff':cut.isoformat(),'eval_end':stop.isoformat(),
  'source_sha256':hashes,'fit':fit,'comparison':summary,
  'independent_approval':False,'production_approved':False,'fire_authorized':False}
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 scores.to_csv(out/'per_game_scores.csv',index=False)
 (out/'diagnostic.json').write_text(json.dumps(result,indent=2))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for arg in ('schedule','box','passing','out'):p.add_argument('--'+arg,required=True)
 args=p.parse_args()
 print(json.dumps(run(args.schedule,args.box,args.passing,args.out),indent=2))
