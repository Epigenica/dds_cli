.. _installation:

Installation guide
####################

Download the latest release for your operating system from the
`|org| DDS CLI releases page <https://github.com/Epigenica/dds_cli/releases>`_.

.. list-table::
   :header-rows: 1
   :widths: 30 40

   * - Operating system
     - File to download
   * - macOS (Apple Silicon)
     - ``dds_cli_macos_arm64``
   * - macOS (Intel)
     - ``dds_cli_macos_x86_64``
   * - Linux (Ubuntu latest)
     - ``dds_cli_ubuntu-latest_x86_64``
   * - Linux (Ubuntu 24.04)
     - ``dds_cli_ubuntu-24.04_x86_64``
   * - Linux (Ubuntu 22.04)
     - ``dds_cli_ubuntu-22.04_x86_64``
   * - Windows
     - ``dds_cli_win_x86_64.exe``


.. _mac-linux:

macOS / Linux
==============

1. Download the binary for your OS from the `releases page <https://github.com/Epigenica/dds_cli/releases>`_.

2. Open a terminal in the folder where you downloaded the file and make it executable:

   .. code-block:: bash

      chmod +x dds_cli_*

3. Move it to a directory on your PATH so you can run it from anywhere:

   .. code-block:: bash

      mv dds_cli_* /usr/local/bin/dds

4. Verify the installation:

   .. code-block:: bash

      dds --version

.. admonition:: macOS users

   On macOS, the first time you run the binary your system may block it because it is not from the App Store. To allow it, go to **System Settings → Privacy & Security** and click *Open Anyway*, or run:

   .. code-block:: bash

      xattr -d com.apple.quarantine /usr/local/bin/dds


.. _windows:

Windows
=======

1. Download ``dds_cli_win_x86_64.exe`` from the `releases page <https://github.com/Epigenica/dds_cli/releases>`_.

2. Rename it to ``dds.exe`` and place it in a folder that is on your PATH (for example ``C:\Users\<you>\bin``).

3. Open **PowerShell** or **Command Prompt** and verify:

   .. code-block:: powershell

      dds --version


.. _usage:

Basic usage
===========

Log in to the |org| Data Delivery System:

.. code-block:: bash

   dds auth login

List your projects:

.. code-block:: bash

   dds ls

Download all data from a project:

.. code-block:: bash

   dds data get -p <project-id> -a --verify-checksum

For a full list of commands and options, run ``dds --help`` or ``dds <command> --help``.
