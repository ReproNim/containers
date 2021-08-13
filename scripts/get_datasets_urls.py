#!/usr/bin/env python3
"""Just a little helper to mint urls pointing to datasets.datalad.org
for those annexed files we have in the tree
"""

import tqdm
from datalad.distribution.dataset import Dataset
import os.path as op

ds = Dataset(op.dirname(op.dirname(__file__)))

repo = ds.repo

# hardcode one for datasets.datalad.org
uuid = '71c620b5-997f-4849-bb30-c42dbb48a51e'
recs = []

containers = [s for s in ds.config.sections() if s.startswith('datalad.containers.')]

for c in containers:
    shuburl = ds.config.get_value(c, 'updateurl')
    p = ds.config.get_value(c, 'image')
    try:
        j = ds.status(p, annex=True)[0]
    except:
        continue
    if not j.get('key') or not p.endswith('.sing'):
        continue
    whereis = repo.whereis(p)
    if (uuid in whereis and
        j['key'].startswith('MD5E')):
            md5 = j['key'].split('--')[-1].split('.')[0]
            assert len(md5) == 32
            recs.append({
                'shuburl': shuburl,
                'url': 'http://datasets.datalad.org/repronim/containers/.git/annex/objects/{hashdirmixed}{key}/{'
                       'key}'.format(**j),
                'md5': md5,

            })
import json
print(json.dumps(recs, indent=2))
