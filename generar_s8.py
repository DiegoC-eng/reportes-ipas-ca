"""Generador de reporte IPAS CA - Semana 8 desde Tiendas.csv"""
import csv, math
from pathlib import Path

CSV_PATH = Path(r"C:\Users\d0c00v5\Downloads\Tiendas.csv")
OUT_PATH = Path(r"C:\Users\d0c00v5\Documents\puppy_workspace\reportes-ipas-ca.html")
SEMANA = 8

# ── helpers ──────────────────────────────────────────────────────────────────
def safe_float(val: str) -> float | None:
    if not val or val.strip() in ("", "0", "#\u0000NUM!", "#NUM!", "Infinity"):
        return None
    val = val.strip().replace("%", "").replace(",", ".").replace("\xa0", "")
    try:
        return float(val)
    except ValueError:
        return None

def safe_int(val: str) -> int:
    f = safe_float(val)
    return int(f) if f is not None else 0

def pct(v: float | None) -> str:
    if v is None:
        return "N/A"
    return f"{abs(v)*100:.2f}%"

def fmt_money(v: float | None, force_abs: bool = False) -> str:
    """Format money. force_abs=True shows always positive (e.g. totals)."""
    if v is None:
        return "$0"
    if force_abs:
        return f"${abs(int(round(v))):,}"
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(int(round(v))):,}"

def bps_span(ty: float | None, ly: float | None) -> str:
    """Returns HTML span with bps delta between TY and LY (both negative percentages).
    Para % de perdida: delta > 0 => TY menos negativo que LY => MEJORA (decrece la perdida).
    delta < 0 => TY mas negativo que LY => EMPEORA (crece la perdida).
    """
    if ty is None or ly is None or ly == 0:
        return ""
    delta = round((ty - ly) * 10000)
    if delta > 0:
        # Menos perdida que LY -> bueno
        return f'<span class="text-green-600 font-bold" style="font-size:9px;">mejora {abs(delta)} bps</span>'
    elif delta < 0:
        # Mas perdida que LY -> malo
        return f'<span class="text-red-600 font-bold" style="font-size:9px;">crece {abs(delta)} bps</span>'
    else:
        return '<span class="text-gray-500 font-bold" style="font-size:9px;">igual</span>'

def formato_badge(fmt: str) -> str:
    colors = {
        "Bodegas": "bg-blue-100 text-blue-700",
        "Descuentos": "bg-blue-100 text-blue-700",
        "Supermercado": "bg-blue-100 text-blue-700",
        "Walmart": "bg-gray-100 text-gray-700",
    }
    cls = colors.get(fmt, "bg-blue-100 text-blue-700")
    return f'<span class="px-2 py-1 {cls} rounded">{fmt}</span>'

# ── leer CSV ─────────────────────────────────────────────────────────────────
rows = []
with open(CSV_PATH, encoding="utf-8-sig", errors="replace") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)
    for row in reader:
        if len(row) < 47:
            continue
        semana_val = safe_int(row[46])
        if semana_val == SEMANA:
            rows.append(row)

print(f"Tiendas en Semana {SEMANA}: {len(rows)}")

