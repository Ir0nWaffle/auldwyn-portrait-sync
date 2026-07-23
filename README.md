# Auldwyn Portrait Sync

Downloads player portraits from the Auldwyn Dropbox folder (including any
nested inside `.zip` files) and copies the `.tga` files into one folder on
your PC. Click a button whenever you want fresh portraits.

## For players/server members: just download and run

1. Go to the [Releases page](../../releases) of this repo.
2. Download `AuldwynPortraitSync.exe` from the latest release.
3. Run it. Windows may show a "protect your PC" SmartScreen warning since
   the app isn't code-signed — click **More info** → **Run anyway**.
4. Click **Browse...**, pick where you want the portraits saved, then click
   **Sync Now**.

No Python install needed — everything's bundled into the one `.exe`.

## For the repo owner: how the build works

This repo has a GitHub Actions workflow (`.github/workflows/build.yml`) that
builds the Windows executable automatically on GitHub's own servers — you
don't need Windows or PyInstaller installed locally.

**To publish a new release:**

```
git add .
git commit -m "Update sync tool"
git tag v1.0.0
git push origin main --tags
```

Pushing a tag matching `v*.*.*` triggers the workflow, which builds
`AuldwynPortraitSync.exe` and automatically attaches it to a new GitHub
Release matching that tag. Bump the version number (`v1.0.1`, `v1.1.0`, etc.)
each time you want to publish an update.

You can also trigger a build without publishing a release — go to the
**Actions** tab on GitHub, select "Build Windows executable", and click
**Run workflow**. The built `.exe` will be attached to that run as a
downloadable artifact (useful for testing before you tag an official
release).

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
