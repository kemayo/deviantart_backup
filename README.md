# DeviantArt Backup

A backup script for DeviantArt. It'll save your deviations, journals, and statuses.

# Install

Prerequisite: have Python 3.

1. Download this repo.
1. (Optionally) activate the virtualenv
1. `pip install -r requirements.txt`
1. Visit https://www.deviantart.com/developers/ and generate a client id / secret.
1. Edit config.py to contain your id / secret.

# Usage

```
deviantart_backup.py [-h]
                     [--no-deviations]
                     [--no-journals]
                     [--no-statuses]
                     [--dry-run]
                     username
```

e.g.

```
> ./deviantart_backup.py kemayo
```
