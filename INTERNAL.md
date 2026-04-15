# Internal use

This repository is for **internal** use: an aligned copy of the SciLifeLab Data Delivery System CLI ([upstream `dds_cli`](https://github.com/ScilifelabDataCentre/dds_cli)). Product and API behaviour are documented with **dds_web** ([`dds_web` repository](https://github.com/ScilifelabDataCentre/dds_web), e.g. [`dev/doc`](https://github.com/ScilifelabDataCentre/dds_web/tree/dev/doc)). Published upstream CLI docs: [GitHub Pages](https://scilifelabdatacentre.github.io/dds_cli/).

## Default API URL for CI-built binaries

Internal PyInstaller builds use [`.github/workflows/build-binaries-fork.yml`](.github/workflows/build-binaries-fork.yml). It patches `dds_cli/__init__.py` on the runner before packaging; **nothing is committed**.

**Default:** set **`FORK_DDS_API_BASE_URL`** in the GitHub repo under **Settings → Secrets and variables → Actions → Variables** (full API root, including `/api/v1` if that is where your API lives). Used when workflow inputs are empty, including builds triggered by a push to `dev`.

**One-off:** **Actions → Build fork binaries → Run workflow** → fill **api_base_url** with the same value.
