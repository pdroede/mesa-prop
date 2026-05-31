import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Prop Firm — Projecao Financeira",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Dark theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="stSidebar"]          { background: #1e293b; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1400px; }

.kpi {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 22px;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #64748b;
    margin-bottom: 8px;
}
.kpi-value { font-size: 26px; font-weight: 700; color: #f1f5f9; line-height: 1; }
.kpi-sub   { font-size: 12px; color: #94a3b8; margin-top: 6px; }

.sh { font-size: 15px; font-weight: 600; color: #f1f5f9; margin-bottom: 2px; }
.sd { font-size: 12px; color: #64748b; margin-bottom: 10px; }

.divider { border: none; border-top: 1px solid #1e293b; margin: 32px 0; }

/* dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Paleta dark ───────────────────────────────────────────────────────────────
BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
GRID     = "#1e293b"
FONT_COL = "#cbd5e1"

# ── Constants ─────────────────────────────────────────────────────────────────
MONTHS = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
AVG_TICKET   = 440
FIXED        = 1_020
STRIPE_RATE  = 0.03
PAYOUT_SCHED = [0, 0, .05, .05, .10, .10, .10, .15, .15, .15, .15, .15]

SCENARIO_DEFS = {
    "Conservador": dict(
        start=8, growth=.15,
        challenges=[8, 9, 11, 13, 15, 17, 20, 23, 26, 30, 35, 40],
        color="#94a3b8", fill="rgba(148,163,184,.12)",
    ),
    "Base": dict(
        start=15, growth=.22,
        challenges=[15, 18, 22, 27, 33, 41, 50, 61, 74, 90, 110, 134],
        color="#60a5fa", fill="rgba(96,165,250,.12)",
    ),
    "Otimista": dict(
        start=25, growth=.30,
        challenges=[25, 33, 43, 56, 73, 95, 123, 160, 208, 270, 351, 456],
        color="#34d399", fill="rgba(52,211,153,.12)",
    ),
}

def build_df(challenges):
    rows = []
    for i, ch in enumerate(challenges):
        r = ch * AVG_TICKET
        s = r * STRIPE_RATE
        p = r * PAYOUT_SCHED[i]
        c = FIXED + s + p
        rows.append(dict(
            mes=MONTHS[i], desafios=ch,
            receita=r, plataforma=FIXED,
            stripe=s, payouts=p, custos=c, lucro=r - c,
        ))
    df = pd.DataFrame(rows)
    df["acumulado"] = df["lucro"].cumsum()
    return df

SCENARIOS = {}
for name, cfg in SCENARIO_DEFS.items():
    SCENARIOS[name] = {**cfg, "df": build_df(cfg["challenges"])}

def base_layout(height=340, dollar_y=True, barmode=None, x_title=None):
    yaxis = dict(
        gridcolor=GRID, zerolinecolor=BORDER, linecolor=BORDER,
        tickcolor=BORDER, tickfont=dict(color=FONT_COL),
    )
    if dollar_y:
        yaxis.update(tickprefix="$", tickformat=",")
    d = dict(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        height=height,
        font=dict(
            family="system-ui,-apple-system,BlinkMacSystemFont,sans-serif",
            size=12, color=FONT_COL,
        ),
        margin=dict(l=8, r=8, t=10, b=8),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0f172a", bordercolor=BORDER,
            font=dict(color="#f1f5f9", size=12),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11, color=FONT_COL),
            bgcolor="rgba(15,23,42,.7)", bordercolor=BORDER, borderwidth=1,
        ),
        xaxis=dict(
            showgrid=False, linecolor=BORDER, tickcolor=BORDER,
            tickfont=dict(color=FONT_COL), title=x_title or "",
        ),
        yaxis=yaxis,
    )
    if barmode:
        d["barmode"] = barmode
    return d

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## Projecao Financeira — Prop Firm")
st.markdown(
    '<span style="color:#475569;font-size:14px;">'
    'Projecao Ano 1 &nbsp;·&nbsp; Valores em USD &nbsp;·&nbsp; '
    'Referencia de preco: FTMO / Funded Next'
    '</span>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
db = SCENARIOS["Base"]["df"]
margin_base = db["lucro"].sum() / db["receita"].sum() * 100

kpi_cols = st.columns(5)
kpis = [
    ("Receita Total (Base)",    f"${db['receita'].sum():,.0f}",  "Cenario base — Ano 1"),
    ("Lucro Liquido (Base)",    f"${db['lucro'].sum():,.0f}",    f"Margem de {margin_base:.1f}%"),
    ("Lucro no Mes 12 (Base)",  f"${db['lucro'].iloc[-1]:,.0f}", "Recorrente mensal"),
    ("Ticket Medio Ponderado",  "$440",                          "4 planos de conta"),
    ("Break-even",              "3 desafios/mes",                "Custo fixo: $1.020/mes"),
]
for col, (label, val, sub) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f'<div class="kpi">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Receita + Lucro Mensal ─────────────────────────────────────────────
r1a, r1b = st.columns(2)

with r1a:
    st.markdown('<div class="sh">Receita Mensal por Cenario</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Crescimento projetado ao longo do Ano 1</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for name, sc in SCENARIOS.items():
        fig.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["receita"], name=name,
            mode="lines+markers",
            line=dict(color=sc["color"], width=2.5),
            marker=dict(size=5, color=sc["color"]),
            hovertemplate=f"<b>{name}</b><br>Receita: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(**base_layout())
    st.plotly_chart(fig, use_container_width=True)

with r1b:
    st.markdown('<div class="sh">Lucro Liquido Mensal por Cenario</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Apos plataforma ($1.020/mes), Stripe (3%) e payouts</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig2.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["lucro"], name=name,
            mode="lines+markers",
            line=dict(color=sc["color"], width=2.5),
            marker=dict(size=5, color=sc["color"]),
            fill="tozeroy", fillcolor=sc["fill"],
            hovertemplate=f"<b>{name}</b><br>Lucro: $%{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(**base_layout())
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Acumulado + Volume ─────────────────────────────────────────────────
r2a, r2b = st.columns(2)

with r2a:
    st.markdown('<div class="sh">Lucro Acumulado por Cenario</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Evolucao do caixa gerado durante o ano</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig3.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["acumulado"], name=name,
            mode="lines",
            line=dict(color=sc["color"], width=3),
            fill="tozeroy", fillcolor=sc["fill"],
            hovertemplate=f"<b>{name}</b><br>Acumulado: $%{{y:,.0f}}<extra></extra>",
        ))
    fig3.update_layout(**base_layout())
    st.plotly_chart(fig3, use_container_width=True)

with r2b:
    st.markdown('<div class="sh">Desafios Vendidos por Mes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Volume de vendas mensal projetado por cenario</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig4.add_trace(go.Bar(
            x=MONTHS, y=sc["df"]["desafios"], name=name,
            marker_color=sc["color"],
            hovertemplate=f"<b>{name}</b><br>Desafios: %{{y}}<extra></extra>",
        ))
    l4 = base_layout(barmode="group", dollar_y=False)
    fig4.update_layout(**l4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Composicao de Custos ──────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Composicao da Receita — Cenario Base</div>', unsafe_allow_html=True)
st.markdown('<div class="sd">Breakdown mensal: lucro liquido, payouts, taxas e custo de plataforma</div>', unsafe_allow_html=True)

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=MONTHS, y=db["plataforma"], name="Plataforma + CF",
    marker_color="#334155",
    hovertemplate="Plataforma: $%{y:,.0f}<extra></extra>",
))
fig5.add_trace(go.Bar(
    x=MONTHS, y=db["stripe"], name="Stripe (3%)",
    marker_color="#3b82f6",
    hovertemplate="Stripe: $%{y:,.0f}<extra></extra>",
))
fig5.add_trace(go.Bar(
    x=MONTHS, y=db["payouts"], name="Payouts Traders",
    marker_color="#f87171",
    hovertemplate="Payouts: $%{y:,.0f}<extra></extra>",
))
fig5.add_trace(go.Bar(
    x=MONTHS, y=db["lucro"], name="Lucro Liquido",
    marker_color="#4ade80",
    hovertemplate="Lucro: $%{y:,.0f}<extra></extra>",
))
fig5.update_layout(**base_layout(height=380, barmode="stack"))
st.plotly_chart(fig5, use_container_width=True)

# ── Comparativo de Cenarios ───────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Comparativo de Cenarios — Ano 1</div>', unsafe_allow_html=True)
st.markdown('<div class="sd">Receita total, custos e lucro liquido por cenario</div>', unsafe_allow_html=True)

r3a, r3b = st.columns([3, 2])

with r3a:
    cats = ["Receita Total", "Custos Totais", "Lucro Liquido"]
    fig6 = go.Figure()
    for name, sc in SCENARIOS.items():
        df = sc["df"]
        fig6.add_trace(go.Bar(
            x=cats,
            y=[df["receita"].sum(), df["custos"].sum(), df["lucro"].sum()],
            name=name, marker_color=sc["color"],
            hovertemplate=f"<b>{name}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))
    l6 = base_layout(height=360, barmode="group")
    l6["xaxis"] = dict(
        showgrid=False, linecolor=BORDER,
        tickfont=dict(color=FONT_COL),
    )
    fig6.update_layout(**l6)
    st.plotly_chart(fig6, use_container_width=True)

with r3b:
    st.markdown('<div class="sh">Resumo Anual</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    summary = {"Metrica": [
        "Desafios iniciais/mes",
        "Crescimento mensal",
        "Total desafios vendidos",
        "Receita total",
        "Custos totais",
        "Lucro liquido",
        "Margem liquida",
        "Lucro no mes 12",
    ]}
    for name, sc in SCENARIOS.items():
        df = sc["df"]
        summary[name] = [
            str(sc["start"]),
            f"{sc['growth']*100:.0f}%",
            f"{int(df['desafios'].sum()):,}",
            f"${df['receita'].sum():,.0f}",
            f"${df['custos'].sum():,.0f}",
            f"${df['lucro'].sum():,.0f}",
            f"{df['lucro'].sum() / df['receita'].sum() * 100:.1f}%",
            f"${df['lucro'].iloc[-1]:,.0f}",
        ]
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# ── Break-even ────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
r4a, r4b = st.columns([3, 1])

with r4a:
    st.markdown('<div class="sh">Analise de Break-even</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Receita liquida vs. custo fixo mensal — quantos desafios para cobrir os custos operacionais</div>', unsafe_allow_html=True)

    xs       = list(range(0, 31))
    rev_net  = [x * AVG_TICKET * (1 - STRIPE_RATE) for x in xs]
    fixed_ln = [FIXED] * len(xs)
    be_point = FIXED / (AVG_TICKET * (1 - STRIPE_RATE))

    fig_be = go.Figure()
    fig_be.add_vrect(x0=0, x1=be_point,
                     fillcolor="rgba(239,68,68,.12)", layer="below", line_width=0)
    fig_be.add_vrect(x0=be_point, x1=30,
                     fillcolor="rgba(52,211,153,.10)", layer="below", line_width=0)
    fig_be.add_trace(go.Scatter(
        x=xs, y=rev_net, name="Receita Liquida (pos-Stripe)",
        line=dict(color="#60a5fa", width=2.5),
        hovertemplate="Desafios: %{x}<br>Receita: $%{y:,.0f}<extra></extra>",
    ))
    fig_be.add_trace(go.Scatter(
        x=xs, y=fixed_ln, name="Custo Fixo Mensal",
        line=dict(color="#f87171", width=2, dash="dash"),
        hovertemplate="Custo fixo: $1.020<extra></extra>",
    ))
    fig_be.add_vline(
        x=be_point, line_color="#fbbf24", line_dash="dot", line_width=2,
        annotation_text=f"Break-even: {be_point:.1f} desafios/mes",
        annotation_font=dict(color="#fbbf24", size=12),
        annotation_position="top right",
    )
    l_be = base_layout(height=360, x_title="Desafios vendidos no mes")
    fig_be.update_layout(**l_be)
    st.plotly_chart(fig_be, use_container_width=True)

with r4b:
    st.markdown('<div class="sh">Premissas</div>', unsafe_allow_html=True)
    st.markdown("""
**Planos e precos**

| Conta | Preco |
|-------|-------|
| $25k  | $250  |
| $50k  | $345  |
| $100k | $540  |
| $200k | $1.080|

Ticket medio ponderado: **$440**

Distribuicao: 30% / 35% / 25% / 10%

---

**Custos fixos: $1.020/mes**
- Plataforma: $1.000
- Cloudflare Pro: $20

**Stripe:** 3% por transacao

**Payouts a traders**
- M1-2: 0% da receita
- M3-4: 5% da receita
- M5-7: 10% da receita
- M8-12: 15% da receita

---
*Nao inclui marketing nem salarios*
""")

# ── Detalhamento Mensal ───────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Detalhamento Mensal por Cenario</div>', unsafe_allow_html=True)

def fmt_table(df):
    d = df[["mes","desafios","receita","plataforma","stripe",
            "payouts","custos","lucro","acumulado"]].copy()
    d.columns = ["Mes","Desafios","Receita","Plataforma+CF",
                 "Stripe","Payouts","Custos Totais","Lucro","Acumulado"]
    for col in d.columns[2:]:
        d[col] = d[col].apply(lambda v: f"${v:,.0f}")
    return d

tabs = st.tabs(list(SCENARIOS.keys()))
for tab, (name, sc) in zip(tabs, SCENARIOS.items()):
    with tab:
        st.dataframe(fmt_table(sc["df"]), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#334155;font-size:12px;">'
    'Projecao para fins de planejamento estrategico. Valores em USD. '
    'Nao inclui marketing, salarios ou despesas de abertura de empresa.'
    '</div>',
    unsafe_allow_html=True,
)