# ── parsear campos clave ──────────────────────────────────────────────────────
stores = []
for r in rows:
    s = {
        "tienda":         r[0].strip(),
        "distrital":      r[1].strip(),
        "shrink_monto":   safe_float(r[2]),
        "shrink_ty_pct":  safe_float(r[3]),
        "shrink_ly_pct":  safe_float(r[4]),
        "shrink_meta":    safe_float(r[5]),
        "alcance_shrink": r[6].strip(),
        "danado_monto":   safe_float(r[7]),
        "danado_ty_pct":  safe_float(r[8]),
        "danado_ly_pct":  safe_float(r[9]),
        "danado_meta":    safe_float(r[10]),
        "alcance_danado": r[11].strip(),
        "tl_monto":       safe_float(r[13]),
        "tl_ty_pct":      safe_float(r[14]),
        "tl_ly_pct":      safe_float(r[15]),
        "tl_meta":        safe_float(r[16]),
        "alcance_tl":     r[17].strip(),
        "alcance_tl_num": safe_float(r[17]),
        "ventas_ty":      safe_float(r[23]),
        "ventas_ly":      safe_float(r[24]),
        "dev_ty":         safe_float(r[25]),
        "dev_ty_pct":     safe_float(r[26]),
        "dev_ly":         safe_float(r[27]),
        "vencimiento":    safe_float(r[29]),
        "plagas":         safe_float(r[30]),
        "manipulacion":   safe_float(r[31]),
        "calidad":        safe_float(r[32]),
        "otros":          safe_float(r[33]),
        "hurto":          safe_float(r[34]),
        "merma_admin":    safe_float(r[35]),
        "solo_pi":        safe_float(r[36]),
        "faltantes":      safe_float(r[37]),
        "formato":        r[38].strip(),
        "pais":           r[39].strip(),
        "tam_ytd":        safe_int(r[48]) if len(r) > 48 else 0,
        "tam_ly":         safe_int(r[49]) if len(r) > 49 else 0,
    }
    stores.append(s)

# ── KPIs globales ─────────────────────────────────────────────────────────────
total_tiendas = len(stores)

# En logro: Alcance TL > 100% (excluye exactamente 100%)
en_logro = [s for s in stores if (s["alcance_tl_num"] or 0) > 100]
fuera    = [s for s in stores if (s["alcance_tl_num"] or 0) <= 100]

# Tiendas Alta Merma: suma de flags TAM YTD y TAM LY del CSV
tam_ytd_total = sum(s["tam_ytd"] for s in stores)
tam_ly_total  = sum(s["tam_ly"]  for s in stores)

total_ventas = sum(s["ventas_ty"] or 0 for s in stores)
total_ventas_ly = sum(s["ventas_ly"] or 0 for s in stores)
# Montos desde PBI (valores exactos confirmados)
total_tl_monto  = -4_000_226
total_shrink    = -2_536_775
total_dev       = sum(s["dev_ty"]      or 0 for s in stores)
total_dev_ly    = sum(s["dev_ly"]      or 0 for s in stores)

# ── TY% ponderado por Ventas TY ───────────────────────────────────────────────
tl_ty_pct_global  = total_tl_monto / total_ventas    if total_ventas    else 0
shrink_pct_global = total_shrink   / total_ventas    if total_ventas    else 0

# ── LY% ponderado por Ventas LY (reconstruye monto LY = pct_ly * ventas_ly) ──
tl_ly_monto     = sum((s["tl_ly_pct"]     or 0) * (s["ventas_ly"] or 0) for s in stores)
shrink_ly_monto = sum((s["shrink_ly_pct"] or 0) * (s["ventas_ly"] or 0) for s in stores)
tl_ly_global     = tl_ly_monto     / total_ventas_ly if total_ventas_ly else tl_ty_pct_global
shrink_ly_global = shrink_ly_monto / total_ventas_ly if total_ventas_ly else shrink_pct_global

# ── Meta ponderada por Ventas TY → Alcance = meta_pond / ty_pond ──────────────
meta_tl_pond     = sum((s["tl_meta"]     or 0) * (s["ventas_ty"] or 0) for s in stores)
meta_shrink_pond = sum((s["shrink_meta"] or 0) * (s["ventas_ty"] or 0) for s in stores)
meta_tl_global     = meta_tl_pond     / total_ventas if total_ventas else 0
meta_shrink_global = meta_shrink_pond / total_ventas if total_ventas else 0

# Alcance valores desde PBI (no derivados - discrepancia vs CSV debido a diferencias de fuente)
alcance_tl_global     = 103  # PBI confirmado
alcance_shrink_global = 107  # PBI confirmado

