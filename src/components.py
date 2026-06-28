"""Reusable HTML components for the KinetiX dark AI theme."""

import streamlit as st

# ── SVG Icons (Phosphor) ──────────────────────────────────────────────────────

ICONS = {
    "data":       '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M224,200h-8V40a8,8,0,0,0-8-8H152a8,8,0,0,0-8,8V80H96a8,8,0,0,0-8,8v40H48a8,8,0,0,0-8,8v64H32a8,8,0,0,1,0,16H224a8,8,0,0,1,0-16Z"/></svg>',
    "search":     '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M229.66,218.34l-50.07-50.07a88,88,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.31ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"/></svg>',
    "play":       '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M240,128a15.74,15.74,0,0,1-7.6,13.51L88.32,229.65a16,16,0,0,1-16.2.3A15.86,15.86,0,0,1,64,216.13V39.87a15.86,15.86,0,0,1,8.12-13.82,16,16,0,0,1,16.2.3L232.4,114.49A15.74,15.74,0,0,1,240,128Z"/></svg>',
    "layers":     '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M243.31,90.91l-128-64a8,8,0,0,0-7.16,0l-128,64a8,8,0,0,0,0,14.18l128,64a8,8,0,0,0,7.16,0l128-64a8,8,0,0,0,0-14.18ZM128,138.75,28.29,88,128,37.25,227.71,88ZM237.31,165.09l-109.31,55L18.69,165.09a8,8,0,0,0-7.16,14.17l112,56a8,8,0,0,0,7.16,0l112-56a8,8,0,1,0-7.38-14.17Z"/></svg>',
    "warning":    '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M236.8,188.09,149.35,36.65a24.76,24.76,0,0,0-42.7,0L19.2,188.09a23.51,23.51,0,0,0,0,23.72A24.35,24.35,0,0,0,40.55,224h174.9a24.35,24.35,0,0,0,21.33-12.19A23.51,23.51,0,0,0,236.8,188.09ZM120,104a8,8,0,0,1,16,0v40a8,8,0,0,1-16,0Zm8,88a12,12,0,1,1,12-12A12,12,0,0,1,128,192Z"/></svg>',
    "check":      '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"/></svg>',
    "file":       '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"/></svg>',
    "lightbulb":  '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M176,232a8,8,0,0,1-8,8H88a8,8,0,0,1,0-16h80A8,8,0,0,1,176,232Zm40-128a87.55,87.55,0,0,1-33.64,69.21A16.24,16.24,0,0,1,176,186v6a16,16,0,0,1-16,16H96a16,16,0,0,1-16-16v-6a16,16,0,0,1-6.23-12.66A87.59,87.59,0,0,1,40,104a88,88,0,0,1,176,0Z"/></svg>',
    "download":   '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M224,152v56a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V152a8,8,0,0,1,16,0v56H208V152a8,8,0,0,1,16,0Zm-101.66-77.66-32,32a8,8,0,0,0,11.32,11.32L120,99.31V192a8,8,0,0,0,16,0V99.31l18.34,18.35a8,8,0,0,0,11.32-11.32l-32-32A8,8,0,0,0,122.34,74.34Z"/></svg>',
    "services":   '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M224,200h-8V40a8,8,0,0,0-8-8H152a8,8,0,0,0-8,8V80H96a8,8,0,0,0-8,8v40H48a8,8,0,0,0-8,8v64H32a8,8,0,0,1,0,16H224a8,8,0,0,1,0-16Z"/></svg>',
    "target":     '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Zm-32,0a56,56,0,1,1-56-56A56.06,56.06,0,0,1,184,128Zm-16,0a40,40,0,1,0-40,40A40,40,0,0,0,168,128Zm-16,0a24,24,0,1,1-24-24A24,24,0,0,1,152,128Z"/></svg>',
    "money":      '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm40-68a28,28,0,0,1-28,28h-4v8a8,8,0,0,1-16,0v-8H104a8,8,0,0,1,0-16h36a12,12,0,0,0,0-24H116a28,28,0,0,1,0-56h4V72a8,8,0,0,1,16,0v8h16a8,8,0,0,1,0,16H116a12,12,0,0,0,0,24h24A28,28,0,0,1,168,148Z"/></svg>',
    "chart":      '<svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor"><path d="M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1-8-8V48a8,8,0,0,1,16,0v94.37L90.73,98a8,8,0,0,1,10.07-.38l58.81,44.11L218.73,90a8,8,0,1,1,10.54,12.06l-64,56a8,8,0,0,1-10.07.38L96.39,114.29,40,163.63V200H224A8,8,0,0,1,232,208Z"/></svg>',
}


# ── Divider ───────────────────────────────────────────────────────────────────

def divider():
    st.markdown("""
        <div style="
          height:1px;
          background: linear-gradient(90deg,
            transparent 0%,
            rgba(84,84,84,0.5) 20%,
            rgba(84,84,84,0.5) 80%,
            transparent 100%);
          margin: 32px 0;
        "></div>
    """, unsafe_allow_html=True)


