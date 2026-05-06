
# ============================================================
# Delivery PoD Telemetry Dashboard — Academic Field-Test Explorer
# Streamlit + Folium
# ============================================================
# Run:
#   pip install streamlit pandas numpy folium streamlit-folium requests
#   python -m streamlit run app_improved.py
#   python -m streamlit run app.py --server.headless true --server.port 8501 --server.address localhost --server.enableCORS false --server.enableXsrfProtection false
# ============================================================

from __future__ import annotations

import pathlib
from typing import Optional

import folium
import numpy as np
import pandas as pd
import requests
import streamlit as st
from folium.plugins import AntPath
from streamlit_folium import st_folium

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PoD Telemetry Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Design system — Cohere-inspired theme (DESIGN.md)
# ------------------------------------------------------------------
_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Space Grotesk', ui-sans-serif, system-ui, -apple-system, sans-serif;
    color: #212121;
}
.stApp { background-color: #ffffff; }

/* ---- Sidebar (light, consistent with main) ---- */
section[data-testid="stSidebar"] {
    background-color: #f7f6f3;
    border-right: 1px solid #e5e7eb;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] div {
    color: #212121 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #17171c !important;
    font-family: 'Inter', ui-sans-serif, system-ui !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px !important;
    border-bottom: 2px solid #17171c;
    padding-bottom: 0.35rem !important;
    margin-bottom: 0.5rem !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #d9d9dd !important;
    margin: 0.5rem 0 !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="input"] input {
    background-color: #ffffff !important;
    color: #212121 !important;
    border-color: #d9d9dd !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #212121 !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #ffffff !important;
    color: #212121 !important;
    border: 1px solid #d9d9dd !important;
}

/* ---- Headings ---- */
h1 {
    font-family: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif !important;
    letter-spacing: -1.44px !important;
    font-weight: 400 !important;
    color: #17171c !important;
    line-height: 1.0 !important;
}
h2 {
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
    letter-spacing: -0.48px !important;
    font-weight: 400 !important;
    color: #17171c !important;
}
h3, h4 {
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
    letter-spacing: -0.32px !important;
    font-weight: 400 !important;
    color: #17171c !important;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
    background: #eeece7;
    border-radius: 16px;
    padding: 1rem 1.25rem;
    border: none;
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    color: #75758a !important;
    text-transform: uppercase;
    letter-spacing: 0.28px;
}
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', ui-sans-serif, system-ui !important;
    color: #17171c !important;
    font-weight: 500 !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #d9d9dd;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', ui-sans-serif, system-ui !important;
    font-size: 14px;
    font-weight: 500;
    color: #75758a !important;
    padding: 12px 24px;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #17171c !important;
    border-bottom-color: #17171c !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #212121 !important;
}

/* ---- Buttons ---- */
.stButton > button,
.stDownloadButton > button {
    font-family: 'Inter', ui-sans-serif, system-ui !important;
    font-size: 14px;
    font-weight: 500;
    background-color: #17171c !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 32px !important;
    padding: 0.5rem 1.5rem;
    line-height: 1.71;
    transition: opacity 0.2s;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    opacity: 0.85;
    background-color: #17171c !important;
    color: #ffffff !important;
}
.stButton > button:focus,
.stDownloadButton > button:focus {
    box-shadow: 0 0 0 2px #4c6ee6 !important;
}

/* ---- Radio & Checkbox (readability) ---- */
.stRadio > label,
.stCheckbox > label {
    color: #212121 !important;
    font-weight: 500 !important;
}
.stRadio [role="radiogroup"] label,
.stRadio [role="radiogroup"] label p,
.stRadio [role="radiogroup"] label span,
.stCheckbox label span {
    color: #212121 !important;
}

