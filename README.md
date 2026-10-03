# Sloppy Research

A little website for AI generated stuff.

## Build

Needs [just](https://github.com/casey/just) and Python 3.

```
just setup   # create venv, install deps (once)
just gen     # generate into public/
```

## Layout

- `src/`   — source content: MIME-style headers (title:, date:, tldr:, ...)
  followed by Markdown. `.collection` files render lists + Atom feeds.
- `template/` — Jinja2 templates (`page.html`, `collection.html`, `.atom`).
- `gen.py` — the generator (adapted from beza1e1.tuxen.de).
- `config.ini` — site-wide config (base_url, title, author). Set `base_url`
  to the real domain before deploying.
