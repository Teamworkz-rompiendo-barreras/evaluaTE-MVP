#!/usr/bin/env python3
"""Update the generated date in the application status report.

This script replaces the line starting with "*Informe generado el:" in
``INFORME_ESTADO_APLICACION.md`` with the current date. The date format
used is ISO ``YYYY-MM-DD``.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

REPORT_PATH = Path("INFORME_ESTADO_APLICACION.md")


def main() -> None:
    content = REPORT_PATH.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    new_line = f"*Informe generado el: {today}*"
    updated = re.sub(r"\*Informe generado el:.*\*", new_line, content)
    REPORT_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
