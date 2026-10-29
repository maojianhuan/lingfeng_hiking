"""Entry point for the Windows executable."""
import sys
from pathlib import Path

from streamlit.web import cli
import duties
import finance  # Included explicitly: app.py is loaded dynamically by Streamlit.


def main():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    sys.argv = [
        'streamlit', 'run', str(root / 'app.py'),
        '--global.developmentMode=false',
        '--server.address=127.0.0.1',
        '--server.port=8501',
        '--server.headless=false',
        '--browser.serverAddress=localhost',
        '--browser.gatherUsageStats=false',
    ]
    cli.main()


if __name__ == '__main__':
    main()
