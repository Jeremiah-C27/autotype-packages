#!/usr/bin/env python3
"""Index and sign an Autotype apt repository; private keys stay in GnuPG."""
import argparse
import gzip
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime


def run(*args, **kwargs):
    return subprocess.check_output(list(map(str, args)), **kwargs)


def build(output, packages, key, home):
    if not re.fullmatch('[A-Fa-f0-9]{40}', key):
        raise ValueError('Use the full signing-key fingerprint')
    gpg = ['gpg', '--batch', '--yes', '--homedir', str(home.resolve())]
    public = run(*gpg, '--export-options', 'export-minimal', '--export', key)
    if not public:
        raise ValueError('Signing key not found')
    output.mkdir(parents=True, exist_ok=True)
    pool = output / 'pool/main/a/autotype'
    pool.mkdir(parents=True, exist_ok=True)
    for package in packages:
        name, version, arch = run('dpkg-deb', '--show', '--showformat=${Package}\t${Version}\t${Architecture}', package, text=True).split('\t')
        if name != 'autotype' or arch != 'amd64' or not re.fullmatch(r'\d+\.\d+\.\d+-[1-9]\d*', version):
            raise ValueError('Only stable Autotype amd64 packages are accepted')
        target = pool / f'autotype_{version}_amd64.deb'
        if target.exists() and target.read_bytes() != package.read_bytes():
            raise ValueError('Cannot replace different bytes under an existing package version')
        if not target.exists():
            shutil.copyfile(package, target)
    if not list(pool.glob('*.deb')):
        raise ValueError('No packages to index')
    index = output / 'dists/stable/main/binary-amd64'
    index.mkdir(parents=True, exist_ok=True)
    content = run('dpkg-scanpackages', '--multiversion', '--arch', 'amd64', 'pool', '/dev/null', cwd=output)
    (index / 'Packages').write_bytes(content)
    (index / 'Packages.gz').write_bytes(gzip.compress(content, mtime=0))
    for path in [index / 'Packages', index / 'Packages.gz']:
        for name, hash_function in [('SHA256', hashlib.sha256), ('SHA512', hashlib.sha512)]:
            hashed = index / 'by-hash' / name / hash_function(path.read_bytes()).hexdigest()
            hashed.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, hashed)
    release_dir = output / 'dists/stable'
    for name in ['Release', 'InRelease', 'Release.gpg']:
        (release_dir / name).unlink(missing_ok=True)
    release = run('apt-ftparchive', '-o', 'APT::FTPArchive::Release::Origin=Autotype',
                  '-o', 'APT::FTPArchive::Release::Label=Autotype',
                  '-o', 'APT::FTPArchive::Release::Suite=stable',
                  '-o', 'APT::FTPArchive::Release::Codename=stable',
                  '-o', 'APT::FTPArchive::Release::Architectures=amd64',
                  '-o', 'APT::FTPArchive::Release::Components=main',
                  '-o', 'APT::FTPArchive::Release::Acquire-By-Hash=yes',
                  'release', 'dists/stable', cwd=output)
    expiry = format_datetime(datetime.now(timezone.utc) + timedelta(days=90), usegmt=True)
    (release_dir / 'Release').write_bytes(f'Valid-Until: {expiry}\n'.encode() + release)
    run(*gpg, '--local-user', key, '--digest-algo', 'SHA256', '--clearsign',
        '--output', release_dir / 'InRelease', release_dir / 'Release')
    run(*gpg, '--local-user', key, '--digest-algo', 'SHA256', '--armor', '--detach-sign',
        '--output', release_dir / 'Release.gpg', release_dir / 'Release')
    (output / 'autotype-archive-keyring.gpg').write_bytes(public)
    (output / 'key-fingerprint.txt').write_text(key.upper() + '\n')
    print(f'Signed apt repository: {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deb', type=Path, action='append', default=[])
    parser.add_argument('--signing-key', required=True)
    parser.add_argument('--gnupg-home', type=Path, required=True)
    args = parser.parse_args()
    build(args.output.resolve(), [p.resolve() for p in args.deb], args.signing_key, args.gnupg_home)


if __name__ == '__main__':
    main()
