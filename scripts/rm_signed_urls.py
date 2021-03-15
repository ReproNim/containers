#!/usr/bin/env python3

import tqdm
from datalad.distribution.dataset import Dataset
import os.path as op

ds = Dataset(op.dirname(op.dirname(__file__)))

repo = ds.repo

# we need to disable datalad remove due to
# https://git-annex.branchable.com/bugs/rmurl_marks_url_not_available_in_wrong_remote/?updated
reenable_datalad = False
if 'datalad' in repo.get_remotes():
    ds.repo.call_git(['remote', 'rm', 'datalad'])
    reenable_datalad = True

for j in tqdm.tqdm(ds.status(annex=True)):
    if not j.get('key'):
        continue
    p = j['path']
    urls = repo.get_urls(p)
    for url in urls:
        # well -- we need to remove old urls as well anyways since
        if 'googleapis.com/' in url:
            print(f"{p}: rm {url[:20]}...")
            repo.rm_url(p, url)

if reenable_datalad:
    ds.repo.call_annex(['enableremote', 'datalad'])