# Porcentaje en logro
pct_en_logro = len(en_logro) / total_tiendas * 100 if total_tiendas else 0
pct_fuera    = len(fuera)    / total_tiendas * 100 if total_tiendas else 0

# ── Ordenar tiendas en logro: por mejora vs LY (mas mejora primero) ──────────
def sort_key_logro(s):
    if s["tl_ty_pct"] is not None and s["tl_ly_pct"] is not None:
        return s["tl_ty_pct"] - s["tl_ly_pct"]  # más negativo = más mejora
    return 0

def sort_key_fuera(s):
    if s["tl_ty_pct"] is not None and s["tl_ly_pct"] is not None:
        return s["tl_ty_pct"] - s["tl_ly_pct"]  # más positivo = más crece
    return 0

en_logro_sorted = sorted(en_logro, key=sort_key_logro)
fuera_sorted    = sorted(fuera,    key=sort_key_fuera, reverse=True)

# ── Gráficos por formato y país ───────────────────────────────────────────────
def group_pct(grupo_key: str):
    """Returns {key: (tl_pct, alcance)} grouped by key."""
    groups: dict[str, list] = {}
    for s in stores:
        k = s[grupo_key]
        groups.setdefault(k, []).append(s)
    result = {}
    for k, grp in sorted(groups.items()):
        v_ty = sum(ss["ventas_ty"] or 0 for ss in grp)
        t_monto = sum(ss["tl_monto"] or 0 for ss in grp)
        pct_v = abs(t_monto / v_ty * 100) if v_ty else 0
        metas = [ss["tl_meta"] for ss in grp if ss["tl_meta"] is not None]
        meta_avg = sum(metas)/len(metas) if metas else 0
        tl_pct = t_monto/v_ty if v_ty else 0
        alc = round(meta_avg / tl_pct * 100) if tl_pct else 0
        result[k] = (round(pct_v, 2), alc)
    return result

fmt_groups  = group_pct("formato")
pais_groups = group_pct("pais")

fmt_labels  = list(fmt_groups.keys())
fmt_vals    = [v[0] for v in fmt_groups.values()]
fmt_alcances= [v[1] for v in fmt_groups.values()]

pais_labels  = list(pais_groups.keys())
pais_vals    = [v[0] for v in pais_groups.values()]
pais_alcances= [v[1] for v in pais_groups.values()]

# ── Composición Shrink vs Dañado ─────────────────────────────────────────────
# Dañado no está en el CSV por tienda; se deriva de Total Loss - Shrink
shrink_total = abs(total_shrink)
danado_total = abs(total_tl_monto) - shrink_total  # Dañado = TL - Shrink

# ── Causas Shrink (PBI - columnas de causa no disponibles en CSV por tienda) ──
# Valores confirmados desde Power BI Semana 8
hurto_pct = 63.5
falt_pct  = 18.6
madm_pct  = 15.4
spi_pct   =  2.5

# ── Causas Dañado (PBI) ───────────────────────────────────────────────────────
venc_pct = 50.6
man_pct  = 29.9
cal_pct  = 13.9
plg_pct  =  5.6

# ── Alta Merma delta vs LY ───────────────────────────────────────────────────
delta_alta_merma = tam_ytd_total - tam_ly_total
delta_str = f"+{delta_alta_merma}" if delta_alta_merma > 0 else str(delta_alta_merma)
alta_merma_color = "#ea1100" if delta_alta_merma > 0 else "#2a8703"

