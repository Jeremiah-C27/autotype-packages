# Install through apt or winget

The source repository stays private. Public package downloads and apt metadata
live in [autotype-packages](https://github.com/Jeremiah-C27/autotype-packages).
Packages support Linux amd64 and Windows x64; Rust and Node.js are not required.
Close the app before updating it. Your shortcut preferences survive upgrades.

## Debian / Ubuntu

Ubuntu 22.04+ and Debian 12+ can install the `.deb` directly:

```sh
sudo apt install ./autotype_1.5.0-1_amd64.deb
```

The package installs `/usr/bin/autotype`, an application-menu entry and the GUI
libraries needed by X11/Wayland. It starts from your application menu or with
`autotype`. Wayland still needs the desktop's keyboard-control and global-shortcut
portal support; installing a package does not grant those permissions.

For updates through apt, add the signed repository once:

```sh
sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://jeremiah-c27.github.io/autotype-packages/apt/autotype-archive-keyring.gpg | sudo tee /etc/apt/keyrings/autotype.gpg >/dev/null
sudo chmod 0644 /etc/apt/keyrings/autotype.gpg
echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/autotype.gpg] https://jeremiah-c27.github.io/autotype-packages/apt/ stable main' | sudo tee /etc/apt/sources.list.d/autotype.list >/dev/null
sudo apt update
sudo apt install autotype
```

The public signing-key fingerprint is published alongside the feed in
[`key-fingerprint.txt`](https://jeremiah-c27.github.io/autotype-packages/apt/key-fingerprint.txt).
The key is scoped to this feed with `signed-by`; system-wide `apt-key` and unsigned
repository overrides are unnecessary. Later updates use `sudo apt upgrade`.
Remove the app with `sudo apt remove autotype`. To stop receiving packages,
remove `/etc/apt/sources.list.d/autotype.list` and `/etc/apt/keyrings/autotype.gpg`.

## Windows

Once Microsoft's community submission is accepted:

```powershell
winget install --id JeremiahC27.Autotype --exact
winget upgrade --id JeremiahC27.Autotype --exact
```

This installs the native portable executable and the `autotype` command. It does
not run a custom installer or require Node/Rust. Uninstall with
`winget uninstall --id JeremiahC27.Autotype --exact`.

While catalog review is pending, the public downloads repository contains the
executable and a three-file winget manifest set. On a Windows PC with local
manifests enabled, validate and install the downloaded manifest folder:

```powershell
winget validate .\winget\manifests\j\JeremiahC27\Autotype\1.5.0
winget install --manifest .\winget\manifests\j\JeremiahC27\Autotype\1.5.0
```

Enabling local manifests requires an elevated terminal:
`winget settings --enable LocalManifestFiles`.
The final executable URL is public and its SHA-256 is pinned in the manifest.
Normal catalog installation becomes available after Microsoft's review/indexing;
a prepared manifest or opened pull request alone is not a catalog listing.

## Feed maintenance

Release packages are built and checked by the app's private source CI. This
repository publishes only distribution files, manifests, documentation and the
apt metadata generator; it does not contain the Rust application source.

The monthly refresh workflow re-signs the feed and deploys it to GitHub Pages.
Its signing material is stored in the repository's Actions secret, outside the
public files. Only the public archive keyring and fingerprint are served.
The feed retains older versions and rejects changed bytes under an existing
version. Release assets and manifest hashes must remain immutable.
