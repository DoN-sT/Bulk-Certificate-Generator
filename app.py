"""
app.py
──────
Bulk Certificate Generator — Streamlit entry point.

Workflow:  Upload → Design → Preview → Generate → Download
           (Step 1)  (Step 2) (Step 3)  (Step 4)   (Step 5)

Run with:
    streamlit run app.py
"""

import io
import time
import copy

import streamlit as st
import pandas as pd

# ── Local modules ─────────────────────────────────────────────────────────────
from data_handler       import parse_uploaded_file, render_data_preview, get_available_placeholders
from template_handler   import template_editor_ui, render_preview, DEFAULT_LAYOUT
from certificate_engine import generate_single, generate_batch, GeneratedCert
from export_handler     import render_download_section

# ─── Page configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="Bulk Certificate Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Global reset ───────────────────────────────── */
:root {
  --bg:        #09090b;
  --surface:   #111113;
  --surface-2: #18181b;
  --border:    #27272a;
  --accent:    #3b82f6;
  --accent-dk: #1d4ed8;
  --text:      #f4f4f5;
  --muted:     #71717a;
  --success:   #22c55e;
  --radius:    8px;
}

/* ── Base ───────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ── Sidebar ────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Page headings ──────────────────────────────── */
.main-title {
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-bottom: 2px;
}
.main-subtitle {
  font-size: 0.8rem;
  color: var(--muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ── Step pills ─────────────────────────────────── */
.step-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.82rem;
  color: var(--muted);
  border: 1px solid transparent;
  margin-bottom: 4px;
}
.step-pill.active {
  background: #1c2033;
  border-color: var(--accent);
  color: #93c5fd;
  font-weight: 600;
}
.step-pill.done {
  color: var(--success);
}

/* ── Primary buttons ────────────────────────────── */
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  border-radius: var(--radius) !important;
  letter-spacing: 0.01em !important;
  transition: background 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent-dk) !important;
  box-shadow: 0 4px 16px rgba(59,130,246,0.3) !important;
}

/* ── Secondary buttons ──────────────────────────── */
.stButton > button {
  border-radius: var(--radius) !important;
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}
.stButton > button:hover {
  background: #27272a !important;
  border-color: #3f3f46 !important;
}

/* ── Inputs ─────────────────────────────────────── */
.stTextInput input,
.stSelectbox select,
.stNumberInput input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 6px !important;
}
.stTextInput input:focus,
.stSelectbox select:focus,
.stNumberInput input:focus {
  border-color: var(--accent) !important;
}

/* ── Dividers ───────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Metrics ────────────────────────────────────── */
[data-testid="stMetricValue"] { color: var(--accent) !important; }
[data-testid="stMetricLabel"] { color: var(--muted)  !important; }

/* ── Progress bar ───────────────────────────────── */
.stProgress > div > div > div {
  background: var(--accent) !important;
}

/* ── Expanders ──────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--surface-2) !important;
  border-radius: 6px !important;
  color: var(--text) !important;
}

/* ── Dataframe ──────────────────────────────────── */
.stDataFrame { border-radius: var(--radius) !important; }

/* ── Sidebar section text ───────────────────────── */
.sidebar-section {
  font-size: 0.78rem;
  color: var(--muted);
  line-height: 1.75;
}

/* ── Caption / small ────────────────────────────── */
.stCaption { color: var(--muted) !important; }

/* Circular upload area */
.stFileUploader > div[data-testid="stFileUploaderDropzone"] {
    border-radius: 50% !important;
    border: 2px dashed var(--border) !important;
    background: var(--surface) !important;
    padding: 40px !important;
    min-height: 200px !important;
    min-width: 200px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 auto !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--accent) !important;
    background: var(--surface-2) !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"] span {
    color: var(--text) !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Session state initialisation ─────────────────────────────────────────────