# ── Page Header with ambient glow ─────────────────────────────────────────────

def page_header(title: str, subtitle: str, tag: str):
    st.markdown(f"""
        <div style="
          position: relative;
          text-align: center;
          padding: 60px 40px 48px 40px;
          margin-bottom: 48px;
          overflow: hidden;
        ">
          <div style="
            position:absolute; top:0; left:50%; transform:translateX(-50%);
            width:600px; height:300px;
            background: radial-gradient(ellipse at 50% 0%,
              rgba(64,242,154,0.12) 0%, transparent 70%);
            pointer-events:none;
          "></div>
          <div style="
            position:absolute; top:-40px; left:-20px; width:250px; height:240px;
            background: linear-gradient(270deg, transparent 0%,
              rgba(149,244,71,0.15) 50%, transparent 100%);
            transform: rotate(-45deg);
            pointer-events:none;
          "></div>
          <div style="
            position:absolute; top:-40px; right:-20px; width:250px; height:240px;
            background: linear-gradient(270deg, transparent 0%,
              rgba(149,244,71,0.15) 50%, transparent 100%);
            transform: rotate(45deg);
            pointer-events:none;
          "></div>
          <div style="
            display:inline-block;
            background: rgb(30,59,12);
            color: rgb(64,242,154);
            border: 1px solid rgba(64,242,154,0.35);
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 20px;
            font-family: Inter, sans-serif;
          ">{tag}</div>
          <h1 style="
            font-family: Inter, sans-serif;
            font-weight: 500;
            font-size: clamp(32px, 4vw, 52px);
            color: rgb(255,255,255);
            margin: 0 0 16px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
            position: relative;
          ">{title}</h1>
          <p style="
            font-family: Inter, sans-serif;
            font-weight: 400;
            font-size: 16px;
            color: rgb(128,128,128);
            margin: 0 auto;
            max-width: 560px;
            line-height: 1.6;
            position: relative;
          ">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)


# ── Section header (lighter, no glow) ─────────────────────────────────────────

def section_header(tag: str, title: str, subtitle: str = ""):
    sub_html = f"""
        <p style="color:rgb(128,128,128); font-family:Inter,sans-serif;
                  font-size:14px; font-weight:400; max-width:600px;
                  margin:4px auto 0; text-align:center;">{subtitle}</p>
    """ if subtitle else ""
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:32px;">
          <span style="background:rgb(30,59,12); color:rgb(64,242,154);
                       font-family:Inter,sans-serif; font-size:11px; font-weight:600;
                       padding:4px 12px; border-radius:20px;
                       border:1px solid rgba(64,242,154,0.3);
                       display:inline-block; margin-bottom:12px;
                       text-transform:uppercase; letter-spacing:0.08em;">{tag}</span>
          <h2 style="color:rgb(255,255,255); font-family:Inter,sans-serif;
                     font-weight:500; font-size:28px; margin:0;">{title}</h2>
          {sub_html}
        </div>
    """, unsafe_allow_html=True)


# ── KPI card (single) ─────────────────────────────────────────────────────────

def _kpi_card_html(icon_svg: str, label: str, value: str,
                   delta: str = None, positive: bool = True) -> str:
    delta_html = ""
    if delta:
        c  = "rgb(64,242,154)" if positive else "rgb(220,80,80)"
        bg = "rgb(30,59,12)"   if positive else "rgba(200,50,50,0.15)"
        delta_html = (
            f'<span style="background:{bg};color:{c};padding:2px 8px;'
            f'border-radius:6px;font-size:12px;font-weight:600;'
            f'margin-left:8px;">{delta}</span>'
        )
    return f"""
        <div style="
          background: rgb(13,13,13);
          border: 1px solid rgba(84,84,84,0.5);
          border-radius: 14px;
          padding: 24px;
          font-family: Inter, sans-serif;
          box-shadow: inset 0px 2px 1px rgba(64,242,154,0.15),
                      0px 0px 8px rgba(64,242,154,0.12);
          position: relative;
          overflow: hidden;
          flex: 1;
          min-width: 0;
        ">
          <div style="
            position:absolute; bottom:-30px; right:-20px;
            width:120px; height:120px; border-radius:50%;
            background: radial-gradient(circle, rgba(64,242,154,0.06) 0%,
                        transparent 70%);
            pointer-events:none;
          "></div>
          <div style="
            background:rgba(0,0,0,0.8);
            border: 1px solid rgba(84,84,84,0.5);
            border-radius:10px; padding:8px;
            display:inline-flex; margin-bottom:16px;
            color: rgb(64,242,154);
            box-shadow: 0px 0.7px 0.7px rgba(149,245,71,0.08),
                        0px 1.8px 1.8px rgba(149,245,71,0.08),
                        0px 3.6px 3.6px rgba(149,245,71,0.08);
          ">{icon_svg}</div>
          <div style="color:rgb(128,128,128);font-size:11px;font-weight:600;
                      text-transform:uppercase;letter-spacing:0.08em;
                      margin-bottom:8px;">{label}</div>
          <div style="color:rgb(255,255,255);font-size:26px;font-weight:700;
                      display:flex;align-items:baseline;flex-wrap:wrap;
                      gap:6px;line-height:1.3;">
            <span>{value}</span>{delta_html}
          </div>
        </div>
    """