/* ---- Containers ---- */
[data-testid="stDataFrame"] {
    border: 1px solid #d9d9dd;
    border-radius: 8px;
    overflow: hidden;
}
[data-testid="stExpander"] {
    border: 1px solid #d9d9dd !important;
    border-radius: 8px !important;
}
hr { border-color: #d9d9dd !important; }
[data-testid="stCaptionContainer"] {
    color: #75758a !important;
    font-size: 14px;
}
.stAlert { border-radius: 8px; }
[data-baseweb="tag"] {
    border-radius: 30px !important;
    background-color: #eeece7 !important;
    color: #212121 !important;
}

/* ---- Node nav buttons (smaller pill) ---- */
.node-nav-row .stButton > button {
    padding: 0.25rem 0.6rem !important;
    font-size: 16px !important;
    min-height: 0 !important;
    line-height: 1.2 !important;
}
</style>
"""
st.markdown(_THEME_CSS, unsafe_allow_html=True)

TZ = "Asia/Kuala_Lumpur"
DEFAULT_CSV = pathlib.Path(__file__).parent / "supabase_data" / "field_test_records_rows.csv"

# Fixed evaluation criteria used for analysis labels only.
CONFIDENCE_THRESHOLD = 0.80
GPS_THRESHOLD_METRES = 10.0
LATENCY_THRESHOLD_MS = 1000.0
COORD_TOL_METRES = 12.0
TIME_DISPLAY_UNIT = "Milliseconds (ms)"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def safe_pct(num: float, den: float) -> float:
    return (num / den * 100.0) if den else 0.0


def fmt_ms(value: object) -> str:
    if pd.isna(value):
        return "N/A"

    value = float(value)
    unit = st.session_state.get("time_display_unit", TIME_DISPLAY_UNIT)
    if unit == "Seconds (s)":
        return f"{value / 1000.0:.2f} s"
    return f"{value:.0f} ms"


def fmt_num(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):.{digits}f}"


def fmt_pct(value: object, digits: int = 1) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.{digits}f}%"


def try_to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def bool_to_text(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return "Yes" if bool(value) else "No"


def status_label(row: pd.Series) -> str:
    if bool(row.get("upload_success", False)) is False:
        return "Upload failed"

    gt = row.get("ground_truth_is_building")
    pred = row.get("building_detected")
    overridden = bool(row.get("detection_overridden", False))

    if pd.notna(gt):
        if bool(pred) == bool(gt):
            return "Correct"
        if overridden:
            return "Overridden"
        return "Mismatch"

    return "Uploaded"


def status_color(label: str) -> str:
    return {
        "Correct": "#003c33",
        "Overridden": "#ff7759",
        "Mismatch": "#b30000",
        "Upload failed": "#75758a",
        "Uploaded": "#1863dc",
    }.get(label, "#1863dc")


def build_confusion_counts(df: pd.DataFrame) -> dict[str, int]:
    labeled = df[df["ground_truth_is_building"].notna()].copy()
    if labeled.empty:
        return {"TP": 0, "FP": 0, "TN": 0, "FN": 0}

    y_true = labeled["ground_truth_is_building"].astype(bool)
    y_pred = labeled["building_detected"].astype(bool)

    tp = int(((y_true == True) & (y_pred == True)).sum())
    tn = int(((y_true == False) & (y_pred == False)).sum())
    fp = int(((y_true == False) & (y_pred == True)).sum())
    fn = int(((y_true == True) & (y_pred == False)).sum())
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn}


def precision_recall_f1(counts: dict[str, int]) -> tuple[float, float, float, float]:
    tp, fp, tn, fn = counts["TP"], counts["FP"], counts["TN"], counts["FN"]
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total else 0.0

    precision_den = tp + fp
    recall_den = tp + fn
    precision = tp / precision_den if precision_den else 0.0
    recall = tp / recall_den if recall_den else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return accuracy, precision, recall, f1


def quality_band_confidence(x: float) -> str:
    if pd.isna(x):
        return "Unknown"
    return "High" if x >= CONFIDENCE_THRESHOLD else "Low"


def quality_band_gps(x: float) -> str:
    if pd.isna(x):
        return "Unknown"
    return "Within threshold" if x <= GPS_THRESHOLD_METRES else "Outside threshold"


def quality_band_latency(x: float) -> str:
    if pd.isna(x):
        return "Unknown"
    return "Normal" if x < LATENCY_THRESHOLD_MS else "Anomalous"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DEFAULT_CSV.exists():
        raise FileNotFoundError(f"CSV not found: {DEFAULT_CSV}")
    df = pd.read_csv(DEFAULT_CSV)

    if "captured_at" in df.columns:
        df["captured_at"] = pd.to_datetime(df["captured_at"], utc=True, errors="coerce")
    else:
        df["captured_at"] = pd.NaT

    numeric_cols = [
        "latitude",
        "longitude",
        "altitude",
        "gps_accuracy_metres",
        "model_confidence",
        "barcode_scan_ms",
        "gps_fix_ms",
        "time_to_capture_ms",
        "upload_latency_ms",
        "exif_write_ms",
        "battery_level",
        "gps_speed",
        "gps_heading",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = try_to_float(df[col])

    bool_cols = ["upload_success", "building_detected", "detection_overridden", "ground_truth_is_building"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype("boolean")

    if "tracking_number" not in df.columns:
        df["tracking_number"] = ""

    df = df.sort_values("captured_at", kind="stable").reset_index(drop=True)
    df["record_no"] = np.arange(1, len(df) + 1)
    df["captured_local"] = df["captured_at"].dt.tz_convert(TZ)
    df["status"] = df.apply(status_label, axis=1)
    df["confidence_band"] = df["model_confidence"].apply(quality_band_confidence)
    df["gps_band"] = df["gps_accuracy_metres"].apply(quality_band_gps)
    df["latency_band"] = df["upload_latency_ms"].apply(quality_band_latency)
    df["edge_processing_ms"] = df[["barcode_scan_ms", "time_to_capture_ms", "exif_write_ms"]].sum(axis=1, min_count=1)
    df["end_to_end_ms"] = df[["time_to_capture_ms", "upload_latency_ms"]].sum(axis=1, min_count=1)
    return df


def nearest_node(df: pd.DataFrame, click_lat: float, click_lng: float) -> Optional[pd.Series]:
    if df.empty:
        return None
    dist = np.sqrt((df["latitude"] - click_lat) ** 2 + (df["longitude"] - click_lng) ** 2)
    idx = dist.idxmin()
    if pd.isna(dist.loc[idx]):
        return None
    return df.loc[idx]


def metrics_summary(df: pd.DataFrame) -> dict[str, float]:
    total = len(df)
    uploaded = int(df["upload_success"].fillna(False).sum())
    labeled = int(df["ground_truth_is_building"].notna().sum())
    overrides = int(df["detection_overridden"].fillna(False).sum())

    counts = build_confusion_counts(df)
    acc, prec, rec, f1 = precision_recall_f1(counts) if labeled else (0.0, 0.0, 0.0, 0.0)

    return {
        "total": total,
        "uploaded": uploaded,
        "labeled": labeled,
        "overrides": overrides,
        "upload_rate": safe_pct(uploaded, total),
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
    }


def render_small_metric(label: str, value: str) -> None:
    st.metric(label, value)


def make_popup_html(row: pd.Series) -> str:
    ts = row["captured_local"]
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(ts) else "N/A"
    return f"""
    <div style="font-family: 'Inter', 'Space Grotesk', ui-sans-serif, system-ui, sans-serif; font-size: 14px; line-height: 1.5; width: 320px; word-break: break-word; color: #212121;">
      <b>Record #{int(row['record_no'])}</b><br>
      Tracking: {row.get('tracking_number', 'N/A')}<br>
      Time: {ts_str}<br>
      Status: {row.get('status', 'N/A')}<br>
      Confidence: {fmt_pct(row.get('model_confidence'), 1)}<br>
      GPS accuracy: {fmt_num(row.get('gps_accuracy_metres'))} m<br>
      Upload latency: {fmt_ms(row.get('upload_latency_ms'))}
    </div>
    """


def make_map(df: pd.DataFrame, show_route: bool) -> folium.Map:
    df = df.dropna(subset=["latitude", "longitude"])
    if df.empty:
        return folium.Map(location=[0.0, 0.0], zoom_start=2, tiles="OpenStreetMap")

    center_lat = float(df["latitude"].mean())
    center_lon = float(df["longitude"].mean())
    bounds = [[df["latitude"].min(), df["longitude"].min()], [df["latitude"].max(), df["longitude"].max()]]

    m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles="OpenStreetMap")
    m.fit_bounds(bounds, padding=(30, 30), max_zoom=17)

    route_coords = list(zip(df["latitude"], df["longitude"]))
    if show_route and len(route_coords) >= 2:
        AntPath(
            locations=route_coords,
            color="#17171c",
            weight=4,
            opacity=0.8,
            delay=900,
            dash_array=[18, 28],
        ).add_to(m)

    for _, row in df.iterrows():
        popup = folium.Popup(make_popup_html(row), max_width=460)
        tooltip = folium.Tooltip(f"#{int(row['record_no'])} · {row.get('tracking_number', 'N/A')}")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            color="#17171c",
            weight=1,
            fill=True,
            fill_color=status_color(row["status"]),
            fill_opacity=0.92,
            tooltip=tooltip,
            popup=popup,
        ).add_to(m)

    return m


def plot_confusion_matrix(counts: dict[str, int]) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    matrix = np.array([[counts["TP"], counts["FN"]], [counts["FP"], counts["TN"]]])
    labels = np.array([["TP", "FN"], ["FP", "TN"]])

    cmap = mcolors.LinearSegmentedColormap.from_list("cohere", ["#eeece7", "#003c33"])
    fig, ax = plt.subplots(figsize=(4.8, 4.0))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    im = ax.imshow(matrix, interpolation="nearest", cmap=cmap)
    ax.set_xticks([0, 1], ["Predicted True", "Predicted False"], fontfamily="sans-serif", fontsize=11, color="#212121")
    ax.set_yticks([0, 1], ["Actual True", "Actual False"], fontfamily="sans-serif", fontsize=11, color="#212121")
    ax.set_title("Building Detection Confusion Matrix", fontfamily="sans-serif", fontsize=14, color="#17171c", pad=12)
    ax.tick_params(colors="#212121")

    for i in range(2):
        for j in range(2):
            txt_color = "#ffffff" if matrix[i, j] > matrix.max() / 2 else "#17171c"
            ax.text(j, i, f"{labels[i, j]}\n{matrix[i, j]}", ha="center", va="center", color=txt_color, fontsize=12, fontweight=500)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def plot_series(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    working = df.dropna(subset=["captured_local"]).copy()
    if working.empty:
        st.info("No timestamped records available for time-series charts.")
        return

    _plot_colors = ["#003c33", "#1863dc", "#ff7759"]
    fig, axes = plt.subplots(3, 1, figsize=(10, 8.5), sharex=True)
    fig.patch.set_facecolor("#ffffff")

    for ax in axes:
        ax.set_facecolor("#ffffff")
        ax.tick_params(colors="#212121", labelsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#d9d9dd")
        ax.spines["left"].set_color("#d9d9dd")

    axes[0].plot(working["captured_local"], working["model_confidence"], marker="o", markersize=5, color=_plot_colors[0], linewidth=1.5)
    axes[0].set_ylabel("Confidence", fontsize=11, color="#212121")

    axes[1].plot(working["captured_local"], working["gps_accuracy_metres"], marker="o", markersize=5, color=_plot_colors[1], linewidth=1.5)
    axes[1].set_ylabel("GPS accuracy (m)", fontsize=11, color="#212121")

    if "battery_level" in working.columns:
        axes[2].plot(working["captured_local"], working["battery_level"], marker="o", markersize=5, color=_plot_colors[2], linewidth=1.5)
        axes[2].set_ylabel("Battery", fontsize=11, color="#212121")
    else:
        axes[2].axis("off")

    axes[2].set_xlabel("Captured time", fontsize=11, color="#212121")
    fig.autofmt_xdate()
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def _detection_pill(label: str, value) -> str:
    v = bool_to_text(value)
    if v == "Yes":
        bg, bc, tc = "#edfce9", "#003c33", "#003c33"
    elif v == "No":
        bg, bc, tc = "#ffffff", "#d9d9dd", "#212121"
    else:
        bg, bc, tc = "#f7f6f3", "#d9d9dd", "#75758a"
    return (
        f'<span style="display:inline-block;font-size:11px;padding:2px 8px;'
        f'border:1px solid {bc};border-radius:30px;color:{tc};background:{bg};'
        f'margin-right:3px;white-space:nowrap;">{label}: <b>{v}</b></span>'
    )


def render_compact_node(node: pd.Series) -> None:
    sc = status_color(node.get("status", "Uploaded"))
    ts = node["captured_local"]
    ts_text = ts.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(ts) else "N/A"

    # ---- Header: record + status badge + tracking + time ----
    st.markdown(
        f"""<div style="margin-bottom:0.4rem;">
          <div style="display:flex;align-items:center;gap:0.45rem;margin-bottom:2px;">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:1.15rem;font-weight:600;color:#17171c;">
              #{int(node['record_no'])}
            </span>
            <span style="background:{sc};color:#fff;font-size:10px;font-weight:600;
              padding:2px 10px;border-radius:32px;text-transform:uppercase;letter-spacing:0.4px;">
              {node.get('status', 'N/A')}
            </span>
          </div>
          <div style="font-size:12px;color:#75758a;">
            {node.get('tracking_number', 'N/A')} &middot; {ts_text}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Key metrics: 3-column highlight grid ----
    st.markdown(
        f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.35rem;margin-bottom:0.4rem;">
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">Confidence</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_pct(node.get('model_confidence'), 1)}</div>
            <div style="font-size:10px;color:#93939f;">{node.get('confidence_band', '')}</div>
          </div>
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">GPS Acc.</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_num(node.get('gps_accuracy_metres'))} m</div>
            <div style="font-size:10px;color:#93939f;">{node.get('gps_band', '')}</div>
          </div>
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">Upload</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_ms(node.get('upload_latency_ms'))}</div>
            <div style="font-size:10px;color:#93939f;">{node.get('latency_band', '')}</div>
          </div>
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">Battery</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_pct(node.get('battery_level'), 0)}</div>
          </div>
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">Edge proc.</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_ms(node.get('edge_processing_ms'))}</div>
          </div>
          <div style="background:#eeece7;border-radius:8px;padding:0.45rem 0.5rem;">
            <div style="font-size:10px;color:#75758a;text-transform:uppercase;letter-spacing:0.3px;">End-to-end</div>
            <div style="font-size:1.05rem;font-weight:600;color:#17171c;line-height:1.2;">{fmt_ms(node.get('end_to_end_ms'))}</div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Detection pills ----
    st.markdown(
        f"""<div style="margin-bottom:0.35rem;line-height:2;">
          {_detection_pill("Building", node.get('building_detected'))}
          {_detection_pill("Ground truth", node.get('ground_truth_is_building'))}
          {_detection_pill("Override", node.get('detection_overridden'))}
          {_detection_pill("Upload", node.get('upload_success'))}
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Timing row ----
    st.markdown(
        f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.35rem;
              font-size:12px;margin-bottom:0.35rem;">
          <div style="border:1px solid #e5e7eb;border-radius:8px;padding:0.3rem 0.45rem;">
            <span style="color:#75758a;">GPS fix</span><br><b style="color:#212121;">{fmt_ms(node.get('gps_fix_ms'))}</b>
          </div>
          <div style="border:1px solid #e5e7eb;border-radius:8px;padding:0.3rem 0.45rem;">
            <span style="color:#75758a;">EXIF</span><br><b style="color:#212121;">{fmt_ms(node.get('exif_write_ms'))}</b>
          </div>
          <div style="border:1px solid #e5e7eb;border-radius:8px;padding:0.3rem 0.45rem;">
            <span style="color:#75758a;">Barcode</span><br><b style="color:#212121;">{fmt_ms(node.get('barcode_scan_ms'))}</b>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Coordinates ----
    st.markdown(
        f"""<div style="font-size:12px;color:#75758a;margin-bottom:0.4rem;">
          {fmt_num(node.get('latitude'), 6)}, {fmt_num(node.get('longitude'), 6)}
          &middot; Alt {fmt_num(node.get('altitude'))} m
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Image ----
    img_url = node.get("image_url")
    if pd.notna(img_url) and str(img_url).startswith("http"):
        try:
            st.image(str(img_url), use_container_width=True)
        except Exception:
            st.caption("Image load failed.")

    # ---- Expandable full values ----
    with st.expander("All fields", expanded=False):
        detail_rows = [
            ("Record #", int(node["record_no"])),
            ("Tracking number", node.get("tracking_number", "N/A")),
            ("Captured (UTC+8)", ts_text),
            ("Latitude", fmt_num(node.get("latitude"), 6)),
            ("Longitude", fmt_num(node.get("longitude"), 6)),
            ("Altitude", fmt_num(node.get("altitude"))),
            ("GPS accuracy (m)", fmt_num(node.get("gps_accuracy_metres"))),
            ("Confidence", fmt_pct(node.get("model_confidence"), 2)),
            ("Building detected", bool_to_text(node.get("building_detected"))),
            ("Ground truth building", bool_to_text(node.get("ground_truth_is_building"))),
            ("Override", bool_to_text(node.get("detection_overridden"))),
            ("Barcode scan", fmt_ms(node.get("barcode_scan_ms"))),
            ("GPS fix", fmt_ms(node.get("gps_fix_ms"))),
            ("Time to capture", fmt_ms(node.get("time_to_capture_ms"))),
            ("Upload latency", fmt_ms(node.get("upload_latency_ms"))),
            ("EXIF write", fmt_ms(node.get("exif_write_ms"))),
            ("Battery level", fmt_pct(node.get("battery_level"), 2)),
            ("GPS speed", fmt_num(node.get("gps_speed"))),
            ("GPS heading", fmt_num(node.get("gps_heading"))),
            ("Image hash", node.get("image_hash", "N/A")),
            ("Upload success", bool_to_text(node.get("upload_success"))),
            ("Image URL", node.get("image_url", "N/A")),
        ]
        st.dataframe(pd.DataFrame(detail_rows, columns=["Field", "Value"]), use_container_width=True, hide_index=True)


def filter_records(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()

    with st.sidebar:
        st.header("Filters")

        if filtered["captured_local"].notna().any():
            min_date = filtered["captured_local"].min().date()
            max_date = filtered["captured_local"].max().date()
            date_range = st.date_input(
                "Captured date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                start_ts = pd.Timestamp(start_date).tz_localize(TZ)
                end_ts = pd.Timestamp(end_date).tz_localize(TZ) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
                filtered = filtered[(filtered["captured_local"] >= start_ts) & (filtered["captured_local"] <= end_ts)]

        search_term = st.text_input("Search tracking number", value="").strip()
        if search_term:
            filtered = filtered[filtered["tracking_number"].astype(str).str.contains(search_term, case=False, na=False)]

        status_options = sorted(filtered["status"].dropna().unique().tolist())
        selected_status = st.multiselect("Status category", options=status_options, default=status_options)
        if selected_status:
            filtered = filtered[filtered["status"].isin(selected_status)]

        upload_choice = st.radio("Upload result", ["All", "Successful only", "Failed only"], horizontal=False)
        if upload_choice == "Successful only":
            filtered = filtered[filtered["upload_success"].fillna(False)]
        elif upload_choice == "Failed only":
            filtered = filtered[~filtered["upload_success"].fillna(False)]

        building_choice = st.radio("Building detection", ["All", "Detected", "Not detected"], horizontal=False)
        if building_choice == "Detected":
            filtered = filtered[filtered["building_detected"].fillna(False)]
        elif building_choice == "Not detected":
            filtered = filtered[~filtered["building_detected"].fillna(False)]

        override_only = st.checkbox("Show override records only", value=False)
        if override_only:
            filtered = filtered[filtered["detection_overridden"].fillna(False)]

        quality_choice = st.multiselect(
            "Quality bands",
            options=["High confidence", "GPS within threshold", "Latency anomalous"],
            default=[],
        )
        if "High confidence" in quality_choice:
            filtered = filtered[filtered["confidence_band"] == "High"]
        if "GPS within threshold" in quality_choice:
            filtered = filtered[filtered["gps_band"] == "Within threshold"]
        if "Latency anomalous" in quality_choice:
            filtered = filtered[filtered["latency_band"] == "Anomalous"]

        st.divider()
        st.subheader("Display")
        time_display_unit = st.radio(
            "Latency unit",
            ["Milliseconds (ms)", "Seconds (s)"],
            index=0 if st.session_state.get("time_display_unit", TIME_DISPLAY_UNIT) == "Milliseconds (ms)" else 1,
            horizontal=True,
        )
        st.session_state["time_display_unit"] = time_display_unit

        st.divider()
        show_route = st.checkbox("Show route flow", value=True)
        show_all_nodes = st.checkbox("Show all nodes on map", value=False)

    return filtered, show_route, show_all_nodes


# ------------------------------------------------------------------
# Data load
# ------------------------------------------------------------------
st.title("Delivery PoD Telemetry Dashboard")
st.caption("Field-test analysis interface for proof-of-delivery verification using building detection and EXIF metadata.")

with st.sidebar:
    st.header("Evaluation criteria")
    st.markdown(
        f"""
        <div style="font-size:13px; line-height:1.7; color:#212121;">
        Confidence &ge; <b>{CONFIDENCE_THRESHOLD:.2f}</b> &nbsp;&middot;&nbsp;
        GPS &le; <b>{GPS_THRESHOLD_METRES:.0f} m</b> &nbsp;&middot;&nbsp;
        Latency &ge; <b>{LATENCY_THRESHOLD_MS:.0f} ms</b> &rarr; anomalous<br>
        Map click tolerance: <b>{COORD_TOL_METRES:.0f} m</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

try:
    df = load_data()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

filtered_df, show_route, show_all_nodes = filter_records(df)

# ------------------------------------------------------------------
# Top-level KPIs
# ------------------------------------------------------------------
summary = metrics_summary(filtered_df if not filtered_df.empty else df)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_small_metric("Visible records", f"{len(filtered_df)}")
with c2:
    render_small_metric("Upload success", f"{summary['upload_rate']:.1f}%")
with c3:
    render_small_metric("Labeled cases", f"{summary['labeled']}")
with c4:
    render_small_metric("Building accuracy", f"{summary['accuracy']*100:.1f}%")
with c5:
    render_small_metric("Overrides", f"{summary['overrides']}")

st.markdown(
    f"""
    **Field-test summary:** {len(filtered_df)} records are currently visible after filtering.
    The fixed evaluation criteria remain constant for reproducible analysis:
    confidence ≥ {CONFIDENCE_THRESHOLD:.2f}, GPS ≤ {GPS_THRESHOLD_METRES:.0f} m, and upload latency ≥ {LATENCY_THRESHOLD_MS:.0f} ms flagged as anomalous.
    """
)

# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab_overview, tab_map, tab_quality, tab_records = st.tabs(
    ["Overview", "Map & Node Explorer", "Quality Analysis", "Raw Records"]
)

# ===========================
# Overview tab
# ===========================
with tab_overview:
    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("Operational performance")
        op1, op2, op3 = st.columns(3)
        op1.metric("Mean edge processing", fmt_ms(filtered_df["edge_processing_ms"].mean()))
        op2.metric("Mean upload latency", fmt_ms(filtered_df["upload_latency_ms"].mean()))
        op3.metric("Mean GPS accuracy", f"{fmt_num(filtered_df['gps_accuracy_metres'].mean())} m")

        perf_table = pd.DataFrame(
            {
                "Metric": [
                    "Upload success rate",
                    "Mean model confidence",
                    "Median GPS accuracy (m)",
                    "Mean edge processing (ms)",
                    "Mean end-to-end time (ms)",
                    "Override rate",
                ],
                "Value": [
                    f"{safe_pct(int(filtered_df['upload_success'].fillna(False).sum()), len(filtered_df)):.2f}%",
                    fmt_pct(filtered_df["model_confidence"].mean(), 2),
                    fmt_num(filtered_df["gps_accuracy_metres"].median()),
                    fmt_ms(filtered_df["edge_processing_ms"].mean()),
                    fmt_ms(filtered_df["end_to_end_ms"].mean()),
                    f"{safe_pct(int(filtered_df['detection_overridden'].fillna(False).sum()), len(filtered_df)):.2f}%",
                ],
            }
        )
        st.dataframe(perf_table, use_container_width=True, hide_index=True)

        st.subheader("Academic interpretation")
        st.write(
            "This dashboard is designed to present the field test as a reproducible validation study. "
            "The focus is on operational latency, geolocation quality, building-detection performance, "
            "and evidence traceability across the delivery route."
        )

    with right:
        st.subheader("Temporal trends")
        plot_series(filtered_df)

# ===========================
# Map tab
# ===========================
MAP_HEIGHT = 620

with tab_map:
    map_df = filtered_df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

    if map_df.empty:
        st.info("No records with GPS coordinates in the current filter set.")
    else:
        n_nodes = len(map_df)

        # Initialise navigation state
        if "node_idx" not in st.session_state:
            st.session_state.node_idx = 0
        if st.session_state.node_idx >= n_nodes:
            st.session_state.node_idx = 0

        map_obj = make_map(map_df, show_route=show_route)
        map_col, detail_col = st.columns([3, 2])

        with map_col:
            map_data = st_folium(
                map_obj,
                height=MAP_HEIGHT,
                returned_objects=["last_object_clicked"],
                key="field_test_map",
                use_container_width=True,
            )

            # Handle map click → update node_idx
            clicked = map_data.get("last_object_clicked") if map_data else None
            if clicked:
                click_key = (round(clicked["lat"], 8), round(clicked["lng"], 8))
                prev_key = st.session_state.get("_last_click_key")
                if click_key != prev_key:
                    st.session_state._last_click_key = click_key
                    hit = nearest_node(map_df, clicked["lat"], clicked["lng"])
                    if hit is not None:
                        match = map_df.index[map_df["record_no"] == hit["record_no"]].tolist()
                        if match:
                            st.session_state.node_idx = match[0]

        with detail_col:
            with st.container(height=MAP_HEIGHT, border=False):
                # ---- Navigation row ----
                nav_c1, nav_c2, nav_info, nav_c3, nav_c4 = st.columns([1, 1, 2, 1, 1])
                with nav_c1:
                    if st.button("⏮", key="nav_first", use_container_width=True):
                        st.session_state.node_idx = 0
                with nav_c2:
                    if st.button("◀", key="nav_prev", use_container_width=True):
                        st.session_state.node_idx = max(0, st.session_state.node_idx - 1)
                with nav_info:
                    st.markdown(
                        f"<div style='text-align:center;padding-top:0.35rem;font-size:13px;color:#75758a;'>"
                        f"<b style='color:#17171c;'>{st.session_state.node_idx + 1}</b> / "
                        f"<b style='color:#17171c;'>{n_nodes}</b></div>",
                        unsafe_allow_html=True,
                    )
                with nav_c3:
                    if st.button("▶", key="nav_next", use_container_width=True):
                        st.session_state.node_idx = min(n_nodes - 1, st.session_state.node_idx + 1)
                with nav_c4:
                    if st.button("⏭", key="nav_last", use_container_width=True):
                        st.session_state.node_idx = n_nodes - 1

                # ---- Render selected node ----
                selected = map_df.iloc[st.session_state.node_idx]
                render_compact_node(selected)

# ===========================
# Quality analysis tab
# ===========================
with tab_quality:
    a, b = st.columns([1, 1])

    with a:
        st.subheader("Building detection evaluation")
        if summary["labeled"]:
            counts = build_confusion_counts(filtered_df)
            acc, prec, rec, f1 = precision_recall_f1(counts)
            st.write(
                f"Accuracy: **{acc*100:.1f}%** · Precision: **{prec*100:.1f}%** · "
                f"Recall: **{rec*100:.1f}%** · F1-score: **{f1*100:.1f}%**"
            )
            plot_confusion_matrix(counts)
        else:
            st.info("No ground-truth labels are available for confusion-matrix analysis in the current filter set.")

    with b:
        st.subheader("GPS, confidence, and latency quality")
        q1, q2, q3 = st.columns(3)
        q1.metric("GPS within threshold", f"{safe_pct(int(filtered_df['gps_band'].eq('Within threshold').sum()), len(filtered_df)):.1f}%")
        q2.metric("Latency anomalous", f"{safe_pct(int(filtered_df['latency_band'].eq('Anomalous').sum()), len(filtered_df)):.1f}%")
        q3.metric("High confidence", f"{safe_pct(int(filtered_df['confidence_band'].eq('High').sum()), len(filtered_df)):.1f}%")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")
        clean_gps = filtered_df["gps_accuracy_metres"].dropna()
        if not clean_gps.empty:
            ax.hist(clean_gps, bins=min(10, max(3, len(clean_gps) // 2)), color="#003c33", edgecolor="#ffffff", linewidth=0.8)
            ax.axvline(GPS_THRESHOLD_METRES, linestyle="--", color="#ff7759", linewidth=1.5)
            ax.set_xlabel("GPS accuracy (m)", fontsize=11, color="#212121")
            ax.set_ylabel("Count", fontsize=11, color="#212121")
            ax.set_title("GPS Accuracy Distribution", fontsize=14, color="#17171c", pad=12)
            ax.tick_params(colors="#212121", labelsize=10)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_color("#d9d9dd")
            ax.spines["left"].set_color("#d9d9dd")
            st.pyplot(fig, clear_figure=True)
        else:
            st.info("No GPS accuracy data available.")

    st.divider()
    st.subheader("KPI table")
    kpi_df = pd.DataFrame(
        {
            "Indicator": [
                "Upload success rate",
                "Mean confidence",
                "Median confidence",
                "Mean GPS accuracy",
                "Median GPS accuracy",
                "Mean edge processing",
                "Mean end-to-end latency",
                "Override rate",
                "Labeled agreement rate",
            ],
            "Result": [
                f"{safe_pct(int(filtered_df['upload_success'].fillna(False).sum()), len(filtered_df)):.2f}%",
                fmt_pct(filtered_df["model_confidence"].mean(), 2),
                fmt_pct(filtered_df["model_confidence"].median(), 2),
                f"{fmt_num(filtered_df['gps_accuracy_metres'].mean())} m",
                f"{fmt_num(filtered_df['gps_accuracy_metres'].median())} m",
                fmt_ms(filtered_df["edge_processing_ms"].mean()),
                fmt_ms(filtered_df["end_to_end_ms"].mean()),
                f"{safe_pct(int(filtered_df['detection_overridden'].fillna(False).sum()), len(filtered_df)):.2f}%",
                f"{(precision_recall_f1(build_confusion_counts(filtered_df))[0] * 100):.2f}%" if summary["labeled"] else "N/A",
            ],
        }
    )
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)

# ===========================
# Raw records tab
# ===========================
with tab_records:
    st.subheader("Filtered field test records")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes,
        file_name="field_test_records_filtered.csv",
        mime="text/csv",
    )