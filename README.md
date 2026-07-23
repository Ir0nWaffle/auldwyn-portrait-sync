# Auldwyn Portrait Sync

Downloads player portraits from the Auldwyn Dropbox folder (including any
nested inside `.zip` files) and copies the `.tga` files into one folder on
your PC. Click a button whenever you want fresh portraits.

## For players/server members: just download and run

Go to the [Releases page](../../releases) of this repo and grab the file for
your OS. No Python install needed — everything's bundled in.

### Windows

1. Download `AuldwynPortraitSync-windows.exe`.
2. Run it. Windows may show a "protect your PC" SmartScreen warning since
   the app isn't code-signed — click **More info** → **Run anyway**.

### macOS

1. Download `AuldwynPortraitSync-macOS.zip` and unzip it (double-click).
2. Since the app isn't code-signed/notarized, Gatekeeper will block a normal
   double-click the first time. Instead, **right-click (or Control-click)**
   `AuldwynPortraitSync.app` → **Open** → **Open** in the dialog that
   appears. After that first time, it'll open normally.
3. If macOS still refuses, open Terminal, `cd` to the folder with the app,
   and run `xattr -cr AuldwynPortraitSync.app`, then try opening it again.

### Linux

1. Download `AuldwynPortraitSync-linux`.
2. Make it executable and run it:
   ```
   chmod +x AuldwynPortraitSync-linux
   ./AuldwynPortraitSync-linux
   ```
3. If it fails to start with a Tk-related error, install Tk for your distro
   (e.g. `sudo apt install python3-tk` on Debian/Ubuntu-based systems).

### All platforms

The destination defaults to `Documents/Neverwinter Nights/portraits` in your
user folder (created automatically if it doesn't exist yet) — NWN:EE's
default portraits folder. Click **Browse...** if you want to save somewhere
else, then click **Sync Now**. Whatever you pick is remembered for next time.

## For the repo owner: how the build works

This repo has a GitHub Actions workflow (`.github/workflows/build.yml`) that
builds Windows, macOS, and Linux executables automatically on GitHub's own
servers — you don't need any of those OSes or PyInstaller installed locally.

**To publish a new release:**

```
git add .
git commit -m "Update sync tool"
git tag v1.0.0
git push origin main --tags
```

Pushing a tag matching `v*.*.*` triggers the workflow, which builds all
three platform executables and automatically attaches them to a new GitHub
Release matching that tag. Bump the version number (`v1.0.1`, `v1.1.0`, etc.)
each time you want to publish an update.

You can also trigger a build without publishing a release — go to the
**Actions** tab on GitHub, select "Build executables", and click
**Run workflow**. The built files will be attached to that run as
downloadable artifacts, one per OS (useful for testing before you tag an
official release).

## Local development

```
pip install -r requirements.txt
python dropbox_tga_sync.py
```

## Notes

- The Dropbox link is hardcoded near the top of `dropbox_tga_sync.py`. If it
  ever changes, update it there, commit, and push a new tag.
- Windows Defender / antivirus software sometimes flags PyInstaller-built
  executables as suspicious purely because they're unsigned and bundle a
  Python interpreter — this is a common false positive for small unsigned
  tools, not a sign anything's wrong. Code-signing the executable (with a
  paid certificate) would remove this warning if it becomes a recurring
  issue for your players.
