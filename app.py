import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Prop Firm — Projecao Financeira",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
.kpi-label { font-size:11px; font-weight:600; text-transform:uppercase;
             letter-spacing:.08em; color:#64748b; margin-bottom:8px; }
.kpi-value { font-size:26px; font-weight:700; color:#f1f5f9; line-height:1; }
.kpi-sub   { font-size:12px; color:#94a3b8; margin-top:6px; }
.sh { font-size:15px; font-weight:600; color:#f1f5f9; margin-bottom:2px; }
.sd { font-size:12px; color:#64748b; margin-bottom:10px; }
.divider { border:none; border-top:1px solid #1e293b; margin:32px 0; }
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Paleta ────────────────────────────────────────────────────────────────────
BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
GRID     = "#1e293b"
FONT_COL = "#cbd5e1"

# ── Constantes ────────────────────────────────────────────────────────────────
MONTHS       = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
PRICES       = [250, 345, 540, 1080]
ACCT_KEYS    = ["25k", "50k", "100k", "200k"]
ACCT_LABELS  = ["$25k", "$50k", "$100k", "$200k"]
ACCT_COLORS  = ["#64748b", "#60a5fa", "#a78bfa", "#fbbf24"]
FIXED        = 1_020
STRIPE_RATE  = 0.03
PAYOUT_SCHED = [0, 0, .05, .05, .10, .10, .10, .15, .15, .15, .15, .15]

def avg_ticket(dist):
    return sum(d * p for d, p in zip(dist, PRICES))

# Distribuicoes (25k / 50k / 100k / 200k)
DIST_BASE  = (0.30, 0.35, 0.25, 0.10)   # ticket medio $440
DIST_100K  = (0.20, 0.25, 0.40, 0.15)   # ticket medio $514
DIST_200K  = (0.15, 0.20, 0.25, 0.40)   # ticket medio $674
DIST_VIRAL = (0.45, 0.35, 0.15, 0.05)   # ticket medio $368 — viral traz mais iniciantes

CH_BASE  = [15, 18, 22, 27, 33, 41,  50,  61,  74,  90, 110, 134]
CH_VIRAL = [15, 18, 22, 27, 33, 41, 250,  70,  85, 104, 127, 155]

SCENARIO_DEFS = {
    "Padrao": {
        "ch":    CH_BASE,
        "dist":  [DIST_BASE] * 12,
        "color": "#60a5fa",
        "fill":  "rgba(96,165,250,.12)",
        "viral": None,
    },
    "Dominio 100k": {
        "ch":    CH_BASE,
        "dist":  [DIST_100K] * 12,
        "color": "#a78bfa",
        "fill":  "rgba(167,139,250,.12)",
        "viral": None,
    },
    "Dominio 200k": {
        "ch":    CH_BASE,
        "dist":  [DIST_200K] * 12,
        "color": "#fbbf24",
        "fill":  "rgba(251,191,36,.12)",
        "viral": None,
    },
    "Video Viral (M7)": {
        "ch":    CH_VIRAL,
        "dist":  [DIST_BASE]*6 + [DIST_VIRAL] + [DIST_BASE]*5,
        "color": "#fb923c",
        "fill":  "rgba(251,146,60,.12)",
        "viral": 6,
    },
}

def build_df(ch_list, dist_list):
    rows = []
    for i, (ch, dist) in enumerate(zip(ch_list, dist_list)):
        t = avg_ticket(dist)
        r = ch * t
        s = r * STRIPE_RATE
        p = r * PAYOUT_SCHED[i]
        c = FIXED + s + p
        row = dict(mes=MONTHS[i], desafios=ch, ticket=t, receita=r,
                   plataforma=FIXED, stripe=s, payouts=p, custos=c, lucro=r - c)
        for key, price, d in zip(ACCT_KEYS, PRICES, dist):
            row[f"rev_{key}"] = ch * d * price
        rows.append(row)
    df = pd.DataFrame(rows)
    df["acumulado"] = df["lucro"].cumsum()
    return df

SCENARIOS = {
    name: {**cfg, "df": build_df(cfg["ch"], cfg["dist"])}
    for name, cfg in SCENARIO_DEFS.items()
}

def lay(height=340, dollar_y=True, barmode=None, x_title=None):
    yaxis = dict(gridcolor=GRID, zerolinecolor=BORDER, linecolor=BORDER,
                 tickcolor=BORDER, tickfont=dict(color=FONT_COL))
    if dollar_y:
        yaxis.update(tickprefix="$", tickformat=",")
    d = dict(
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, height=height,
        font=dict(family="system-ui,-apple-system,sans-serif", size=12, color=FONT_COL),
        margin=dict(l=8, r=8, t=10, b=8),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0f172a", bordercolor=BORDER,
                        font=dict(color="#f1f5f9", size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color=FONT_COL), bgcolor="rgba(15,23,42,.7)",
                    bordercolor=BORDER, borderwidth=1),
        xaxis=dict(showgrid=False, linecolor=BORDER, tickcolor=BORDER,
                   tickfont=dict(color=FONT_COL), title=x_title or ""),
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
    'Referencia: FTMO / Funded Next'
    '</span>', unsafe_allow_html=True,
)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
dp = SCENARIOS["Padrao"]["df"]
d2 = SCENARIOS["Dominio 200k"]["df"]
dv = SCENARIOS["Video Viral (M7)"]["df"]

kpi_cols = st.columns(5)
kpis = [
    ("Receita — Padrao",
     f"${dp['receita'].sum():,.0f}",
     "Distribuicao base, Ano 1"),
    ("Receita — Dominio 200k",
     f"${d2['receita'].sum():,.0f}",
     f"+{(d2['receita'].sum()/dp['receita'].sum()-1)*100:.0f}% vs padrao"),
    ("Receita — Video Viral",
     f"${dv['receita'].sum():,.0f}",
     "Spike de 250 vendas no mes 7"),
    ("Ticket: Padrao vs 200k",
     "$440 → $674",
     "Impacto do mix de contas"),
    ("Break-even",
     "2–3 desafios/mes",
     "Depende do mix de contas"),
]
for col, (label, val, sub) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f'<div class="kpi">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>', unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Receita + Lucro ────────────────────────────────────────────────────
r1a, r1b = st.columns(2)

with r1a:
    st.markdown('<div class="sh">Receita Mensal por Cenario</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Impacto do mix de contas e do video viral na receita</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for name, sc in SCENARIOS.items():
        fig.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["receita"], name=name,
            mode="lines+markers",
            line=dict(color=sc["color"], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>{name}</b><br>Receita: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.add_annotation(
        x="Jul", y=dv["receita"].iloc[6],
        text="Spike viral<br>250 vendas",
        showarrow=True, arrowhead=2,
        arrowcolor="#fb923c", arrowwidth=1.5,
        font=dict(color="#fb923c", size=10),
        ax=55, ay=-45,
        bgcolor="rgba(15,23,42,.85)", bordercolor="#fb923c", borderwidth=1,
    )
    fig.update_layout(**lay())
    st.plotly_chart(fig, use_container_width=True)

with r1b:
    st.markdown('<div class="sh">Lucro Liquido Mensal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Apos plataforma ($1.020/mes), Stripe (3%) e payouts</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig2.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["lucro"], name=name,
            mode="lines+markers",
            line=dict(color=sc["color"], width=2.5),
            marker=dict(size=5),
            fill="tozeroy", fillcolor=sc["fill"],
            hovertemplate=f"<b>{name}</b><br>Lucro: $%{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(**lay())
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Acumulado + Ticket Medio ──────────────────────────────────────────
r2a, r2b = st.columns(2)

with r2a:
    st.markdown('<div class="sh">Lucro Acumulado</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Evolucao do caixa gerado ao longo do ano</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig3.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["acumulado"], name=name,
            mode="lines",
            line=dict(color=sc["color"], width=3),
            fill="tozeroy", fillcolor=sc["fill"],
            hovertemplate=f"<b>{name}</b><br>Acumulado: $%{{y:,.0f}}<extra></extra>",
        ))
    fig3.update_layout(**lay())
    st.plotly_chart(fig3, use_container_width=True)

with r2b:
    st.markdown('<div class="sh">Ticket Medio por Mes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Mix de contas afeta diretamente o valor por desafio — viral traz mais iniciantes</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    for name, sc in SCENARIOS.items():
        fig4.add_trace(go.Scatter(
            x=MONTHS, y=sc["df"]["ticket"], name=name,
            mode="lines+markers",
            line=dict(color=sc["color"], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>{name}</b><br>Ticket: $%{{y:,.0f}}<extra></extra>",
        ))
    fig4.add_annotation(
        x="Jul", y=dv["ticket"].iloc[6],
        text="Ticket cai:<br>mais iniciantes",
        showarrow=True, arrowhead=2,
        arrowcolor="#fb923c", arrowwidth=1.5,
        font=dict(color="#fb923c", size=10),
        ax=60, ay=35,
        bgcolor="rgba(15,23,42,.85)", bordercolor="#fb923c", borderwidth=1,
    )
    fig4.update_layout(**lay())
    st.plotly_chart(fig4, use_container_width=True)

# ── Receita por Tipo de Conta ─────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Receita por Tipo de Conta</div>', unsafe_allow_html=True)
st.markdown('<div class="sd">Quanto cada plano contribui para a receita mensal — selecione o cenario</div>', unsafe_allow_html=True)

tabs_acc = st.tabs(list(SCENARIOS.keys()))
for tab, (name, sc) in zip(tabs_acc, SCENARIOS.items()):
    with tab:
        fig_acc = go.Figure()
        for key, label, color in zip(ACCT_KEYS, ACCT_LABELS, ACCT_COLORS):
            fig_acc.add_trace(go.Bar(
                x=MONTHS, y=sc["df"][f"rev_{key}"],
                name=label, marker_color=color,
                hovertemplate=f"{label}: $%{{y:,.0f}}<extra></extra>",
            ))
        if sc["viral"] is not None:
            fig_acc.add_vline(
                x="Jul", line_color="#fb923c", line_dash="dot", line_width=2,
                annotation_text="Video viral",
                annotation_font=dict(color="#fb923c", size=11),
                annotation_position="top left",
            )
        fig_acc.update_layout(**lay(height=320, barmode="stack"))
        st.plotly_chart(fig_acc, use_container_width=True)

# ── Composicao custo/lucro ────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Composicao da Receita — Cenario Padrao</div>', unsafe_allow_html=True)
st.markdown('<div class="sd">Breakdown mensal: lucro liquido, payouts, Stripe e plataforma</div>', unsafe_allow_html=True)

fig5 = go.Figure()
fig5.add_trace(go.Bar(x=MONTHS, y=dp["plataforma"], name="Plataforma + CF",
                      marker_color="#334155", hovertemplate="Plataforma: $%{y:,.0f}<extra></extra>"))
fig5.add_trace(go.Bar(x=MONTHS, y=dp["stripe"],    name="Stripe (3%)",
                      marker_color="#3b82f6", hovertemplate="Stripe: $%{y:,.0f}<extra></extra>"))
fig5.add_trace(go.Bar(x=MONTHS, y=dp["payouts"],   name="Payouts Traders",
                      marker_color="#f87171", hovertemplate="Payouts: $%{y:,.0f}<extra></extra>"))
fig5.add_trace(go.Bar(x=MONTHS, y=dp["lucro"],     name="Lucro Liquido",
                      marker_color="#4ade80", hovertemplate="Lucro: $%{y:,.0f}<extra></extra>"))
fig5.update_layout(**lay(height=380, barmode="stack"))
st.plotly_chart(fig5, use_container_width=True)

# ── Comparativo ───────────────────────────────────────────────────────────────
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
    l6 = lay(height=360, barmode="group")
    l6["xaxis"] = dict(showgrid=False, linecolor=BORDER, tickfont=dict(color=FONT_COL))
    fig6.update_layout(**l6)
    st.plotly_chart(fig6, use_container_width=True)

with r3b:
    st.markdown('<div class="sh">Resumo Anual</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    summary = {"Metrica": [
        "Ticket medio",
        "Total desafios",
        "Receita total",
        "Custos totais",
        "Lucro liquido",
        "Margem",
        "Lucro mes 12",
    ]}
    for name, sc in SCENARIOS.items():
        df = sc["df"]
        summary[name] = [
            f"${df['ticket'].mean():,.0f}",
            f"{int(df['desafios'].sum()):,}",
            f"${df['receita'].sum():,.0f}",
            f"${df['custos'].sum():,.0f}",
            f"${df['lucro'].sum():,.0f}",
            f"{df['lucro'].sum()/df['receita'].sum()*100:.1f}%",
            f"${df['lucro'].iloc[-1]:,.0f}",
        ]
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# ── Break-even ────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
r4a, r4b = st.columns([3, 1])

with r4a:
    st.markdown('<div class="sh">Break-even por Mix de Contas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sd">Quanto mais caro o plano vendido, menos desafios precisam para cobrir os custos fixos</div>', unsafe_allow_html=True)

    xs       = list(range(0, 21))
    fixed_ln = [FIXED] * len(xs)
    be_lines = [
        ("Padrao ($440)",      440, "#60a5fa"),
        ("Dominio 100k ($514)", 514, "#a78bfa"),
        ("Dominio 200k ($674)", 674, "#fbbf24"),
    ]

    fig_be = go.Figure()
    fig_be.add_vrect(x0=0, x1=3, fillcolor="rgba(239,68,68,.10)", layer="below", line_width=0)
    fig_be.add_vrect(x0=3, x1=20, fillcolor="rgba(52,211,153,.06)", layer="below", line_width=0)

    for be_label, ticket, be_color in be_lines:
        rev_net = [x * ticket * (1 - STRIPE_RATE) for x in xs]
        be_x    = FIXED / (ticket * (1 - STRIPE_RATE))
        fig_be.add_trace(go.Scatter(
            x=xs, y=rev_net, name=be_label,
            line=dict(color=be_color, width=2),
            hovertemplate=f"{be_label}<br>Desafios: %{{x}}<br>Receita: $%{{y:,.0f}}<extra></extra>",
        ))
        fig_be.add_annotation(
            x=be_x, y=FIXED,
            text=f"{be_x:.1f}", showarrow=False,
            font=dict(color=be_color, size=10), yshift=12,
        )

    fig_be.add_trace(go.Scatter(
        x=xs, y=fixed_ln, name="Custo Fixo ($1.020)",
        line=dict(color="#f87171", width=2, dash="dash"),
        hovertemplate="Custo fixo: $1.020<extra></extra>",
    ))
    fig_be.update_layout(**lay(height=380, x_title="Desafios vendidos no mes"))
    st.plotly_chart(fig_be, use_container_width=True)

with r4b:
    st.markdown('<div class="sh">Mix por Cenario</div>', unsafe_allow_html=True)
    st.markdown("""
| Plano | Padrao | 100k | 200k |
|-------|:------:|:----:|:----:|
| $25k  | 30%   | 20%  | 15%  |
| $50k  | 35%   | 25%  | 20%  |
| $100k | 25%   | 40%  | 25%  |
| $200k | 10%   | 15%  | 40%  |
| **Ticket** | **$440** | **$514** | **$674** |
| **Break-even** | **~2.4** | **~2.0** | **~1.6** |

---

**Video Viral (M7)**
- 250 desafios no mes
- Mix: 45% contas $25k
- Ticket cai para $368
- Baseline pos-viral: +70%

---

**Custos fixos:** $1.020/mes
**Stripe:** 3% por transacao
**Payouts:** ate 15% da receita
""")

# ── Detalhamento Mensal ───────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="sh">Detalhamento Mensal por Cenario</div>', unsafe_allow_html=True)

def fmt_table(df):
    d = df[["mes","desafios","ticket","receita","plataforma",
            "stripe","payouts","custos","lucro","acumulado"]].copy()
    d.columns = ["Mes","Desafios","Ticket Medio","Receita","Plataforma+CF",
                 "Stripe","Payouts","Custos Totais","Lucro","Acumulado"]
    for col in ["Ticket Medio","Receita","Plataforma+CF","Stripe",
                "Payouts","Custos Totais","Lucro","Acumulado"]:
        d[col] = d[col].apply(lambda v: f"${v:,.0f}")
    return d

tabs_det = st.tabs(list(SCENARIOS.keys()))
for tab, (name, sc) in zip(tabs_det, SCENARIOS.items()):
    with tab:
        st.dataframe(fmt_table(sc["df"]), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#334155;font-size:12px;">'
    'Projecao para fins de planejamento estrategico. Valores em USD. '
    'Nao inclui marketing, salarios ou despesas de abertura de empresa.'
    '</div>', unsafe_allow_html=True,
)
