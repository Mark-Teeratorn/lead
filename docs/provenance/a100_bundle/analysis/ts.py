import json,sys
for p in sys.argv[1:]:
    s=json.load(open(p))
    lh=s.get('log_history',[])
    print('==',p)
    print({k:s.get(k) for k in ['global_step','max_steps','epoch','num_train_epochs','train_batch_size','best_model_checkpoint','best_metric','logging_steps','save_steps']})
    tr=[e for e in lh if 'loss' in e]
    print(' first:',[(e.get('step'),e.get('epoch'),e.get('loss'),e.get('learning_rate')) for e in tr[:3]])
    print(' last :',[(e.get('step'),e.get('epoch'),e.get('loss'),e.get('learning_rate')) for e in tr[-3:]])
    print(' n_entries',len(lh),' other:',[e for e in lh if 'loss' not in e][-2:])
