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

1. Inject `truststore` before anything else imports `ssl`/`requests`/`botocore`.
   This makes TLS *verification* use the OS-native certificate store (Windows
   CryptoAPI / macOS Security framework / Linux system store) instead of the
   certifi `cacert.pem` file PyInstaller extracts into a temp directory at
   runtime. That file can be deleted or quarantined mid-run by antivirus/EDR
   on locked-down machines, which previously surfaced as:

       OSError: Could not find a suitable TLS CA certificate bundle, invalid
       path: ...\\_MEI<pid>\\certifi\\cacert.pem

   truststore's SSLContext treats load_verify_locations()/cafile as a no-op,
   so once a connection actually gets to the SSL layer, that file going
   missing doesn't matter -- verification happens against the OS store
   regardless of what cafile was passed in.

2. Patch `requests.adapters.HTTPAdapter.cert_verify` to drop its own upfront
   `os.path.exists(certifi.where())` check. This is a *separate* bug from (1):
   `requests` (used for all DDS API calls -- auth, file metadata, MOTD, etc.)
   validates that certifi's cacert.pem file exists on disk *before* an SSL
   context is ever created, and raises exactly the OSError above if it
   doesn't -- so truststore alone never gets a chance to help for anything
   going through `requests`. (boto3/botocore, used for the actual S3 file
   transfer, has no such upfront check, so it was already covered by (1)
   alone.) The patch only skips the check when using the default,
   auto-detected bundle path; an explicitly-configured custom `verify=<path>`
   still fails loudly if that path is genuinely wrong.

Requires the `truststore` package to be installed in the build environment
(added as a separate pip install step in build-binaries-fork.yml -- not added
to requirements.txt, to keep that file identical to upstream's).
"""
import os
import sys

import truststore

truststore.inject_into_ssl()

import requests.adapters  # noqa: E402  (import after truststore injection)


def _cert_verify_without_file_check(self, conn, url, verify, cert):
    """Drop-in replacement for requests' HTTPAdapter.cert_verify.

    Identical to the original except: when using the default, auto-detected
    CA bundle (verify=True, i.e. certifi.where()), a missing file no longer
    raises OSError -- verification still happens via truststore's patched
    ssl.SSLContext against the OS trust store regardless of what cafile is
    (or isn't) set. An explicitly-configured custom `verify="/some/path"`
    still raises normally if that path doesn't exist, since that's a real
    misconfiguration rather than a temp file having been swept away.
    """
    if url.lower().startswith("https") and verify:
        cert_loc = None
        if verify is not True:
            # Explicit custom CA bundle path: keep the original, strict check.
            cert_loc = verify
            if not cert_loc or not os.path.exists(cert_loc):
                raise OSError(
                    f"Could not find a suitable TLS CA certificate bundle, "
                    f"invalid path: {cert_loc}"
                )

        conn.cert_reqs = "CERT_REQUIRED"
        if cert_loc and not os.path.isdir(cert_loc):
            conn.ca_certs = cert_loc
        elif cert_loc:
            conn.ca_cert_dir = cert_loc
        else:
            # Default bundle: let truststore's OS-backed verification handle
            # it even if certifi's cacert.pem isn't there.
            conn.ca_certs = None
            conn.ca_cert_dir = None
    else:
        conn.cert_reqs = "CERT_NONE"
        conn.ca_certs = None
        conn.ca_cert_dir = None

    if cert:
        if not isinstance(cert, str):
            conn.cert_file = cert[0]
            conn.key_file = cert[1]
        else:
            conn.cert_file = cert
            conn.key_file = None
        if conn.cert_file and not os.path.exists(conn.cert_file):
            raise OSError(f"Could not find the TLS certificate file, invalid path: {conn.cert_file}")
        if conn.key_file and not os.path.exists(conn.key_file):
            raise OSError(f"Could not find the TLS key file, invalid path: {conn.key_file}")


requests.adapters.HTTPAdapter.cert_verify = _cert_verify_without_file_check

from dds_cli.__main__ import dds_main  # noqa: E402  (import after patching requests)

if getattr(sys, "frozen", False):
    dds_main(sys.argv[1:])
else:
    dds_main()