def render_kpi_row(cards: list[dict]):
    """Render a row of KPI cards. Each dict: {icon, label, value, delta?, positive?}"""
    html_parts = []
    for c in cards:
        html_parts.append(_kpi_card_html(
            c.get("icon", ""),
            c["label"],
            c["value"],
            c.get("delta"),
            c.get("positive", True),
        ))
    combined = "\n".join(html_parts)
    st.markdown(f"""
        <div style="display:flex; gap:16px; margin-bottom:32px;">
          {combined}
        </div>
    """, unsafe_allow_html=True)


# ── Status badge ──────────────────────────────────────────────────────────────

def status_badge(text: str, variant: str = "success") -> str:
    colours = {
        "success": ("rgb(30,59,12)", "rgb(64,242,154)"),
        "warning": ("rgba(200,150,0,0.15)", "rgb(240,190,0)"),
        "error":   ("rgba(200,50,50,0.15)", "rgb(220,80,80)"),
        "neutral": ("rgb(51,51,51)", "rgb(209,209,209)"),
    }
    bg, fg = colours.get(variant, colours["neutral"])
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border-radius:20px;font-family:Inter,sans-serif;'
        f'font-size:11px;font-weight:500;">{text}</span>'
    )


# ── Sidebar branding ─────────────────────────────────────────────────────────

def render_sidebar_brand():
    st.markdown("""
        <div style="padding: 20px 16px 20px 16px;
                    border-bottom: 1px solid rgba(84,84,84,0.5);
                    margin-bottom: 16px;">
          <div style="font-family: Inter, sans-serif; font-size: 24px;
                      font-weight: 700; color: rgb(255,255,255);
                      letter-spacing: -0.03em; margin-bottom: 4px;">
            Kineti<span style="color: rgb(64,242,154);">X</span>
          </div>
          <div style="font-family: Inter, sans-serif; font-size: 12px;
                      color: rgb(128,128,128); font-weight: 400;">
            ESADE MiBA Capstone
          </div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar_footer():
    st.markdown("""
        <div style="
          margin-top: 40px;
          background: rgb(13,13,13);
          border: 1px solid rgba(84,84,84,0.5);
          border-radius: 10px;
          padding: 16px;
          font-family: Inter, sans-serif;
        ">
          <div style="color:rgb(64,242,154);font-size:11px;font-weight:600;
                      text-transform:uppercase;letter-spacing:0.08em;
                      margin-bottom:8px;">HOW TO USE</div>
          <div style="color:rgb(128,128,128);font-size:13px;line-height:1.5;">
            Navigate the sections above to explore data, run scenarios,
            and export results.
          </div>
        </div>
    """, unsafe_allow_html=True)


# ── Metadata bar ──────────────────────────────────────────────────────────────

def info_block(title: str, content: str):
    """A styled always-visible info section - replaces st.expander."""
    st.markdown(f"""
        <div style="
          background: rgb(13,13,13);
          border: 1px solid rgba(84,84,84,0.5);
          border-radius: 12px;
          padding: 24px;
          margin: 16px 0;
          font-family: Inter, sans-serif;
        ">
          <div style="color:rgb(64,242,154); font-size:12px; font-weight:600;
                      text-transform:uppercase; letter-spacing:0.08em;
                      margin-bottom:12px; display:flex; align-items:center; gap:8px;">
            <span style="font-size:16px;">📘</span> {title}
          </div>
          <div style="color:rgb(161,161,161); font-size:14px; line-height:1.7;">
            {content}
          </div>
        </div>
    """, unsafe_allow_html=True)


def render_metadata_bar():
    st.markdown("""
        <div style="
          display: flex; align-items: center; gap: 8px;
          font-family: Inter, sans-serif; font-size: 14px;
          color: rgb(128,128,128); margin-bottom: 32px;
          padding-bottom: 24px;
          border-bottom: 1px solid rgba(84,84,84,0.4);
          flex-wrap: wrap;
        ">
          <span style="color:rgb(209,209,209);font-weight:500;">
            ESADE MiBA Capstone
          </span>
          <span>&middot;</span>
          <span>In collaboration with</span>
          <span style="color:rgb(64,242,154);font-weight:600;">KinetiX</span>
          <span style="margin-left:8px; padding-left:8px;
                       border-left:1px solid rgba(84,84,84,0.5);">
            Data period: March 2024 &ndash; March 2025
          </span>
        </div>
    """, unsafe_allow_html=True)
