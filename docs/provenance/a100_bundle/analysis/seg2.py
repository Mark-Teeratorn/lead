import re,sys
pat=re.compile(r'(\d+)/(2000|8000) \[([\d:]+)<')
mark=re.compile(r'STARTING/RESUMING|Starting Alpamayo 1.5 Matrix|Existing checkpoints|OutOfMemory|Continuing training|global step|\[\d{4}-\d\d-\d\d [\d:]+(,\d+)?\]')
for p in sys.argv[1:]:
    lines=open(p,errors='replace').read().replace('\r','\n').split('\n')
    print('########',p)
    vals=[];last=None
    for i,l in enumerate(lines):
        if re.search(r'Starting Alpamayo 1.5 Matrix|Existing checkpoints|OutOfMemory|Continuing training|STARTING/RESUMING|IMMUNE',l):
            if vals: print('   tqdm seq start',vals[:6],'... end',vals[-1]); vals=[]
            print('  L%d'%i,l[:160])
        m=pat.search(l)
        if m:
            v=(int(m.group(1)),m.group(3))
            if not vals or vals[-1][0]!=v[0]: vals.append(v)
    if vals: print('   tqdm seq start',vals[:6],'... end',vals[-1])
