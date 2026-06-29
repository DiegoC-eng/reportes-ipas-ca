"""Plantilla HTML del reporte de Protección de Activos CA.

Se separa de generate.py para mantener archivos pequeños y legibles.
La semana y el mes los inyecta generate.py (una sola fuente de verdad).
"""


def _money(v):
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"


def build_html(n_total, n_logro, n_fuera, alta, alta_ly, w, m,
               logro_rows, fuera_rows, c_logro, c_fuera,
               fmt_order, fmt_agg, pais_order, pais_agg,
               semana, mes_nombre):
    SEMANA = semana
    MES_NOMBRE = mes_nombre
    pct_logro = n_logro / n_total * 100
    pct_fuera = n_fuera / n_total * 100
    delta_tam = alta - alta_ly
    if delta_tam > 0:
        tam_note = f'<span class="text-red-600">+{delta_tam} vs LY</span>'
    elif delta_tam < 0:
        tam_note = f'<span class="text-green-600">{delta_tam} vs LY</span>'
    else:
        tam_note = '<span class="text-gray-500">igual vs LY</span>'

    fmt_labels = ", ".join(f'"{f}"' for f in fmt_order)
    fmt_data = ", ".join(f"{fmt_agg[f][0]:.4f}" for f in fmt_order)
    fmt_alc = ", ".join(f"{fmt_agg[f][1]:.1f}" for f in fmt_order)
    pais_labels = ", ".join(f'"{p}"' for p in pais_order)
    pais_data = ", ".join(f"{pais_agg[p][0]:.4f}" for p in pais_order)
    pais_alc = ", ".join(f"{pais_agg[p][1]:.1f}" for p in pais_order)

    return f"""<!DOCTYPE html>
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
        body {{ font-family: 'Inter', sans-serif; background:#f9fafb; }}
        @media print {{
            .no-print {{ display: none !important; }}
            .page-break {{ page-break-before: always; }}
            body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
        .gradient-header {{ background: linear-gradient(135deg, #0053e2 0%, #003399 100%); }}
        .card {{ box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }}
        .metric-card {{ transition: transform 0.2s; }}
        .metric-card:hover {{ transform: translateY(-2px); }}
        .table-scroll {{ max-height: 420px; overflow-y: auto; }}
        thead {{ position: sticky; top: 0; z-index: 1; }}
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
                    <p class="text-xs mt-2 text-blue-200 font-bold">Protección de Activos - Centroamérica &nbsp;|&nbsp; {n_total} Tiendas</p>
                </div>
                <a href="https://app.powerbi.com/reportEmbed?reportId=10cadfe8-706b-4aa3-a177-db6620371a49&autoAuth=true&ctid=3cbcc3d3-094d-4006-9849-0d11d61f484d" target="_blank"
                   class="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2 text-sm no-print">
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
                    <p class="text-3xl font-bold text-gray-800">{n_total}</p>
                    <p class="text-xs text-gray-400 mt-1">Analizadas</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-green-500">
                    <p class="text-sm text-gray-500">En Logro</p>
                    <p class="text-3xl font-bold text-green-600">{n_logro}</p>
                    <p class="text-xs text-green-500 mt-1">{pct_logro:.1f}% del total</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-red-500">
                    <p class="text-sm text-gray-500">Fuera de Logro</p>
                    <p class="text-3xl font-bold text-red-600">{n_fuera}</p>
                    <p class="text-xs text-red-500 mt-1">{pct_fuera:.1f}% del total</p>
                </div>
                <div class="metric-card bg-white rounded-xl p-5 card border-l-4 border-purple-500">
                    <p class="text-sm text-gray-500">Tiendas Alta Merma</p>
                    <p class="text-3xl font-bold text-purple-600">{alta}</p>
                    <p class="text-xs mt-1 font-semibold">{tam_note}</p>
                </div>
            </div>
        </section>

        <!-- Indicadores Principales -->
        <section class="mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Indicadores Principales</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Total Loss</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{_money(w['tl_monto'])}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">
                        -{w['tl_pct']:.2f}% TY &nbsp; -{w['tl_ly']:.2f}% LY &nbsp; Alcance {w['tl_alc']:.0f}%</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado - Mes {MES_NOMBRE}</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {_money(m['tl_monto'])} &nbsp; -{m['tl_pct']:.2f}% TY &nbsp; -{m['tl_ly']:.2f}% LY &nbsp; Alcance {m['tl_alc']:.0f}%</p>
                </div>
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Shrink</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{_money(w['sh_monto'])}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">
                        -{w['sh_pct']:.2f}% TY &nbsp; -{w['sh_ly']:.2f}% LY &nbsp; Alcance {w['sh_alc']:.0f}%</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado - Mes {MES_NOMBRE}</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {_money(m['sh_monto'])} &nbsp; -{m['sh_pct']:.2f}% TY &nbsp; Alcance {m['sh_alc']:.0f}%</p>
                </div>
                <div class="rounded-xl p-6 card" style="background: linear-gradient(135deg, #fff4cc 0%, #ffe680 100%);">
                    <p class="font-bold text-center" style="color: #7a6520;">Devolución Merma</p>
                    <p class="text-3xl font-bold mt-2 text-center" style="color: #2a8703;">{_money(w['dev'])}</p>
                    <p class="text-sm mt-2 text-center" style="color: #8a7530;">{_money(w['dev_ly'])} LY</p>
                    <p class="mt-3 text-center font-bold" style="color: #7a6520; font-size:11px;">Acumulado - Mes {MES_NOMBRE}</p>
                    <p class="text-center font-bold" style="color: #7a6520; font-size:10px;">
                        {_money(m['dev'])} TY</p>
                </div>
            </div>
        </section>

        <!-- Tiendas en Logro -->
        <section class="mb-8 page-break">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">
                Tiendas en Logro
                <span class="text-sm font-normal text-green-600 ml-2">{c_logro} tiendas</span>
            </h3>
            <div class="bg-white rounded-xl card overflow-hidden">
                <div class="table-scroll">
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
{logro_rows}
                    </tbody>
                </table>
                </div>
            </div>
        </section>

        <!-- Tiendas Fuera de Logro -->
        <section class="mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">
                Tiendas Fuera de Logro (Requieren Atención)
                <span class="text-sm font-normal text-red-600 ml-2">{c_fuera} tiendas</span>
            </h3>
            <div class="bg-white rounded-xl card overflow-hidden">
                <div class="table-scroll">
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
{fuera_rows}
                    </tbody>
                </table>
                </div>
            </div>
        </section>

        <!-- Gráficas barras -->
        <section class="mb-8 grid md:grid-cols-2 gap-6">
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Total Loss % por Formato</h4>
                <div style="height: 220px;">
                    <canvas id="chartFormato"></canvas>
                </div>
            </div>
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Total Loss % por País</h4>
                <div style="height: 220px;">
                    <canvas id="chartPais"></canvas>
                </div>
            </div>
        </section>

        <!-- Graficos composicion (detalle de causas vive en PowerBI) -->
        <section class="mb-8 grid md:grid-cols-3 gap-6">
            <div class="bg-white rounded-xl p-6 card">
                <h4 class="font-semibold text-gray-700 mb-4">Participación de Merma</h4>
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
        Chart.register(ChartDataLabels);

        const formatoAlcance = [{fmt_alc}];
        const paisAlcance    = [{pais_alc}];

        // Total Loss por Formato
        new Chart(document.getElementById('chartFormato'), {{
            type: 'bar',
            data: {{
                labels: [{fmt_labels}],
                datasets: [{{
                    label: 'Total Loss %',
                    data: [{fmt_data}],
                    backgroundColor: "#7dd3fc",
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                layout: {{ padding: {{ top: 24 }} }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const alc = formatoAlcance[ctx.dataIndex];
                                return [
                                    'TL %: ' + ctx.parsed.y.toFixed(2) + '%',
                                    'Alcance: ' + alc + '%'
                                ];
                            }}
                        }}
                    }},
                    datalabels: {{
                        anchor: 'end', align: 'top',
                        color: '#1f2937',
                        font: {{ size: 11, weight: 'bold' }},
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }},
                scales: {{ y: {{ display: false }} }}
            }}
        }});

        // Total Loss por País
        new Chart(document.getElementById('chartPais'), {{
            type: 'bar',
            data: {{
                labels: [{pais_labels}],
                datasets: [{{
                    label: 'Total Loss %',
                    data: [{pais_data}],
                    backgroundColor: "#86efac",
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                layout: {{ padding: {{ top: 24 }} }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const alc = paisAlcance[ctx.dataIndex];
                                return [
                                    'TL %: ' + ctx.parsed.y.toFixed(2) + '%',
                                    'Alcance: ' + alc + '%'
                                ];
                            }}
                        }}
                    }},
                    datalabels: {{
                        anchor: 'end', align: 'top',
                        color: '#1f2937',
                        font: {{ size: 11, weight: 'bold' }},
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }},
                scales: {{ y: {{ display: false }} }}
            }}
        }});

        // Participación de Merma (Shrink vs Dañado) = monto Shrink / monto Total Loss
        new Chart(document.getElementById('chartComposicion'), {{
            type: 'pie',
            data: {{
                labels: ['Shrink', 'Dañado'],
                datasets: [{{
                    data: [{abs(w['sh_monto']):.0f}, {abs(w['tl_monto']) - abs(w['sh_monto']):.0f}],
                    backgroundColor: ['#0053e2', '#f59e0b'],
                    borderWidth: 2, borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{
                        color: '#fff', font: {{ size: 8, weight: 'bold' }},
                        clamp: true,
                        formatter: (value, ctx) => {{
                            const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            return (value * 100 / sum).toFixed(1) + '%';
                        }}
                    }}
                }}
            }}
        }});

        // Shrink por Causa - detalle PowerBI
        new Chart(document.getElementById('chartShrinkCausa'), {{
            type: 'pie',
            data: {{
                labels: ['Hurto', 'Faltantes', 'Merma Admin.', 'Solo PI'],
                datasets: [{{
                    data: [72.93, 21.13, 2.46, 3.48],
                    backgroundColor: ['#7f1d1d','#dc2626','#f87171','#fecaca'],
                    borderWidth: 2, borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{
                        color: (ctx) => ctx.dataIndex < 2 ? '#fff' : '#333',
                        font: {{ size: 8, weight: 'bold' }},
                        clamp: true,
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }}
            }}
        }});

        // Dañado por Causa - detalle PowerBI
        new Chart(document.getElementById('chartDanadoCausa'), {{
            type: 'pie',
            data: {{
                labels: ['Vencimiento', 'Manipulación', 'Calidad', 'Otros', 'Plagas'],
                datasets: [{{
                    data: [45.64, 25.46, 12.12, 10.11, 6.68],
                    backgroundColor: ['#7c2d12','#ea580c','#fb923c','#fed7aa','#fef3c7'],
                    borderWidth: 2, borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, boxWidth: 12, padding: 8 }} }},
                    datalabels: {{
                        color: (ctx) => ctx.dataIndex < 3 ? '#fff' : '#333',
                        font: {{ size: 8, weight: 'bold' }},
                        clamp: true,
                        formatter: (v) => v.toFixed(2) + '%'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
