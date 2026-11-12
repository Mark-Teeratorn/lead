"""Item 7: among train samples with ego speed <= 0.5 m/s at t0, count future GT path length
over 6.4 s (64 x 0.1 s, matching PAIDataset num_future_steps=64,time_step=0.1) < 0.64 m (stays put)
vs >= 2 m (starts moving). Path length = sum of XY segment lengths between poses linearly
interpolated from egomotion.parquet at t0, t0+0.1, ..., t0+6.4 s. Speed = |(vx,vy)| interpolated at t0.
Also reports the same counts from the annotation fields speed_mps / future_path_m."""
import sys,json,glob,io,zipfile,os
import numpy as np,pandas as pd
root=sys.argv[1]
ann=json.load(open(f'{root}/annotations_train.json'))
loc={}
for zp in sorted(glob.glob(f'{root}/labels/egomotion/*.zip')):
    for n in zipfile.ZipFile(zp).namelist(): loc[n.split('.')[0]]=(zp,n)
need={a['clip_id'] for a in ann}
ego={}
byzip={}
for c in need: byzip.setdefault(loc[c][0],[]).append(c)
for zp,cs in byzip.items():
    z=zipfile.ZipFile(zp)
    for c in cs: ego[c]=pd.read_parquet(io.BytesIO(z.read(loc[c][1])))
res=dict(ego_low=0,ego_put=0,ego_move=0,ego_mid=0,ann_low=0,ann_put=0,ann_move=0,ann_mid=0,trunc=0)
diffs=[]; sdiff=[]
for a in ann:
    df=ego[a['clip_id']]; ts=df.timestamp.values.astype(float); t0=float(a['t0_relative'])
    tq=t0+np.arange(65)*1e5
    if tq[-1]>ts[-1]: res['trunc']+=1
    x=np.interp(tq,ts,df.x.values); y=np.interp(tq,ts,df.y.values)
    L=float(np.hypot(np.diff(x),np.diff(y)).sum())
    v=float(np.hypot(np.interp(t0,ts,df.vx.values),np.interp(t0,ts,df.vy.values)))
    diffs.append(L-a['future_path_m']); sdiff.append(v-a['speed_mps'])
    for pre,s,l in (('ego',v,L),('ann',a['speed_mps'],a['future_path_m'])):
        if s<=0.5:
            res[pre+'_low']+=1
            if l<0.64: res[pre+'_put']+=1
            elif l>=2.0: res[pre+'_move']+=1
            else: res[pre+'_mid']+=1
d=np.abs(diffs); sd=np.abs(sdiff)
print(os.path.basename(root), json.dumps(res), 'n',len(ann),
      '|L_ego-future_path_m| median %.4f p99 %.4f max %.4f'%(np.median(d),np.percentile(d,99),d.max()),
      '|v_ego-speed_mps| median %.4f max %.4f'%(np.median(sd),sd.max()),
      'stationary_flag_true',sum(1 for a in ann if a['stationary']))
