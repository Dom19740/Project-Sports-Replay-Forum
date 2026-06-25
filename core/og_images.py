"""
Per-event Open Graph card generator.

Produces a 1200x630 spoiler-free social card for an Event showing the matchup
(or session) + the Hot/Mid/Not verdict. NEVER renders a score, winner, or any
result-revealing text — the verdict badge is the only signal.

Public API:
    resolve_verdict(event) -> dict   # which verdict to show + a cache token
    generate_og_card(event) -> bytes # PNG bytes, ready to serve / cache
"""

from __future__ import annotations

import os
from io import BytesIO

from django.conf import settings
from django.contrib.staticfiles import finders

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Layout constants
# --------------------------------------------------------------------------
W, H = 1200, 630
PANEL_X = 760                      # left edge of the right verdict panel
PAD = 56
BG = (22, 24, 28)
PANEL = (30, 33, 38)
TEXT = (240, 242, 245)
MUTED = (150, 156, 164)

# Theme per verdict. `logo` is a file under static/img/ (None => no badge art).
THEMES = {
    "hot_watch": {"label": "HOT WATCH",       "accent": (255, 107, 53),
                  "logo": "logo_flame_large.png", "sub": "Worth the full replay"},
    "mid_temp":  {"label": "MID TEMP",        "accent": (245, 166, 35),
                  "logo": "logo_mid.png",         "sub": "Catch the highlights"},
    "not_watch": {"label": "NOT WATCH",       "accent": (74, 144, 217),
                  "logo": "logo_cold.png",        "sub": "Skip to the result"},
    "awaiting":  {"label": "AWAITING VERDICT", "accent": (130, 140, 150),
                  "logo": None,                   "sub": "Rating coming soon"},
}

# Crowd star_label ("Hot"/"Mid"/"Not") -> theme key
_CROWD_MAP = {"Hot": "hot_watch", "Mid": "mid_temp", "Not": "not_watch"}

