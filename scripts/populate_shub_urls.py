#!/usr/bin/env python3

import tqdm
from datalad.distribution.dataset import Dataset
import os.path as op
from time import sleep

from datalad.downloaders.providers import Providers
providers = Providers.from_config_files()
shub_downloader = Providers.from_config_files().get_provider('shub://doesnot/matter').get_downloader('shub://doesnot/matter')

ds = Dataset(op.dirname(op.dirname(__file__)))

repo = ds.repo

containers = [s for s in ds.config.sections() if s.startswith('datalad.containers.')]

# we need to disable datalad remove due to
# https://git-annex.branchable.com/bugs/rmurl_marks_url_not_available_in_wrong_remote/?updated
reenable_datalad = False
if 'datalad' not in repo.get_remotes():
    if 'datalad' in repo.get_special_remotes():
        repo.call_annex(['enableremote', 'datalad'])
    else:
        repo.call_annex(['initremote', 'datalad', 'externaltype=datalad', 'type=external', 'encryption=none', 'autoenable=true'])

for c in containers:
    updateurl = ds.config.get_value(c, 'updateurl')
    image = ds.config.get_value(c, 'image')
    print(f"{image}: {updateurl}")
    try:
        urls = repo.get_urls(image)
        if updateurl not in urls:
            status = shub_downloader.get_status(updateurl)
            if status.size:
                print(f"  adding {updateurl}")
                repo.add_url_to_file(image, updateurl)
            print("Sleeping")  # to not trigger rate limiting of shub
            sleep(60)
        else:
            print(f"  {urls}")
    except Exception as exc:
        print(f"  ERROR: skipping due to {exc}")
