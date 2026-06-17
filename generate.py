"""Genera index.html del reporte de Protección de Activos CA desde Tiendas.csv.

Recalcula KPIs, indicadores, tablas y gráficas de formato/país para la semana
seleccionada. Las gráficas de causas (Shrink/Dañado por causa) se preservan
porque ese detalle no viene en el CSV (vive en PowerBI).
"""
import csv

CSV_PATH = r"C:/Users/d0c00v5/Downloads/Tiendas.csv"
OUT_PATH = r"C:/Users/d0c00v5/Documents/puppy_workspace/reportes-ipas-ca/index.html"
SEMANA = "19"
MES_TFI = "6"
MES_NOMBRE = "Junio"

FORMATO_BADGE = {
    "Supermercado": "bg-amber-100 text-amber-700",
    "Descuentos": "bg-blue-100 text-blue-700",
    "Bodegas": "bg-purple-100 text-purple-700",
    "Walmart": "bg-yellow-100 text-yellow-800",
}


def num(s):
    if s is None:
        return 0.0
    s = s.strip()
    if not s:
        return 0.0
    s = s.replace(".", "").replace(",", ".") if ("," in s) else s
    try:
        return float(s)
    except ValueError:
        return 0.0


def load():
    # El archivo trae BOM UTF-8; utf-8-sig lo descarta y respeta acentos.
    try:
        f = open(CSV_PATH, encoding="utf-8-sig")
        rows = list(csv.DictReader(f, delimiter=";"))
        f.close()
    except UnicodeDecodeError:
        f = open(CSV_PATH, encoding="latin-1")
        rows = list(csv.DictReader(f, delimiter=";"))
        f.close()
    return [{k.strip(): v for k, v in r.items()} for r in rows]


def money(v):
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"


def bps_span(ty_pct, ly_pct):
    """Devuelve el span html de cambio TY vs LY (en bps sobre %)."""
    delta = (abs(ty_pct) - abs(ly_pct)) * 100  # bps
    if ly_pct == 0:
        return ""
    if delta > 0:
        return (f' <span class="text-red-600 font-bold" style="font-size:9px;">'
                f'crece {abs(delta):.0f} bps</span>')
    return (f' <span class="text-green-600 font-bold" style="font-size:9px;">'
            f'mejora {abs(delta):.0f} bps</span>')


def store_row(r, hover):
    """Construye una fila <tr> de tienda."""
    tl_pct = num(r["Total Loss TY %"]) * 100
    tl_ly = num(r["Total Loss LY %"]) * 100
    sh_pct = num(r["Shrink TY %_1"]) * 100
    sh_ly = num(r["Shrink LY %"]) * 100
    dev = num(r["Devolucion TY"])
    fmt = r["Formato"]
    badge = FORMATO_BADGE.get(fmt, "bg-gray-100 text-gray-700")
    dev_color = "text-green-600" if dev >= 0 else "text-red-600"
    tl_cls = "font-semibold text-green-700" if hover == "green" else "font-semibold"
    return f"""<tr class="border-b hover:bg-{hover}-50" style="font-size:10px;">
    <td class="px-2 py-2 font-medium">{r['Tienda'].strip()}</td>
    <td class="px-2 py-2 text-gray-600" style="font-size:9px;">{r['Distrital Ops'].strip()}</td>
    <td class="px-2 py-2 text-center"><span class="px-2 py-1 {badge} rounded text-xs">{fmt}</span></td>
    <td class="px-2 py-2 text-center">{r['Pais']}</td>
    <td class="px-2 py-2 text-right {tl_cls}">{tl_pct:.2f}%{bps_span(tl_pct, tl_ly)}</td>
    <td class="px-2 py-2 text-right">{sh_pct:.2f}%{bps_span(sh_pct, sh_ly)}</td>
    <td class="px-2 py-2 text-right {dev_color}">{money(dev)}</td>
</tr>"""


def agg(rows, group_key):
    """Agrega TL% ponderado por ventas y alcance por grupo."""
    out = {}
    for g in {r[group_key] for r in rows}:
        gr = [r for r in rows if r[group_key] == g]
        tlm = sum(num(r["Total Loss TY Monto"]) for r in gr)
        vm = sum(num(r["Ventas TY"]) for r in gr)
        metam = sum(num(r["Meta Total Loss %"]) * num(r["Ventas TY"]) for r in gr)
        tlp = abs(tlm / vm * 100) if vm else 0
        metap = abs(metam / vm * 100) if vm else 0
        alc = (metap / tlp * 100) if tlp else 0
        out[g] = (tlp, alc)
    return out


