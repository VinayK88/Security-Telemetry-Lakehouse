import streamlit as st

st.set_page_config(page_title="Security Telemetry Lakehouse", page_icon="◉", layout="wide", initial_sidebar_state="expanded")
METRICS=[("Schema","Canonical","normalized"),("Delivery","Idempotent","deduplicated"),("Features","Windowed","event time"),("Findings","Explainable","reason codes"),("Sources","5","illustrative"),("Events","2.4M","illustrative"),("Late events","0.8%","illustrative"),("Duplicate rate","0.3%","illustrative"),("DLQ rate","0.06%","illustrative"),("Feature windows","12","illustrative"),("Freshness","4.2 min","illustrative"),("Production data","0","synthetic demo")]
SIGNALS=[("Schema validity",.98),("Deduplication health",.97),("Event-time freshness",.91),("Feature completeness",.94),("Finding explainability",.88)]

st.markdown("""<style>
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Arial,sans-serif;color:#1d1d1f}.stApp{background:#f5f5f7}[data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e5e5ea}.block-container{max-width:1500px;padding:2rem 2.4rem 4rem}.hero{background:linear-gradient(135deg,#fff,#f7fbff);border:1px solid #e5e5ea;border-radius:32px;padding:38px 42px;margin-bottom:24px;box-shadow:0 14px 36px rgba(0,0,0,.045)}.eyebrow{color:#0071e3;font-size:.78rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase}.hero h1{font-size:3.35rem;letter-spacing:-.052em;margin:.22rem 0 .55rem}.hero p{max-width:900px;color:#6e6e73;font-size:1.12rem;line-height:1.55}.pill{display:inline-block;background:#eef6ff;color:#0066cc;border:1px solid #d8eaff;border-radius:999px;padding:.42rem .78rem;margin:.55rem .35rem 0 0;font-size:.76rem;font-weight:650}[data-testid="stMetric"]{background:#fff;border:1px solid #e5e5ea;border-radius:24px;padding:18px 20px;box-shadow:0 8px 26px rgba(0,0,0,.035);min-height:116px}[data-testid="stMetricLabel"]{color:#6e6e73;font-weight:600}[data-testid="stMetricValue"]{font-size:1.9rem;font-weight:700}.stTabs [data-baseweb="tab"]{background:#fff;border:1px solid #e5e5ea;border-radius:999px;padding:8px 16px}.card{background:#fff;border:1px solid #e5e5ea;border-radius:22px;padding:18px 20px}.note{background:#fff;border:1px solid #e5e5ea;border-radius:18px;padding:14px 18px;color:#6e6e73}</style>""",unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## Security Telemetry Lakehouse"); st.caption("Security Data Platform"); st.divider(); st.markdown("**Overview**\n\nPipeline health\n\nData quality\n\nFeature layer\n\nFindings"); st.divider(); st.caption("Synthetic / illustrative portfolio surface")
st.markdown("""<div class="hero"><div class="eyebrow">Security Data Platform</div><h1>Security Telemetry Lakehouse</h1><p>Normalize, deduplicate, watermark, aggregate, and expose trustworthy security features and explainable findings.</p><span class="pill">Canonical schema</span><span class="pill">Event time</span><span class="pill">Feature windows</span><span class="pill">Data quality</span></div>""",unsafe_allow_html=True)
for s in range(0,len(METRICS),4):
    cols=st.columns(4)
    for c,(l,v,n) in zip(cols,METRICS[s:s+4]): c.metric(l,v,n)
st.subheader("Pipeline health")
l,r=st.columns([1.15,.85],gap="large")
with l:
    for name,val in SIGNALS: st.progress(val,text=f"{name} · {val:.0%}")
with r: st.markdown('<div class="card"><b>Data quality before detection</b><br><br><span style="color:#6e6e73">The dashboard makes schema validity, late data, duplicate handling, freshness, and feature completeness visible before downstream security findings are trusted.</span></div>',unsafe_allow_html=True)
t1,t2,t3,t4=st.tabs(["Pipeline health","Data quality","Feature layer","Findings"])
with t1: st.dataframe([{"Stage":"Validate + normalize","State":"Healthy"},{"Stage":"Deduplicate + watermark","State":"Healthy"},{"Stage":"Raw store + features","State":"Healthy"},{"Stage":"Finding generation","State":"Review"}],use_container_width=True,hide_index=True)
with t2:
    for name,val in SIGNALS[:4]: st.progress(val,text=name)
with t3: st.dataframe([{"Feature":"failed_logins_1h","Window":"1h","State":"Ready"},{"Feature":"source_ip_diversity_1h","Window":"1h","State":"Ready"},{"Feature":"sensitive_actions_24h","Window":"24h","State":"Ready"}],use_container_width=True,hide_index=True)
with t4: st.info("All event counts and pipeline-volume KPIs labeled illustrative are UI defaults. No live security environment is connected.")
st.markdown('<div class="note"><b>Evaluation boundary.</b> This dashboard represents deterministic synthetic telemetry and local-demo contracts only.</div>',unsafe_allow_html=True)
