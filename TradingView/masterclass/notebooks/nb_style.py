"""
nb_style.py — Módulo de Estilo Visual para los Notebooks del Masterclass
=========================================================================
Importar al inicio de cada notebook:
    from nb_style import *
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# # PALETA DE COLORES
# COLORS = {
    'bg':           '#0d1117',
    'bg_card':      '#161b22',
    'bg_light':     '#1c2333',
    'grid':         '#21262d',
    'text':         '#c9d1d9',
    'text_dim':     '#8b949e',
    'text_bright':  '#f0f6fc',
    'blue':         '#58a6ff',
    'blue_dark':    '#1f6feb',
    'green':        '#3fb950',
    'green_dark':   '#238636',
    'red':          '#f85149',
    'red_dark':     '#da3633',
    'orange':       '#d29922',
    'purple':       '#bc8cff',
    'cyan':         '#39d2c0',
    'pink':         '#f778ba',
    'yellow':       '#e3b341',
    'accent1':      '#58a6ff',   # Blue
    'accent2':      '#3fb950',   # Green
    'accent3':      '#f85149',   # Red
    'accent4':      '#d29922',   # Orange
    'accent5':      '#bc8cff',   # Purple
    'accent6':      '#39d2c0',   # Cyan
}

# Colores ordenados para series múltiples
PALETTE = [COLORS['blue'], COLORS['green'], COLORS['red'], COLORS['orange'],
           COLORS['purple'], COLORS['cyan'], COLORS['pink'], COLORS['yellow']]

# Colormaps custom
CMAP_DIVERGENT = LinearSegmentedColormap.from_list(
    'masterclass_div', [COLORS['red'], COLORS['bg_light'], COLORS['green']], N=256
)
CMAP_SEQUENTIAL = LinearSegmentedColormap.from_list(
    'masterclass_seq', [COLORS['bg_card'], COLORS['blue_dark'], COLORS['blue'], COLORS['cyan']], N=256
)
CMAP_HEAT = LinearSegmentedColormap.from_list(
    'masterclass_heat', [COLORS['bg_card'], COLORS['orange'], COLORS['red'], '#ff6b6b'], N=256
)

# # CONFIGURACIÓN GLOBAL DE MATPLOTLIB
# def setup_style():
    """Aplica el tema visual completo del masterclass."""
    plt.rcParams.update({
        # Fondo
        'figure.facecolor':     COLORS['bg'],
        'axes.facecolor':       COLORS['bg_card'],
        'savefig.facecolor':    COLORS['bg'],

        # Grid
        'axes.grid':            True,
        'grid.color':           COLORS['grid'],
        'grid.alpha':           0.6,
        'grid.linewidth':       0.5,
        'grid.linestyle':       '--',

        # Bordes
        'axes.edgecolor':       COLORS['grid'],
        'axes.linewidth':       0.8,

        # Texto
        'text.color':           COLORS['text'],
        'axes.labelcolor':      COLORS['text'],
        'xtick.color':          COLORS['text_dim'],
        'ytick.color':          COLORS['text_dim'],

        # Tipografía
        'font.family':          'sans-serif',
        'font.sans-serif':      ['Inter', 'SF Pro Display', 'Helvetica Neue', 'Arial'],
        'font.size':            11,
        'axes.titlesize':       15,
        'axes.titleweight':     'bold',
        'axes.labelsize':       12,
        'xtick.labelsize':      10,
        'ytick.labelsize':      10,
        'legend.fontsize':      10,

        # Figuras
        'figure.figsize':       (14, 6),
        'figure.dpi':           120,
        'savefig.dpi':          150,

        # Leyenda
        'legend.facecolor':     COLORS['bg_card'],
        'legend.edgecolor':     COLORS['grid'],
        'legend.framealpha':    0.9,
        'legend.labelcolor':    COLORS['text'],

        # Líneas
        'lines.linewidth':      1.8,
        'lines.antialiased':    True,
    })

# Aplicar al importar
setup_style()


# # FUNCIONES DE AYUDA PARA GRÁFICOS DIDÁCTICOS
# def create_figure(nrows=1, ncols=1, figsize=None, title=None, subtitle=None):
    """Crea una figura con título y subtítulo opcionales."""
    if figsize is None:
        w = 14 if ncols <= 2 else 18
        h = 6 * nrows
        figsize = (w, h)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

    if title:
        fig.suptitle(title, fontsize=17, fontweight='bold',
                     color=COLORS['text_bright'], y=0.98)
    if subtitle:
        fig.text(0.5, 0.94, subtitle, ha='center', fontsize=11,
                 color=COLORS['text_dim'], style='italic')

    return fig, axes


def annotate_point(ax, x, y, text, color=None, offset=(0, 15), fontsize=10,
                   arrow=True, ha='center'):
    """Agrega una anotación didáctica con flecha a un punto del gráfico."""
    if color is None:
        color = COLORS['yellow']

    arrow_props = dict(arrowstyle='->', color=color, lw=1.2) if arrow else None

    ax.annotate(
        text, xy=(x, y), xytext=offset, textcoords='offset points',
        fontsize=fontsize, color=color, fontweight='bold', ha=ha,
        arrowprops=arrow_props,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['bg'],
                  edgecolor=color, alpha=0.85)
    )


def add_stat_box(ax, stats_dict, loc='upper right', fontsize=9):
    """Agrega un recuadro de estadísticas al gráfico."""
    lines = []
    for key, val in stats_dict.items():
        if isinstance(val, float):
            lines.append(f'{key}: {val:.4f}')
        else:
            lines.append(f'{key}: {val}')
    text = '\n'.join(lines)

    props = dict(boxstyle='round,pad=0.5', facecolor=COLORS['bg'],
                 edgecolor=COLORS['blue'], alpha=0.9)

    positions = {
        'upper right': (0.97, 0.95),
        'upper left':  (0.03, 0.95),
        'lower right': (0.97, 0.05),
        'lower left':  (0.03, 0.05),
    }
    x_pos, y_pos = positions.get(loc, (0.97, 0.95))
    va = 'top' if 'upper' in loc else 'bottom'
    ha = 'right' if 'right' in loc else 'left'

    ax.text(x_pos, y_pos, text, transform=ax.transAxes, fontsize=fontsize,
            verticalalignment=va, horizontalalignment=ha, bbox=props,
            color=COLORS['text'], family='monospace')


def style_equity_curve(ax, ylabel='Retorno Acumulado (%)'):
    """Aplica estilo consistente a gráficos de equity."""
    ax.axhline(0, color=COLORS['text_dim'], linestyle='--', alpha=0.4, lw=0.8)
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))


def plot_semaphore_table(ax, data_dict, title='Validación In-Sample → Out-of-Sample'):
    """Dibuja una tabla tipo semáforo cuantitativo (Slide 12)."""
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', color=COLORS['text_bright'])

    metrics = list(data_dict.keys())
    n = len(metrics)

    for i, metric in enumerate(metrics):
        is_val, oos_val, threshold = data_dict[metric]
        if isinstance(is_val, float):
            degradation = abs(is_val - oos_val) / abs(is_val) * 100 if is_val != 0 else 0
        else:
            degradation = 0

        y = 0.85 - i * 0.15
        # Metric name
        ax.text(0.02, y, metric, fontsize=11, color=COLORS['text'],
                fontweight='bold', transform=ax.transAxes, va='center')
        # IS value
        ax.text(0.35, y, f'{is_val:.2f}' if isinstance(is_val, float) else str(is_val),
                fontsize=11, color=COLORS['blue'], transform=ax.transAxes,
                va='center', ha='center')
        # OOS value
        color = COLORS['green'] if degradation <= threshold else (
            COLORS['orange'] if degradation <= threshold * 2 else COLORS['red']
        )
        ax.text(0.55, y, f'{oos_val:.2f}' if isinstance(oos_val, float) else str(oos_val),
                fontsize=11, color=color, fontweight='bold',
                transform=ax.transAxes, va='center', ha='center')
        # Degradation
        emoji = '' if degradation <= threshold else ('' if degradation <= threshold * 2 else '')
        ax.text(0.75, y, f'{degradation:.0f}% {emoji}',
                fontsize=11, color=color, transform=ax.transAxes,
                va='center', ha='center')

    # Headers
    for x, label in [(0.02, 'Métrica'), (0.35, 'In-Sample'),
                      (0.55, 'Out-of-Sample'), (0.75, 'Degradación')]:
        ax.text(x, 0.97, label, fontsize=10, color=COLORS['text_dim'],
                fontweight='bold', transform=ax.transAxes, va='center',
                ha='center' if x > 0.1 else 'left')


def section_header(text, emoji=''):
    """Imprime un separador visual de sección en la salida del notebook."""
    width = 70
    print(f'\n{"" * width}')
    print(f' {emoji} {text}')
    print(f'{"" * width}\n')


def metric_card(label, value, fmt='.2f', good=True):
    """Imprime una métrica individual formateada."""
    icon = '' if good else ''
    if isinstance(value, float):
        print(f'  {icon} {label:.<35s} {value:{fmt}}')
    else:
        print(f'  {icon} {label:.<35s} {value}')


def print_metrics_table(metrics_dict, title='Métricas de Desempeño'):
    """Imprime una tabla limpia de métricas."""
    section_header(title, '')
    for key, (val, is_good) in metrics_dict.items():
        metric_card(key, val, good=is_good)
    print()


# # CONSTANTES DE BACKTEST
# INIT_CASH = 100_000
COST_BPS = 2          # 2 bps por lado
COST_PCT = 0.02       # Como porcentaje
FEES_VBT = 0.0001     # Para VectorBT (1 bp)

# Sesiones NQ (hora de NY)
NQ_RTH_START_H = 9
NQ_RTH_START_M = 30
NQ_RTH_END_H = 16

# Sesiones GC (hora de Chicago)
GC_SESSIONS = {
    'Asia':     (17, 1),    # 17:00 - 01:00 CT
    'Europe':   (1, 7),     # 01:00 - 07:00 CT
    'US_RTH':   (7, 13),    # 07:00 - 13:00 CT
    'Post_RTH': (13, 17),   # 13:00 - 17:00 CT
}

print(' nb_style.py cargado — Tema visual del Masterclass activado.')
