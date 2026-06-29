from __future__ import annotations

import argparse

from auto_research.ui_server import app


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local auto-research UI.")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