def main():
    rows = load()
    wk = [r for r in rows if r["Semana"] == SEMANA]
    mes = [r for r in rows if r["Mes TFI"] == MES_TFI]

    n_total = len(wk)
    logro = [r for r in wk if num(r["Alcance Total Loss  %"]) >= 1.0]
    fuera = [r for r in wk if num(r["Alcance Total Loss  %"]) < 1.0]
    # Tiendas Alta Merma (TAM): suma de banderas 0/1 en columnas TAM YTD (2026)
    # y TAM LY (año anterior) para comparar si crece o decrece.
    alta = int(sum(num(r["TAM YTD"]) for r in wk))
    alta_ly = int(sum(num(r["TAM LY"]) for r in wk))

    logro.sort(key=lambda r: num(r["Total Loss TY %"]), reverse=True)
    fuera.sort(key=lambda r: num(r["Total Loss TY %"]), reverse=True)

    def totales(data):
        tlm = sum(num(r["Total Loss TY Monto"]) for r in data)
        shm = sum(num(r["Shrink TY %"]) for r in data)
        dnm = sum(num(r[next(k for k in data[0] if k.startswith('Da') and 'TY Monto' in k)]) for r in data)
        devm = sum(num(r["Devolucion TY"]) for r in data)
        devly = sum(num(r["Devolucion LY"]) for r in data)
        vm = sum(num(r["Ventas TY"]) for r in data)
        metatl = sum(num(r["Meta Total Loss %"]) * num(r["Ventas TY"]) for r in data)
        metash = sum(num(r["Meta Shrink %"]) * num(r["Ventas TY"]) for r in data)
        lytl = sum(num(r["Total Loss LY %"]) * num(r["Ventas TY"]) for r in data)
        lysh = sum(num(r["Shrink LY %"]) * num(r["Ventas TY"]) for r in data)
        return {
            "tl_monto": tlm, "sh_monto": shm, "dn_monto": dnm,
            "dev": devm, "dev_ly": devly,
            "tl_pct": abs(tlm / vm * 100), "sh_pct": abs(shm / vm * 100),
            "tl_meta": abs(metatl / vm * 100), "sh_meta": abs(metash / vm * 100),
            "tl_ly": abs(lytl / vm * 100), "sh_ly": abs(lysh / vm * 100),
        }

    w = totales(wk)
    m = totales(mes)
    w["tl_alc"] = w["tl_meta"] / w["tl_pct"] * 100
    w["sh_alc"] = w["sh_meta"] / w["sh_pct"] * 100
    m["tl_alc"] = m["tl_meta"] / m["tl_pct"] * 100
    m["sh_alc"] = m["sh_meta"] / m["sh_pct"] * 100

    fmt_agg = agg(wk, "Formato")
    pais_agg = agg(wk, "Pais")
    fmt_order = ["Supermercado", "Descuentos", "Bodegas", "Walmart"]
    fmt_order = [f for f in fmt_order if f in fmt_agg]
    pais_order = sorted(pais_agg, key=lambda p: pais_agg[p][0], reverse=True)

    logro_rows = "\n".join(store_row(r, "green") for r in logro)
    fuera_rows = "\n".join(store_row(r, "gray") for r in fuera)

    html = build_html(
        n_total, len(logro), len(fuera), alta, alta_ly, w, m,
        logro_rows, fuera_rows, len(logro), len(fuera),
        fmt_order, fmt_agg, pais_order, pais_agg,
    )
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK -> {OUT_PATH}")
    print(f"Semana {SEMANA}: {n_total} tiendas | logro {len(logro)} | "
          f"fuera {len(fuera)} | alta merma {alta}")
    print(f"TL semana: {money(w['tl_monto'])} ({w['tl_pct']:.2f}% / "
          f"alc {w['tl_alc']:.0f}%)")
    print(f"TL acum mes: {money(m['tl_monto'])} ({m['tl_pct']:.2f}%)")


from html_template import build_html  # noqa: E402


if __name__ == "__main__":
    main()
