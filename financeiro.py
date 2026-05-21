import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StaVest · Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #060d1f;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #060d1f 100%);
    border-right: 1px solid #1a2744;
}

[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

/* Main area */
[data-testid="stAppViewContainer"] > .main {
    background: #060d1f;
    padding: 0 1rem;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1b38 0%, #0a1628 100%);
    border: 1px solid #1a2744;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}

div[data-testid="metric-container"] label {
    color: #64748b !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.5rem !important;
    color: #f1f5f9 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

/* Hide default streamlit header */
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

/* Section headers */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-bottom: 0.5rem;
    padding-left: 2px;
}

/* Card wrapper */
.card {
    background: linear-gradient(135deg, #0d1b38 0%, #0a1628 100%);
    border: 1px solid #1a2744;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.5);
    margin-bottom: 1rem;
}

/* Badge pill */
.badge {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
}

/* Table styling */
.dataframe {
    background: transparent !important;
    border: none !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a1628; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA GENERATION  (500 rows)
# ─────────────────────────────────────────────
@st.cache_data
def gerar_dados():
    np.random.seed(42)
    random.seed(42)

    acoes = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3",
             "MGLU3", "WEGE3", "RENT3", "LREN3", "BBAS3"]
    setores = {
        "PETR4": "Energia", "VALE3": "Mineração", "ITUB4": "Financeiro",
        "BBDC4": "Financeiro", "ABEV3": "Consumo", "MGLU3": "Varejo",
        "WEGE3": "Indústria", "RENT3": "Serviços", "LREN3": "Varejo",
        "BBAS3": "Financeiro",
    }

    # --- Série temporal de preços (500 dias) ---
    datas = pd.date_range(end=datetime.today(), periods=500, freq="B")
    preco_base = {a: random.uniform(10, 90) for a in acoes}
    registros = []

    for acao in acoes:
        preco = preco_base[acao]
        for data in datas:
            retorno = np.random.normal(0.0003, 0.018)
            preco = max(preco * (1 + retorno), 1)
            volume = int(np.random.lognormal(15, 0.5))
            registros.append({
                "Data": data, "Acao": acao, "Setor": setores[acao],
                "Preco": round(preco, 2), "Volume": volume,
                "Retorno_Diario": round(retorno * 100, 4),
            })

    df = pd.DataFrame(registros)

    # --- Portfólio do usuário ---
    portfolio = []
    for acao in acoes:
        preco_atual = df[df["Acao"] == acao]["Preco"].iloc[-1]
        qtd = random.randint(50, 500)
        preco_medio = round(preco_atual * random.uniform(0.75, 1.20), 2)
        portfolio.append({
            "Acao": acao, "Setor": setores[acao],
            "Qtd": qtd, "Preco_Medio": preco_medio,
            "Preco_Atual": round(preco_atual, 2),
            "Valor_Total": round(qtd * preco_atual, 2),
            "Lucro_Pct": round(((preco_atual / preco_medio) - 1) * 100, 2),
        })

    df_port = pd.DataFrame(portfolio)
    return df, df_port

df, df_port = gerar_dados()
acoes_lista = df["Acao"].unique().tolist()
ultima_data = df["Data"].max()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem'>
        <div style='font-family:"Space Mono",monospace; font-size:1.4rem;
                    color:#3b82f6; letter-spacing:0.05em; font-weight:700'>
            Sta<span style='color:#60a5fa'>Vest</span>
        </div>
        <div style='font-size:0.72rem; color:#475569; margin-top:2px'>
            plataforma de análise
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Bem-vindo, Naya** 👋")
    st.caption("Seu painel de investimentos")
    st.divider()

    st.markdown('<p class="section-title">Menu Principal</p>', unsafe_allow_html=True)
    pagina = st.radio("", ["📊 Dashboard", "💼 Portfólio", "📈 Análise", "🏪 Mercado"],
                      label_visibility="collapsed")
    st.divider()

    st.markdown('<p class="section-title">Filtros Rápidos</p>', unsafe_allow_html=True)
    acao_selecionada = st.selectbox("Ação", acoes_lista)
    janela = st.select_slider("Período (dias)", [30, 60, 90, 180, 365, 500], value=180)
    st.divider()
    st.caption("© 2024 StaVest  ·  v2.4.1")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def cor_delta(v):
    return "normal" if v >= 0 else "inverse"


# ─────────────────────────────────────────────
# TOPO
# ─────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; justify-content:space-between;
            padding:1.2rem 0 0.8rem'>
    <div>
        <h2 style='margin:0; font-family:"Space Mono",monospace;
                   font-size:1.6rem; color:#f1f5f9'>Dashboard</h2>
        <p style='margin:0; color:#475569; font-size:0.82rem'>
            Atualizado em """ + ultima_data.strftime("%d/%m/%Y") + """
        </p>
    </div>
    <span class='badge'>● AO VIVO</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
total_carteira  = df_port["Valor_Total"].sum()
total_investido = (df_port["Preco_Medio"] * df_port["Qtd"]).sum()
lucro_total     = total_carteira - total_investido
lucro_pct       = (lucro_total / total_investido) * 100

preco_hoje = df[df["Data"] == ultima_data]["Preco"].mean()
preco_ant  = df[df["Data"] == df[df["Data"] < ultima_data]["Data"].max()]["Preco"].mean()
var_dia     = ((preco_hoje / preco_ant) - 1) * 100

melhor_acao = df_port.loc[df_port["Lucro_Pct"].idxmax()]
pior_acao   = df_port.loc[df_port["Lucro_Pct"].idxmin()]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Patrimônio Total", fmt_brl(total_carteira),
              f"{lucro_pct:+.2f}% total")
with c2:
    st.metric("📈 Lucro / Prejuízo", fmt_brl(lucro_total),
              f"{lucro_pct:+.2f}%", delta_color=cor_delta(lucro_total))
with c3:
    st.metric("🏆 Melhor Ação", melhor_acao["Acao"],
              f"{melhor_acao['Lucro_Pct']:+.2f}%")
with c4:
    st.metric("📉 Variação do Dia", f"{var_dia:+.2f}%",
              delta_color=cor_delta(var_dia))

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LINHA 2 ─ Gráfico de Performance + Donut
# ─────────────────────────────────────────────
col_graf, col_donut = st.columns([3, 1.5])

with col_graf:
    st.markdown('<p class="section-title">Performance do Portfólio</p>',
                unsafe_allow_html=True)

    # Valor diário do portfólio simulado
    datas_unicas = sorted(df["Data"].unique())[-janela:]
    val_diario = []
    for data in datas_unicas:
        snap = df[df["Data"] == data].set_index("Acao")["Preco"]
        val = sum(
            row["Qtd"] * snap.get(row["Acao"], row["Preco_Atual"])
            for _, row in df_port.iterrows()
        )
        val_diario.append({"Data": data, "Valor": val})
    df_val = pd.DataFrame(val_diario)

    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(
        x=df_val["Data"], y=df_val["Valor"],
        mode="lines",
        line=dict(color="#3b82f6", width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>R$ %{y:,.2f}<extra></extra>",
    ))
    fig_perf.update_layout(
        height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, color="#475569", tickformat="%b %Y",
                   showline=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1a2744", color="#475569",
                   tickformat=",.0f", showline=False, zeroline=False),
        hovermode="x unified",
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

with col_donut:
    st.markdown('<p class="section-title">Alocação por Setor</p>',
                unsafe_allow_html=True)
    setor_val = df_port.groupby("Setor")["Valor_Total"].sum().reset_index()
    cores_setor = ["#3b82f6","#06b6d4","#8b5cf6","#f59e0b","#10b981",
                   "#ef4444","#f97316","#84cc16","#ec4899","#a78bfa"]
    fig_donut = go.Figure(go.Pie(
        labels=setor_val["Setor"], values=setor_val["Valor_Total"],
        hole=0.62,
        marker=dict(colors=cores_setor[:len(setor_val)],
                    line=dict(color="#060d1f", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    fig_donut.update_layout(
        height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=10, color="#94a3b8"),
                    bgcolor="rgba(0,0,0,0)", x=1.0),
        font=dict(family="DM Sans"),
        annotations=[dict(text=f"<b>{len(setor_val)}</b><br>setores",
                          x=0.5, y=0.5, font=dict(size=13, color="#60a5fa"),
                          showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
# LINHA 3 ─ Tabela Portfólio + Análise Ação
# ─────────────────────────────────────────────
col_tab, col_acao = st.columns([2, 1.8])

with col_tab:
    st.markdown('<p class="section-title">Visão do Portfólio</p>',
                unsafe_allow_html=True)

    df_show = df_port[[
        "Acao","Setor","Qtd","Preco_Medio","Preco_Atual","Valor_Total","Lucro_Pct"
    ]].copy()
    df_show.columns = ["Ação","Setor","Qtd","P. Médio (R$)","P. Atual (R$)","Total (R$)","Ret. (%)"]
    df_show["P. Médio (R$)"] = df_show["P. Médio (R$)"].map("{:.2f}".format)
    df_show["P. Atual (R$)"] = df_show["P. Atual (R$)"].map("{:.2f}".format)
    df_show["Total (R$)"]    = df_show["Total (R$)"].map("{:,.2f}".format)

    def highlight_ret(val):
        c = "#10b981" if val >= 0 else "#ef4444"
        return f"color: {c}; font-weight: 600"

    styled = (
        df_show.style
        .map(highlight_ret, subset=["Ret. (%)"])
        .set_properties(**{
            "background-color": "transparent",
            "font-size": "0.82rem",
            "font-family": "DM Sans",
            "border": "none",
        })
        .set_table_styles([
            {"selector": "th", "props": [
                ("background-color", "#0d1b38"),
                ("color", "#60a5fa"),
                ("font-size", "0.7rem"),
                ("letter-spacing", "0.08em"),
                ("text-transform", "uppercase"),
                ("border-bottom", "1px solid #1a2744"),
                ("padding", "8px 6px"),
            ]},
            {"selector": "td", "props": [
                ("border-bottom", "1px solid #0f1f3d"),
                ("padding", "7px 6px"),
                ("color", "#cbd5e1"),
            ]},
            {"selector": "tr:hover td", "props": [("background-color", "#0d1b38")]},
        ])
        .format({"Ret. (%)": "{:+.2f}%"})
    )
    st.dataframe(styled, use_container_width=True, height=370)

with col_acao:
    st.markdown(f'<p class="section-title">Análise · {acao_selecionada}</p>',
                unsafe_allow_html=True)

    df_acao = df[(df["Acao"] == acao_selecionada)].tail(janela)

    # Candlestick sintético (OHLC)
    df_ohlc = df_acao.resample("W-FRI", on="Data").agg(
        Open=("Preco", "first"), High=("Preco", "max"),
        Low=("Preco", "min"),   Close=("Preco", "last"),
        Volume=("Volume", "sum"),
    ).dropna().reset_index()

    fig_c = go.Figure(data=go.Candlestick(
        x=df_ohlc["Data"],
        open=df_ohlc["Open"], high=df_ohlc["High"],
        low=df_ohlc["Low"],   close=df_ohlc["Close"],
        increasing_line_color="#10b981", decreasing_line_color="#ef4444",
        increasing_fillcolor="#10b981", decreasing_fillcolor="#ef4444",
    ))
    fig_c.update_layout(
        height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(showgrid=False, color="#475569", rangeslider_visible=False,
                   showline=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1a2744", color="#475569",
                   showline=False, zeroline=False),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})

    # Mini KPIs da ação
    info = df_port[df_port["Acao"] == acao_selecionada].iloc[0]
    ka, kb = st.columns(2)
    ka.metric("Preço Atual", fmt_brl(info["Preco_Atual"]))
    kb.metric("Retorno",    f"{info['Lucro_Pct']:+.2f}%",
              delta_color=cor_delta(info["Lucro_Pct"]))
    kc, kd = st.columns(2)
    kc.metric("Qtd. Cotas", f"{info['Qtd']:,}")
    kd.metric("Valor Posição", fmt_brl(info["Valor_Total"]))

# ─────────────────────────────────────────────
# LINHA 4 ─ Volume + Ranking + Retornos dist
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_vol, col_rank, col_hist = st.columns(3)

with col_vol:
    st.markdown('<p class="section-title">Volume Médio por Ação</p>',
                unsafe_allow_html=True)
    vol_med = df.groupby("Acao")["Volume"].mean().sort_values(ascending=True).reset_index()
    fig_bar = go.Figure(go.Bar(
        x=vol_med["Volume"], y=vol_med["Acao"],
        orientation="h",
        marker=dict(
            color=vol_med["Volume"],
            colorscale=[[0, "#1e3a5f"], [1, "#3b82f6"]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Volume médio: %{x:,.0f}<extra></extra>",
    ))
    fig_bar.update_layout(
        height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(showgrid=True, gridcolor="#1a2744", color="#475569",
                   showline=False, zeroline=False),
        yaxis=dict(showgrid=False, color="#94a3b8", showline=False),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with col_rank:
    st.markdown('<p class="section-title">Ranking de Retorno</p>',
                unsafe_allow_html=True)
    rank = df_port[["Acao","Lucro_Pct"]].sort_values("Lucro_Pct", ascending=False)
    cores_rank = ["#10b981" if v >= 0 else "#ef4444" for v in rank["Lucro_Pct"]]
    fig_rank = go.Figure(go.Bar(
        x=rank["Lucro_Pct"], y=rank["Acao"],
        orientation="h",
        marker=dict(color=cores_rank, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x:+.2f}%<extra></extra>",
        text=[f"{v:+.2f}%" for v in rank["Lucro_Pct"]],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8"),
    ))
    fig_rank.update_layout(
        height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=40, t=5, b=0),
        xaxis=dict(showgrid=True, gridcolor="#1a2744", color="#475569",
                   showline=False, zeroline=False),
        yaxis=dict(showgrid=False, color="#94a3b8", showline=False),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_rank, use_container_width=True, config={"displayModeBar": False})

with col_hist:
    st.markdown(f'<p class="section-title">Distribuição de Retornos · {acao_selecionada}</p>',
                unsafe_allow_html=True)
    retornos = df[df["Acao"] == acao_selecionada]["Retorno_Diario"]
    fig_hist = go.Figure(go.Histogram(
        x=retornos, nbinsx=40,
        marker=dict(color="#3b82f6", line=dict(color="#060d1f", width=0.5)),
        opacity=0.85,
        hovertemplate="Retorno: %{x:.2f}%<br>Freq: %{y}<extra></extra>",
    ))
    fig_hist.add_vline(x=retornos.mean(), line_dash="dash",
                       line_color="#f59e0b", annotation_text="Média",
                       annotation_font=dict(size=10, color="#f59e0b"))
    fig_hist.update_layout(
        height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(showgrid=False, color="#475569", title=dict(text="Retorno Diário (%)",
                   font=dict(size=10, color="#475569")), showline=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1a2744", color="#475569",
                   showline=False, zeroline=False),
        font=dict(family="DM Sans"),
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
# LINHA 5 ─ Correlação + Heatmap mensal
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_corr, col_heat = st.columns([1.5, 1])

with col_corr:
    st.markdown('<p class="section-title">Matriz de Correlação</p>',
                unsafe_allow_html=True)
    pivot = df.pivot_table(index="Data", columns="Acao", values="Retorno_Diario")
    corr  = pivot.corr()
    fig_corr = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0,"#ef4444"],[0.5,"#1e3a5f"],[1,"#3b82f6"]],
        zmin=-1, zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=9, color="white"),
        hovertemplate="%{x} × %{y}<br>ρ = %{z:.2f}<extra></extra>",
    ))
    fig_corr.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        yaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        font=dict(family="DM Sans"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

with col_heat:
    st.markdown(f'<p class="section-title">Retorno Mensal · {acao_selecionada}</p>',
                unsafe_allow_html=True)
    df_sel = df[df["Acao"] == acao_selecionada].copy()
    df_sel["Ano"] = df_sel["Data"].dt.year
    df_sel["Mes"] = df_sel["Data"].dt.month
    mensal = df_sel.groupby(["Ano","Mes"])["Retorno_Diario"].sum().reset_index()
    pivot_m = mensal.pivot(index="Ano", columns="Mes", values="Retorno_Diario").fillna(0)
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    pivot_m.columns = [meses[m-1] for m in pivot_m.columns]

    fig_heat = go.Figure(go.Heatmap(
        z=pivot_m.values, x=pivot_m.columns, y=pivot_m.index.astype(str),
        colorscale=[[0,"#ef4444"],[0.5,"#1e3a5f"],[1,"#10b981"]],
        hovertemplate="<b>%{y} %{x}</b><br>%{z:.2f}%<extra></extra>",
        text=pivot_m.values.round(1),
        texttemplate="%{text}%",
        textfont=dict(size=8, color="white"),
    ))
    fig_heat.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=0),
        xaxis=dict(color="#94a3b8", tickfont=dict(size=9)),
        yaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        font=dict(family="DM Sans"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#1e3a5f; font-size:0.72rem;
            font-family:"Space Mono",monospace; padding: 0.5rem 0 1rem'>
    StaVest Dashboard · dados simulados para fins educacionais · 2024
</div>
""", unsafe_allow_html=True)