#!/bin/bash --login
# The --login ensures the bash configuration is loaded,

# Enable strict mode.
set -euo pipefail
# ... Run whatever commands ...

# Temporarily disable strict mode and activate conda:
set +euo pipefail
conda activate plugins-venv

# Re-enable strict mode:
set -euo pipefail

# exec the final command:
exec python ../runner.py