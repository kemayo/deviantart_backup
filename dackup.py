#!/usr/bin/env python

import json
import os
import posixpath
from urllib.parse import urlparse

import requests

from api import Api
import config


def dackup(username, dry_run=False):
    da = Api(config.CLIENT_ID, config.CLIENT_SECRET)

    print("Deviations")
    deviations = api_suck_up_has_more(da, '/gallery/all', {
        'username': username,
        'limit': 24,
    })

    makedir_if_needed(username, 'deviations')
    for d in deviations:
        best_url = d.get('content', {}).get('src', False)
        if d.get('is_downloadable'):
            download_data = da.request('/deviation/download/{}'.format(d.get('deviationid')))
            best_url = download_data.get('src', best_url)

        print(d['title'], best_url)
        if not dry_run:
            base_path = os.path.join(username, 'deviations', url_filename(d.get('url')))
            with open(base_path + '.json', 'w') as fd:
                json.dump(d, fd, sort_keys=True, indent=4)
            extension = posixpath.splitext(url_filename(best_url))[1]
            download(best_url, base_path + extension)

    print("\nJournals")
    journals = api_suck_up_has_more(da, '/browse/user/journals', {
        'username': username,
        'featured': 0,
        'limit': 50,
    })

    makedir_if_needed(username, 'journals')
    print([d['title'] for d in journals])


def makedir_if_needed(*args):
    path = os.path.join(*args)
    if not os.path.exists(path):
        os.makedirs(path)


def url_filename(url):
    path = urlparse(url).path
    return posixpath.basename(path)


def download(url, filename):
    try:
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(100000):
                fd.write(chunk)
        return True
    except:
        return False


def api_suck_up_has_more(api, endpoint, get={}, post={}, *args, **kw):
    results = []
    offset = 0
    has_more = True
    while has_more:
        updated_get = {
            'offset': offset,
        }
        updated_get.update(get)
        fetched = api.request(endpoint, updated_get, post)
        has_more = fetched['has_more']
        offset = fetched['next_offset']
        results.extend(fetched['results'])
    return results


if __name__ == '__main__':
    dackup('kemayo')
