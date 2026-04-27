from __future__ import annotations

import json
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE_DIR / "web" / "dashboard_online"
TARGET_DIR = BASE_DIR / "saida" / "dashboard_online_publico"


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    shutil.copytree(SOURCE_DIR, TARGET_DIR)

    write_text(TARGET_DIR / ".nojekyll", "")
    write_text(
        TARGET_DIR / "vercel.json",
        json.dumps(
            {
                "cleanUrls": True,
                "trailingSlash": False,
                "headers": [
                    {
                        "source": "/(.*)",
                        "headers": [
                            {"key": "Cache-Control", "value": "public, max-age=300"}
                        ],
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write_text(
        TARGET_DIR / "netlify.toml",
        """
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=300"
""".strip()
        + "\n",
    )
    write_text(
        TARGET_DIR / "README_DEPLOY.md",
        """
# Dashboard Online Publico

Esta pasta esta pronta para subir em hospedagem estatica.

Opcoes recomendadas:
- Vercel
- Netlify
- GitHub Pages

Arquivos incluidos:
- index.html
- app.css
- app.js
- supabase-config.js
- .nojekyll
- vercel.json
- netlify.toml

Origem:
- web/dashboard_online
""".strip()
        + "\n",
    )

    print(f"Pacote pronto para hospedagem: {TARGET_DIR}")


if __name__ == "__main__":
    main()
