#!/usr/bin/env python3
"""Fork-only PyInstaller entry point (CI builds only, not used by upstream).

Upstream's own release workflow (release-cli.yml) builds PyInstaller binaries
directly from `dds_cli/__init__.py`. That file's bottom block (the
`if __name__ == "__main__":` guard) is shared with upstream, so we don't touch
it here -- this file exists purely so build-binaries-fork.yml can point
PyInstaller at a fork-only wrapper instead, keeping every upstream-tracked
file (dds_cli/*.py, requirements.txt, release-cli.yml) untouched and
conflict-free on `git merge`/`git rebase` from ScilifelabDataCentre/dds_cli.

What it adds vs. the upstream entry point:
  Inject `truststore` before anything else imports `ssl`/`requests`/`botocore`.
  This makes TLS verification use the OS-native certificate store (Windows
  CryptoAPI / macOS Security framework / Linux system store) instead of the
  certifi `cacert.pem` file PyInstaller extracts into a temp directory at
  runtime. That file can be deleted or quarantined mid-run by antivirus/EDR
  on locked-down machines, which previously surfaced as:

      OSError: Could not find a suitable TLS CA certificate bundle, invalid
      path: ...\\_MEI<pid>\\certifi\\cacert.pem

  truststore's SSLContext treats load_verify_locations()/cafile as a no-op,
  so libraries that explicitly pass certifi's path (requests, botocore) are
  unaffected by that file going missing after injection.

Requires the `truststore` package to be installed in the build environment
(added as a separate pip install step in build-binaries-fork.yml -- not added
to requirements.txt, to keep that file identical to upstream's).
"""
import sys

import truststore

truststore.inject_into_ssl()

from dds_cli.__main__ import dds_main  # noqa: E402  (import after truststore injection)

if getattr(sys, "frozen", False):
    dds_main(sys.argv[1:])
else:
    dds_main()