# Bundle a font under static/fonts/ in production. We try that first, then fall
# back to common system paths so this never hard-fails on a missing font.
_FONT_CANDIDATES_BOLD = [
    "fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_FONT_CANDIDATES_REG = [
    "fonts/Poppins-Regular.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


# --------------------------------------------------------------------------
# Asset / font resolution
# --------------------------------------------------------------------------
def _static_path(rel: str) -> str | None:
    """Absolute source path for a static asset, dev or prod (manifest-safe)."""
    found = finders.find(rel)
    if found:
        return found
    for base in getattr(settings, "STATICFILES_DIRS", []):
        cand = os.path.join(base, rel)
        if os.path.exists(cand):
            return cand
    return None


def _font_path(candidates: list[str]) -> str:
    for c in candidates:
        p = _static_path(c) if not c.startswith("/") else (c if os.path.exists(c) else None)
        if p:
            return p
    raise FileNotFoundError("No usable TTF font found; bundle one at static/fonts/")


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = _font_path(_FONT_CANDIDATES_BOLD if bold else _FONT_CANDIDATES_REG)
    return ImageFont.truetype(path, size)


def _fit_font(draw, text, max_w, start, bold=True, min_size=20):
    """Largest font (<= start) whose `text` fits within max_w."""
    size = start
    while size > min_size:
        f = _font(size, bold=bold)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return _font(min_size, bold=bold)


def _wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# Verdict resolution
# --------------------------------------------------------------------------
def resolve_verdict(event) -> dict:
    """
    Decide which verdict the card shows.

    Priority: crowd rating (if any votes) -> AI rating -> awaiting.
    Returns {"key", "source", "token"} where key indexes THEMES, source is one
    of {"crowd","ai","awaiting"}, and token is a short cache-busting string.

    To flip to AI-first, swap the two blocks below.
    """
    # --- crowd ---
    try:
        rating = event.rating
        votes = (rating.five_stars + rating.four_stars + rating.three_stars
                 + rating.two_stars + rating.one_star)
        if votes > 0:
            key = _CROWD_MAP.get(rating.star_label, "awaiting")
            return {"key": key, "source": "crowd", "token": f"crowd-{key}"}
    except Exception:
        pass

    # --- AI ---  (mirrors event view: shown unless flagged.
    #              change `!= FLAGGED` to `== PUBLISHED` for stricter gating.)
    try:
        from airatings.models import AIRating
        ai = event.ai_pipeline
        if ai and ai.status != AIRating.STATUS_FLAGGED and ai.verdict in THEMES:
            return {"key": ai.verdict, "source": "ai", "token": f"ai-{ai.verdict}"}
    except Exception:
        pass

    return {"key": "awaiting", "source": "awaiting", "token": "awaiting"}


def _headline_and_kicker(event):
    """Football: matchup is the headline. Motorsport: competition is."""
    et = (event.event_type or "").strip()
    comp = event.event_list.name
    if " vs " in et.lower():
        return et.replace(" vs ", " v ").replace(" VS ", " v "), event.event_list.league
    return comp, et or event.event_list.league


def _comp_logo_rel(event):
    """Best-effort competition logo under static/img/sports/."""
    league = event.event_list.league
    for rel in (f"img/sports/logo_{league}.png", f"img/sports/icon_{league}.png"):
        if _static_path(rel):
            return rel
    # known short aliases
    alias = {"Formula 1": "img/sports/logo_f1.png", "MotoGP": "img/sports/logo_motogp.png"}
    rel = alias.get(league)
    return rel if rel and _static_path(rel) else None


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def generate_og_card(event) -> bytes:
    v = resolve_verdict(event)
    th = THEMES[v["key"]]
    headline, kicker = _headline_and_kicker(event)
    comp_rel = _comp_logo_rel(event)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- right verdict panel ----
    d.rectangle([PANEL_X, 0, W, H], fill=PANEL)
    d.rectangle([PANEL_X, 0, PANEL_X + 8, H], fill=th["accent"])
    panel_w = W - PANEL_X

    has_logo = bool(th["logo"] and _static_path(f"img/{th['logo']}"))
    if has_logo:
        logo = Image.open(_static_path(f"img/{th['logo']}")).convert("RGBA")
        lh = 300
        lw = int(logo.width * lh / logo.height)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        img.paste(logo, (PANEL_X + (panel_w - lw) // 2, 120), logo)
        label_y, sub_y = 440, 500
    else:
        label_y, sub_y = 270, 340  # vertically centred when no badge art

    # verdict label (auto-fit to panel width) + sub
    lf = _fit_font(d, th["label"], panel_w - 48, 46)
    d.text((PANEL_X + (panel_w - d.textlength(th["label"], font=lf)) // 2, label_y),
           th["label"], font=lf, fill=th["accent"])
    sf = _font(24, bold=False)
    d.text((PANEL_X + (panel_w - d.textlength(th["sub"], font=sf)) // 2, sub_y),
           th["sub"], font=sf, fill=(200, 205, 212))
    if v["source"] == "ai":
        d.text((PANEL_X + 24, 30), "AI RATED", font=_font(20), fill=th["accent"])

    # ---- left content ----
    # SIWS wordmark — brand masthead, top-left
    if _static_path("img/logo-welcome.png"):
        mark = Image.open(_static_path("img/logo-welcome.png")).convert("RGBA")
        mh = 80
        mw = int(mark.width * mh / mark.height)
        mark = mark.resize((mw, mh), Image.LANCZOS)
        img.paste(mark, (PAD, 40), mark)

    # competition kicker + headline — left-justified, block vertically centred
    kf = _font(28)
    ktext = kicker.upper()
    ch = 52
    max_w = PANEL_X - PAD - 40
    hf = _fit_font(d, headline, max_w, 60, min_size=38)
    lines = _wrap(d, headline, hf, max_w)
    gap = 16
    line_h = int(hf.size * 1.18)
    block_h = ch + gap + len(lines[:3]) * line_h
    block_y = (H - block_h) // 2

    if comp_rel:
        cl = Image.open(_static_path(comp_rel)).convert("RGBA")
        cw = int(cl.width * ch / cl.height)
        cl = cl.resize((cw, ch), Image.LANCZOS)
        img.paste(cl, (PAD, block_y), cl)
        d.text((PAD + cw + 14, block_y + (ch - 28) // 2), ktext, font=kf, fill=MUTED)
    else:
        d.text((PAD, block_y + 12), ktext, font=kf, fill=MUTED)

    ty = block_y + ch + gap
    for ln in lines[:3]:
        d.text((PAD, ty), ln, font=hf, fill=TEXT)
        ty += line_h

    tagline = "Worth the replay?  Watch the highlights?"
    tf = _fit_font(d, tagline, PANEL_X - PAD - 24, 30, min_size=22)
    d.text((PAD, H - 112), tagline, font=tf, fill=(255, 255, 255))
    d.text((PAD, H - 66), "Decide without spoilers  ·  shouldiwatchsports.com",
           font=_font(24, bold=False), fill=MUTED)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
