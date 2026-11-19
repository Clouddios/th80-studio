"""Where the app reads bundled resources and writes results, backups and logs."""
import sys
from pathlib import Path

RESOURCES=Path(__file__).resolve().parent
if getattr(sys,'frozen',False) and sys.platform=='darwin':
    # A packaged .app is read-only and signed; keep user data outside the bundle.
    DATA=Path.home()/'Library'/'Application Support'/'TH80 Studio'
    DATA.mkdir(parents=True,exist_ok=True)
else:
    DATA=RESOURCES
