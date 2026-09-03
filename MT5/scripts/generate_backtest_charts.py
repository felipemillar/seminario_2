"""
Generador Institucional de la Triada Gráfica de Backtesting (QRT Solutions)
1. Curva de Equity (Capital Growth Curve)
2. Gráfico de Drawdown Underwater (Depth & Duration)
3. Gráfico de Excursiones MAE vs MFE (Trade Excursions Scatter Plot)
"""

import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BacktestCharts")

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def generate_backtest_charts(profits, maes=None, mfes=None, output_dir="MT5/backtests/charts", prefix="backtest"):
    """
    Genera los 3 gráficos obligatorios de auditoría cuantitativa:
    - {prefix}_equity_curve.png
    - {prefix}_drawdown_curve.png
    - {prefix}_excursions_mae_mfe.png
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        profits = np.array(profits, dtype=float)
        n_trades = len(profits)

        if n_trades == 0:
            logger.warning("No hay operaciones para graficar.")
            return {}

        # 1. Curva de Equity
        cum_equity = np.cumsum(profits)
        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
        ax.plot(range(1, n_trades + 1), cum_equity, color='#15803d', linewidth=1.8, label='Curva de Equity')
        ax.fill_between(range(1, n_trades + 1), cum_equity, 0, color='#16a34a', alpha=0.1)
        ax.set_title(f"Curva de Equity Acumulada · {n_trades} Operaciones (QRT Solutions)", fontsize=11, fontweight='bold', pad=12)
        ax.set_xlabel("Número de Operaciones", fontsize=9)
        ax.set_ylabel("PnL Acumulado (USD)", fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)
        equity_path = os.path.join(output_dir, f"{prefix}_equity_curve.png")
        plt.tight_layout()
        plt.savefig(equity_path)
        plt.close()

        # 2. Gráfico de Drawdown Underwater
        peak = np.maximum.accumulate(cum_equity)
        drawdown = cum_equity - peak
        fig, ax = plt.subplots(figsize=(10, 4.0), dpi=150)
        ax.fill_between(range(1, n_trades + 1), drawdown, 0, color='#ef4444', alpha=0.35, label='Drawdown')
        ax.plot(range(1, n_trades + 1), drawdown, color='#dc2626', linewidth=1.2)
        max_dd = np.min(drawdown)
        ax.axhline(max_dd, color='#991b1b', linestyle=':', linewidth=1.2, label=f'Max DD: {max_dd:,.2f}')
        ax.set_title(f"Curva de Drawdown Submarina (Underwater Chart)", fontsize=11, fontweight='bold', pad=12)
        ax.set_xlabel("Número de Operaciones", fontsize=9)
        ax.set_ylabel("Retroceso desde Máximos (USD)", fontsize=9)
        ax.legend(loc='lower left', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        dd_path = os.path.join(output_dir, f"{prefix}_drawdown_curve.png")
        plt.tight_layout()
        plt.savefig(dd_path)
        plt.close()

        # 3. Gráfico de Excursiones (MAE vs MFE)
        excursion_path = None
        if maes is not None and mfes is not None and len(maes) == n_trades:
            maes = np.array(maes, dtype=float)
            mfes = np.array(mfes, dtype=float)
            wins = profits > 0

            fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
            if np.any(wins):
                ax.scatter(maes[wins], mfes[wins], color='#16a34a', alpha=0.6, s=35, label='Trades Ganadores', edgecolors='none')
            if np.any(~wins):
                ax.scatter(maes[~wins], mfes[~wins], color='#ef4444', alpha=0.5, s=35, label='Trades Perdedores', edgecolors='none')

            # Líneas de referencia (Percentil 90 MAE y Mediana MFE de ganadores)
            if np.any(wins):
                p90_mae = np.percentile(maes[wins], 90)
                med_mfe = np.median(mfes[wins])
                ax.axvline(p90_mae, color='#b45309', linestyle='--', linewidth=1.2, label=f'P90 MAE Wins ({p90_mae:.2f}x ATR)')
                ax.axhline(med_mfe, color='#0369a1', linestyle='--', linewidth=1.2, label=f'Mediana MFE Wins ({med_mfe:.2f}x ATR)')

            ax.set_title(f"Dispersión de Excursiones MAE vs MFE (Sweeney & López de Prado)", fontsize=11, fontweight='bold', pad=12)
            ax.set_xlabel("Máxima Excursión Adversa (MAE en unidades ATR)", fontsize=9)
            ax.set_ylabel("Máxima Excursión Favorable (MFE en unidades ATR)", fontsize=9)
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.5)
            excursion_path = os.path.join(output_dir, f"{prefix}_excursions_mae_mfe.png")
            plt.tight_layout()
            plt.savefig(excursion_path)
            plt.close()

        logger.info(f"Triada gráfica generada exitosamente en {output_dir}")
        return {
            "equity_curve": equity_path,
            "drawdown_curve": dd_path,
            "excursions_chart": excursion_path
        }

    except Exception as err:
        logger.error(f"Error al generar gráficos de backtest: {type(err).__name__} (detalles omitidos por seguridad)")
        return {"error": f"Error de operación: {type(err).__name__}"}

if __name__ == "__main__":
    # Test básico
    np.random.seed(42)
    sample_trades = np.random.normal(loc=15, scale=50, size=150)
    sample_mae = np.abs(np.random.normal(loc=0.6, scale=0.3, size=150))
    sample_mfe = np.abs(np.random.normal(loc=1.2, scale=0.5, size=150))
    res = generate_backtest_charts(sample_trades, sample_mae, sample_mfe, prefix="sample_audit")
    print("Test de generación gráfica completado:", res)