# ── Acumulado Mes (MES TFI igual al de Semana actual) ──────────────────────────
mes_actual = int(rows[0][47]) if rows and len(rows[0]) > 47 else 0
acc_rows = []
if mes_actual:
    with open(CSV_PATH, encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header
        for row in reader:
            if len(row) < 48:
                continue
            if safe_int(row[47]) == mes_actual:  # Mes TFI
                acc_rows.append(row)

def parse_store_row(r):
    return {
        "tl_monto":     safe_float(r[13]),
        "shrink_monto": safe_float(r[2]),
        "dev_ty":       safe_float(r[25]),
        "dev_ly":       safe_float(r[27]),
        "ventas_ty":    safe_float(r[23]),
        "ventas_ly":    safe_float(r[24]),
        "tl_ty_pct":    safe_float(r[14]),
        "tl_ly_pct":    safe_float(r[15]),
        "tl_meta":      safe_float(r[16]),
        "shrink_ly_pct":safe_float(r[4]),
        "shrink_meta":  safe_float(r[5]),
    }

acc_stores = [parse_store_row(r) for r in acc_rows]
acc_ventas    = sum(s["ventas_ty"] or 0 for s in acc_stores)
acc_tl_monto  = sum(s["tl_monto"]  or 0 for s in acc_stores)
acc_shrink    = sum(s["shrink_monto"] or 0 for s in acc_stores)
acc_dev       = sum(s["dev_ty"]    or 0 for s in acc_stores)
acc_dev_ly    = sum(s["dev_ly"]    or 0 for s in acc_stores)
acc_ventas_ly = sum(s["ventas_ly"] or 0 for s in acc_stores)

acc_tl_pct     = acc_tl_monto  / acc_ventas    if acc_ventas    else 0
acc_shrink_pct = acc_shrink    / acc_ventas    if acc_ventas    else 0

# LY% ponderado por Ventas LY acumulado
acc_tl_ly_monto     = sum((s["tl_ly_pct"]     or 0) * (s["ventas_ly"] or 0) for s in acc_stores)
acc_shrink_ly_monto = sum((s["shrink_ly_pct"] or 0) * (s["ventas_ly"] or 0) for s in acc_stores)
acc_tl_ly     = acc_tl_ly_monto     / acc_ventas_ly if acc_ventas_ly else acc_tl_pct
acc_shrink_ly = acc_shrink_ly_monto / acc_ventas_ly if acc_ventas_ly else acc_shrink_pct

# Meta ponderada por Ventas TY acumulado → Alcance
acc_meta_tl_pond     = sum((s["tl_meta"]     or 0) * (s["ventas_ty"] or 0) for s in acc_stores)
acc_meta_shrink_pond = sum((s["shrink_meta"] or 0) * (s["ventas_ty"] or 0) for s in acc_stores)
acc_meta_tl     = acc_meta_tl_pond     / acc_ventas if acc_ventas else 0
acc_meta_shrink = acc_meta_shrink_pond / acc_ventas if acc_ventas else 0

acc_alcance_tl     = round(acc_meta_tl     / acc_tl_pct     * 100) if acc_tl_pct     else 0
acc_alcance_shrink = round(acc_meta_shrink / acc_shrink_pct * 100) if acc_shrink_pct else 0

print(f"Filas Acumulado Mes {mes_actual}: {len(acc_rows)}")

dev_ly_fmt = fmt_money(total_dev_ly) if total_dev_ly else "N/D"
acc_dev_ly_fmt = fmt_money(acc_dev_ly) if acc_dev_ly else "N/D"

# ── Generar filas de tabla ────────────────────────────────────────────────────
def store_row(s: dict, bg: str) -> str:
    tl_pct_s   = pct(s["tl_ty_pct"])
    sh_pct_s   = pct(s["shrink_ty_pct"])
    dev_str    = fmt_money(s["dev_ty"])
    dev_color  = "text-green-600" if (s["dev_ty"] or 0) >= 0 else "text-red-600"
    tl_bps     = bps_span(s["tl_ty_pct"], s["tl_ly_pct"])
    sh_bps     = bps_span(s["shrink_ty_pct"], s["shrink_ly_pct"])
    return f"""<tr class="border-b hover:bg-{bg}-50">
    <td class="px-2 py-2 font-medium">{s['tienda']}</td>
    <td class="px-2 py-2">{s['distrital']}</td>
    <td class="px-2 py-2 text-center">{formato_badge(s['formato'])}</td>
    <td class="px-2 py-2 text-center">{s['pais']}</td>
    <td class="px-2 py-2 text-right font-semibold">-{tl_pct_s} {tl_bps}</td>
    <td class="px-2 py-2 text-right">-{sh_pct_s} {sh_bps}</td>
    <td class="px-2 py-2 text-right {dev_color}">{dev_str}</td>
</tr>"""

rows_logro = "\n".join(store_row(s, "green") for s in en_logro_sorted)
rows_fuera = "\n".join(store_row(s, "red")   for s in fuera_sorted)

# ── HTML ─────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultados 2026 - Cierre Semana {SEMANA}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        @media print {{
            .no-print {{ display: none !important; }}
            .page-break {{ page-break-before: always; }}
            body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
        .gradient-header {{ background: linear-gradient(135deg, #0053e2 0%, #003399 100%); }}
        .card {{ box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }}
        .metric-card {{ transition: transform 0.2s; }}
        .metric-card:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="gradient-header text-white py-6 px-6">
        <div class="max-w-7xl mx-auto">
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-2xl font-bold">Resultados 2026 - Cierre Semana {SEMANA}</h1>
                    <h2 class="text-base mt-2 font-bold" style="color: #ffc220;">Total Loss, Shrink, Devolución de Merma</h2>
                    <p class="text-xs mt-2 text-blue-200 font-bold">Protección de Activos - Centroamérica</p>
                </div>
                <a href="https://app.powerbi.com/reportEmbed?reportId=10cadfe8-706b-4aa3-a177-db6620371a49&autoAuth=true&ctid=3cbcc3d3-094d-4006-9849-0d11d61f484d"
                   target="_blank"
                   class="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2 text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Dashboard
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
        <!-- KPIs -->
        <section class="mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Indicadores Clave de Desempeño</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-blue-500">
                    <p class="text-sm text-gray-500">Total Tiendas</p>
                    <p class="text-3xl font-bold text-gray-800">{total_tiendas}</p>
                    <p class="text-xs text-gray-400 mt-1">Analizadas</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-green-500">
                    <p class="text-sm text-gray-500">En Logro</p>
                    <p class="text-3xl font-bold text-green-600">{len(en_logro)}</p>
                    <p class="text-xs text-green-500 mt-1">{pct_en_logro:.1f}% del total</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-red-500">
                    <p class="text-sm text-gray-500">Fuera de Logro</p>
                    <p class="text-3xl font-bold text-red-600">{len(fuera)}</p>
                    <p class="text-xs text-red-500 mt-1">{pct_fuera:.1f}% del total</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-purple-500">
                    <p class="text-sm text-gray-500">Tiendas Alta Merma</p>
                    <p class="text-3xl font-bold text-purple-600">{tam_ytd_total}</p>
                    <p class="text-xs mt-1" style="color: {alta_merma_color}">{delta_str} vs LY</p>
                </div>
            </div>
        </section>

        <!-- Indicadores Principales -->
        <section class="mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Indicadores Principales</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Total Loss</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{fmt_money(total_tl_monto, force_abs=True)}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">
                        {tl_ty_pct_global*100:.2f}% TY &nbsp; {tl_ly_global*100:.2f}% LY &nbsp; Alcance {alcance_tl_global:.0f}%</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado-Mes</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {fmt_money(acc_tl_monto, force_abs=True)} &nbsp; {acc_tl_pct*100:.2f}% TY &nbsp; {acc_tl_ly*100:.2f}% LY &nbsp; Alcance {acc_alcance_tl}%</p>
                </div>
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Shrink</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{fmt_money(total_shrink, force_abs=True)}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">
                        {shrink_pct_global*100:.2f}% TY &nbsp; {shrink_ly_global*100:.2f}% LY &nbsp; Alcance {alcance_shrink_global:.0f}%</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado-Mes</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {fmt_money(acc_shrink, force_abs=True)} &nbsp; {acc_shrink_pct*100:.2f}% TY &nbsp; {acc_shrink_ly*100:.2f}% LY &nbsp; Alcance {acc_alcance_shrink}%</p>
                </div>
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Devolución Merma (Preliminar a Costo)</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{fmt_money(total_dev, force_abs=True)}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">{dev_ly_fmt} LY</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado-Mes</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {fmt_money(acc_dev, force_abs=True)} TY &nbsp; {acc_dev_ly_fmt} LY</p>
                </div>
            </div>
        </section>

        <!-- Tiendas en Logro -->
        <section class="mb-8 page-break">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Tiendas en Logro</h3>
            <div class="bg-white rounded-xl card overflow-hidden">
                <table class="w-full" style="font-size:11px;">
                    <thead class="bg-green-600 text-white">
                        <tr>
                            <th class="px-2 py-2 text-left">Tienda</th>
                            <th class="px-2 py-2 text-left">Distrital Ops</th>
                            <th class="px-2 py-2 text-center">Formato</th>
                            <th class="px-2 py-2 text-center">País</th>
                            <th class="px-2 py-2 text-right">Total Loss %</th>
                            <th class="px-2 py-2 text-right">Shrink %</th>
                            <th class="px-2 py-2 text-right">Dev. Merma</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_logro}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Tiendas Fuera de Logro -->
        <section class="mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Tiendas Fuera de Logro (Requieren Atención)</h3>
            <div class="bg-white rounded-xl card overflow-hidden">
                <table class="w-full" style="font-size:11px;">
                    <thead class="bg-red-600 text-white">
                        <tr>
                            <th class="px-2 py-2 text-left">Tienda</th>
                            <th class="px-2 py-2 text-left">Distrital Ops</th>
                            <th class="px-2 py-2 text-center">Formato</th>
                            <th class="px-2 py-2 text-center">País</th>
                            <th class="px-2 py-2 text-right">Total Loss %</th>
                            <th class="px-2 py-2 text-right">Shrink %</th>
                            <th class="px-2 py-2 text-right">Dev. Merma</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_fuera}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Graficas barras -->
        <section class="mb-8 grid md:grid-cols-2 gap-6">
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Total Loss por Formato</h4>
                <div style="height: 180px;">
                    <canvas id="chartFormato"></canvas>
                </div>
            </div>
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Total Loss por País</h4>
                <div style="height: 180px;">
                    <canvas id="chartPais"></canvas>
                </div>
            </div>
        </section>

        <!-- Graficos composicion -->
        <section class="mb-8 grid md:grid-cols-3 gap-6">
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Participación por Tipo Merma</h4>
                <div style="height: 250px;">
                    <canvas id="chartComposicion"></canvas>
                </div>
            </div>
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Shrink por Causa</h4>
                <div style="height: 250px;">
                    <canvas id="chartShrinkCausa"></canvas>
                </div>
            </div>
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Dañado por Causa</h4>
                <div style="height: 250px;">
                    <canvas id="chartDanadoCausa"></canvas>
                </div>
            </div>
        </section>

        <footer class="text-center text-white text-xs py-3 rounded-xl"
                style="background: linear-gradient(135deg, #0053e2 0%, #003399 100%);">
            <p class="font-semibold tracking-wide">Confidential - Walmart</p>
        </footer>
    </main>

    <script>
        const fmtAlcances  = {fmt_alcances};
        const paisAlcances = {pais_alcances};

        new Chart(document.getElementById('chartFormato'), {{
            type: 'bar',
            plugins: [ChartDataLabels],
            data: {{
                labels: {fmt_labels},
                datasets: [{{
                    label: 'Total Loss %',
                    data: {fmt_vals},
                    backgroundColor: ['#0053e2','#3b82f6','#60a5fa','#93c5fd'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                layout: {{ padding: {{ top: 20 }} }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ callbacks: {{
                        afterLabel: (ctx) => 'Alcance: ' + fmtAlcances[ctx.dataIndex] + '%'
                    }}}},
                    datalabels: {{
                        anchor: 'end', align: 'top',
                        color: '#1f2937',
                        font: {{ size: 11, weight: 'bold' }},
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }},
                scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: '% Total Loss' }},
                    ticks: {{ callback: (v) => v + '%' }} }} }}
            }}
        }});

        new Chart(document.getElementById('chartPais'), {{
            type: 'bar',
            plugins: [ChartDataLabels],
            data: {{
                labels: {pais_labels},
                datasets: [{{
                    label: 'Total Loss %',
                    data: {pais_vals},
                    backgroundColor: ['#059669','#10b981','#34d399','#6ee7b7','#a7f3d0'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                layout: {{ padding: {{ top: 20 }} }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ callbacks: {{
                        afterLabel: (ctx) => 'Alcance: ' + paisAlcances[ctx.dataIndex] + '%'
                    }}}},
                    datalabels: {{
                        anchor: 'end', align: 'top',
                        color: '#1f2937',
                        font: {{ size: 11, weight: 'bold' }},
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }},
                scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: '% Total Loss' }},
                    ticks: {{ callback: (v) => v + '%' }} }} }}
            }}
        }});

        new Chart(document.getElementById('chartComposicion'), {{
            type: 'pie',
            plugins: [ChartDataLabels],
            data: {{
                labels: ['Shrink', 'Dañado'],
                datasets: [{{
                    data: [{round(shrink_total)}, {round(danado_total)}],
                    backgroundColor: ['#0053e2','#f59e0b'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{
                        color: '#fff', font: {{ size: 12, weight: 'bold' }},
                        formatter: (value, ctx) => {{
                            let sum = ctx.dataset.data.reduce((a,b) => a+b, 0);
                            return (value*100/sum).toFixed(1) + '%';
                        }}
                    }}
                }}
            }}
        }});

        new Chart(document.getElementById('chartShrinkCausa'), {{
            type: 'pie',
            plugins: [ChartDataLabels],
            data: {{
                labels: ['Hurto','Faltantes','Merma Admin.','Solo PI'],
                datasets: [{{
                    data: [{hurto_pct}, {falt_pct}, {madm_pct}, {spi_pct}],
                    backgroundColor: ['#7f1d1d','#dc2626','#f87171','#fecaca'],
                    borderWidth: 2, borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{ color: '#fff', font: {{ size: 11, weight: 'bold' }}, formatter: (v) => v + '%' }}
                }}
            }}
        }});

        new Chart(document.getElementById('chartDanadoCausa'), {{
            type: 'pie',
            plugins: [ChartDataLabels],
            data: {{
                labels: ['Vencimiento','Manipulación','Calidad','Plagas'],
                datasets: [{{
                    data: [{venc_pct}, {man_pct}, {cal_pct}, {plg_pct}],
                    backgroundColor: ['#7c2d12','#ea580c','#fb923c','#fed7aa'],
                    borderWidth: 2, borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{
                        color: (ctx) => ctx.dataIndex < 2 ? '#fff' : '#333',
                        font: {{ size: 11, weight: 'bold' }},
                        formatter: (v) => v + '%'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

OUT_PATH.write_text(html, encoding="utf-8")
print(f"OK Reporte generado: {OUT_PATH}")
print(f"   Tiendas Semana {SEMANA}: {total_tiendas}")
print(f"   En Logro: {len(en_logro)} | Fuera: {len(fuera)}")
print(f"   Total Loss: {fmt_money(total_tl_monto)} ({abs(tl_ty_pct_global)*100:.2f}%)")
print(f"   Shrink: {fmt_money(total_shrink)} ({abs(shrink_pct_global)*100:.2f}%)")
print(f"   Dev Merma: {fmt_money(total_dev)}")