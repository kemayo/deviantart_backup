#!/usr/bin/env python

import datetime
import json
import os
import posixpath
from urllib.parse import urlparse

import requests

from api import Api
import config


text_deviation_template = '<html><head><style type="text/css">{css}</style></head><body>{html}</body></html>'


def dackup(username, dry_run=False, journals=True, deviations=True):
    api = Api(config.CLIENT_ID, config.CLIENT_SECRET)

    if deviations:
        dackup_deviations(api, username, dry_run)
    if journals:
        dackup_journals(api, username, dry_run)


def dackup_deviations(api, username, dry_run):
    print("Deviations")
    deviations = api_suck_up_has_more(api, '/gallery/all', {
        'username': username,
        'limit': 24,
    })

    if not deviations:
        return

    makedir_if_needed(username, 'deviations')
    for d in deviations:
        print(d['title'], d.get('url'))
        if not dry_run:
            base_path = os.path.join(username, 'deviations', url_filename(d.get('url')))
            api_save_deviation(api, d, base_path)


def dackup_journals(api, username, dry_run):
    print("Journals")
    journals = api_suck_up_has_more(api, '/browse/user/journals', {
        'username': username,
        'featured': 0,
        'limit': 50,
    })

    if not journals:
        return

    makedir_if_needed(username, 'journals')
    for d in journals:
        print(d['title'], d['url'])
        if not dry_run:
            date = datetime.datetime.fromtimestamp(int(d.get('published_time'))).strftime('%Y-%m-%d_%H-%M-%S_')
            base_path = os.path.join(username, 'journals', date + url_filename(d.get('url')))
            api_save_deviation(api, d, base_path)


def makedir_if_needed(*args):
    path = os.path.join(*args)
    if not os.path.exists(path):
        os.makedirs(path)


def api_save_deviation(api, deviation, base_path):
    best_url = deviation.get('content', {}).get('src', False)
    if deviation.get('is_downloadable'):
        download_data = api.request('/deviation/download/{}'.format(deviation.get('deviationid')))
        best_url = download_data.get('src', best_url)
    with open(base_path + '.json', 'w') as fd:
        json.dump(deviation, fd, sort_keys=True, indent=4)
    extension = posixpath.splitext(url_filename(best_url))[1]
    if best_url:
        print(' downloading', best_url)
        download(best_url, base_path + extension)
    elif deviation.get('excerpt'):
        print(' saving HTML')
        content_data = api.request('/deviation/content', {
            'deviationid': deviation.get('deviationid'),
        })
        if 'html' in content_data:
            with open(base_path + '.html', 'w') as fd:
                fd.write(text_deviation_template.format(
                    html=content_data.get('html', 'NO CONTENT'),
                    css=content_data.get('css', '')
                ))


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