def _init_state() -> None:
    """Initialise all session-state keys with safe defaults."""
    defaults = {
        "step":           1,         # Current wizard step (1–5)
        "df":             None,      # Parsed participant DataFrame
        "template_img":   None,      # PIL Image of the template
        "layout":         copy.deepcopy(DEFAULT_LAYOUT),
        "fmt":            "png",     # Output format
        "certs":          [],        # List[GeneratedCert]
        "preview_cert":   None,      # bytes of sample preview cert
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def _render_sidebar() -> None:
    """Render the sidebar with workflow progress and app info."""
    with st.sidebar:
        st.markdown(
            '<div class="main-title" style="font-size:1.6rem">🎓 CertGen</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="main-subtitle" style="font-size:0.75rem">Bulk Certificate Generator</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        steps = [
            (1, "Upload",    "📤"),
            (2, "Design",    "🎨"),
            (3, "Preview",   "👁️"),
            (4, "Generate",  "⚙️"),
            (5, "Download",  "⬇️"),
        ]

        current = st.session_state.step
        st.markdown("**Workflow Progress**")
        for num, label, icon in steps:
            cls = "done" if num < current else ("active" if num == current else "")
            check = "✓ " if num < current else f"{icon} "
            st.markdown(
                f'<div class="step-pill {cls}">{check}Step {num}: {label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")

        st.divider()

        # Quick nav (only go backward)
        st.markdown("**Quick Navigation**")
        nav_labels = {1: "📤 Upload", 2: "🎨 Design", 3: "👁 Preview",
                      4: "⚙️ Generate", 5: "⬇️ Download"}
        for num, label in nav_labels.items():
            if num < current:
                if st.button(label, key=f"nav_{num}", use_container_width=True):
                    st.session_state.step = num
                    st.rerun()

        st.divider()
        st.markdown(
            '<div class="sidebar-section">'
            '🔒 <b>100% Offline</b><br>'
            'No data leaves your machine.<br><br>'
            '⚡ <b>Multiprocessing</b><br>'
            'Parallel generation on all CPU cores.<br><br>'
            '📄 PNG &amp; PDF output<br>'
            '📦 Bulk ZIP download'
            '</div>',
            unsafe_allow_html=True,
        )


# ─── Step 1 — Upload Data ─────────────────────────────────────────────────────

def _step_upload() -> None:
    st.markdown('<div class="main-title">📤 Upload Data</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    uploaded = st.file_uploader(
        "Choose CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        label_visibility="visible",
    )

    if uploaded:
        with st.spinner("Processing file…"):
            df = parse_uploaded_file(uploaded)

        if df is not None:
            st.success(f"✅ **{len(df)} records loaded** from `{uploaded.name}`")
            render_data_preview(df)
            st.session_state.df = df

            st.markdown("---")
            if st.button("Next: Design Certificate →", type="primary", use_container_width=True):
                st.session_state.step = 2
                st.rerun()


# ─── Step 2 — Design ──────────────────────────────────────────────────────────

def _step_design() -> None:
    st.markdown('<div class="main-title">🎨 Design Certificate</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    df = st.session_state.df
    if df is None:
        st.warning("Please complete Step 1 first.")
        return

    df_cols = list(df.columns)

    sample_row = df.iloc[0].to_dict()
    # Template editor returns (template_img, layout)
    tpl_img, layout = template_editor_ui(
        df_columns=df_cols,
        initial_layout=st.session_state.layout,
        sample_data=sample_row,
    )

    # Output format
    st.divider()
    st.markdown("### 📄 Output Format")
    fmt = st.radio(
        "Select output format",
        ["PNG (image)", "PDF (document)"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.fmt = "pdf" if "PDF" in fmt else "png"

    st.divider()
    if st.button("Preview Sample Certificate →", type="primary", use_container_width=True, disabled=tpl_img is None):
        if tpl_img is None:
            st.error("Please upload a template image first")
        else:
            st.session_state.template_img = tpl_img
            st.session_state.layout       = layout
            st.session_state.step         = 3
            st.rerun()


# ─── Step 3 — Preview ─────────────────────────────────────────────────────────

def _step_preview() -> None:
    st.markdown('<div class="main-title">👁️ Preview</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    df      = st.session_state.df
    tpl_img = st.session_state.template_img
    layout  = st.session_state.layout

    if df is None:
        st.warning("Please complete Step 1 first.")
        return
    
    if tpl_img is None:
        st.warning("Please complete Step 2 first and upload a template.")
        return

    # Let user choose which participant to preview
    # Use the first column as the label (doesn't assume a "Name" column)
    first_col = df.columns[0]
    row_labels = df[first_col].tolist()
    choice     = st.selectbox(f"Select row to preview (by **{first_col}**)", row_labels)
    record     = df[df[first_col] == choice].iloc[0].to_dict()

    # Render live preview
    preview = render_preview(tpl_img, layout, sample_data=record)

    # Show preview image
    buf = io.BytesIO()
    preview.save(buf, format="PNG")
    st.image(buf.getvalue(), caption=f"Preview — {choice}", use_container_width=True)

    # Also generate a downloadable sample
    with st.spinner("Rendering full-res sample…"):
        sample_bytes = generate_single(record, tpl_img, layout, st.session_state.fmt)

    st.session_state.preview_cert = sample_bytes

    mime = "application/pdf" if st.session_state.fmt == "pdf" else "image/png"
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            f"⬇️ Download this sample ({st.session_state.fmt.upper()})",
            data=sample_bytes,
            file_name=f"sample_{choice}.{st.session_state.fmt}",
            mime=mime,
        )
    with col2:
        if st.button("← Back to Design", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

    st.divider()
    if st.button("✅ Looks good — Generate All Certificates →",
                 type="primary", use_container_width=True):
        st.session_state.step = 4
        st.rerun()


# ─── Step 4 — Generate ────────────────────────────────────────────────────────

def _step_generate() -> None:
    st.markdown('<div class="main-title">⚙️ Generate</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    df      = st.session_state.df
    tpl_img = st.session_state.template_img
    layout  = st.session_state.layout
    fmt     = st.session_state.fmt

    if df is None:
        st.warning("Please complete Step 1 first.")
        return
    
    if tpl_img is None:
        st.warning("Please complete Step 2 first and upload a template.")
        return

    total = len(df)
    st.markdown(f"Ready to generate **{total} certificates** in **{fmt.upper()}** format.")

    if st.button(f"🚀 Generate {total} Certificates", type="primary", use_container_width=True):

        # ── Progress tracking ────────────────────────────────────────────────
        progress_bar  = st.progress(0.0, text="Starting generation…")
        status_text   = st.empty()
        start_time    = time.time()

        completed_count = [0]  # mutable container for closure

        def _progress_cb(done: int, total_count: int) -> None:
            completed_count[0] = done
            pct  = done / total_count
            elapsed = time.time() - start_time
            rate    = done / elapsed if elapsed > 0 else 0
            eta     = (total_count - done) / rate if rate > 0 else 0

            progress_bar.progress(
                pct,
                text=f"Generating… {done}/{total_count}  •  "
                     f"{rate:.1f}/s  •  ETA {eta:.0f}s",
            )
            _label_col = df.columns[0]
            status_text.markdown(
                f"<small style='color:#71717a'>Processing: "
                f"**{df.iloc[done-1][_label_col]}**</small>",
                unsafe_allow_html=True,
            )

        with st.spinner(""):
            certs = generate_batch(
                df=df,
                template_img=tpl_img,
                layout=layout,
                fmt=fmt,
                progress_cb=_progress_cb,
            )

        elapsed = time.time() - start_time
        progress_bar.progress(1.0, text="✅ All certificates generated!")
        status_text.empty()

        st.session_state.certs = certs

        # ── Stats ────────────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric("🎓 Certificates", len(certs))
        m2.metric("⏱️ Time taken", f"{elapsed:.1f}s")
        m3.metric("⚡ Rate", f"{len(certs)/elapsed:.1f}/s")

        st.success(f"✅ Generated {len(certs)} certificates in {elapsed:.1f} seconds!")

        if st.button("Proceed to Download →", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()

    elif st.session_state.certs:
        st.success(f"Previously generated {len(st.session_state.certs)} certificates.")
        if st.button("Proceed to Download →", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()


# ─── Step 5 — Download ────────────────────────────────────────────────────────

def _step_download() -> None:
    st.markdown('<div class="main-title">⬇️ Download</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    certs = st.session_state.certs

    if not certs:
        st.warning("No certificates generated yet. Please complete Step 4.")
        if st.button("← Go to Generate"):
            st.session_state.step = 4
            st.rerun()
        return

    render_download_section(certs)

    st.divider()
    if st.button("🔄 Start a new batch", use_container_width=True):
        # Reset all state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ─── Main orchestrator ────────────────────────────────────────────────────────

def main() -> None:
    """Route to the correct step based on st.session_state.step."""
    _render_sidebar()

    step = st.session_state.step

    if   step == 1: _step_upload()
    elif step == 2: _step_design()
    elif step == 3: _step_preview()
    elif step == 4: _step_generate()
    elif step == 5: _step_download()
    else:
        st.error("Unknown step. Resetting…")
        st.session_state.step = 1
        st.rerun()


if __name__ == "__main__":
    main()
