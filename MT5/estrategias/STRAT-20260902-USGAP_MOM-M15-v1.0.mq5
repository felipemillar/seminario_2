//+------------------------------------------------------------------+
//|                          STRAT-20260902-USGAP_MOM-M15-v1.0.mq5  |
//|               QUANT AGENTIC SWARM (QAS) - EA GENERADO POO        |
//|  Tesis: Gap de Apertura EEUU (Momentum) + Z-Score D1 + 3 Barreras|
//+------------------------------------------------------------------+
#property copyright   "Quant Agentic Swarm"
#property link        "https://github.com/quant-agentic-swarm"
#property version     "1.00"
#property description "STRAT-20260902-USGAP_MOM-M15-v1.0"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| ENUMERACIONES Y TIPOS                                            |
//+------------------------------------------------------------------+
enum ENUM_VOL_REGIME
{
   REGIME_LOW = 0,    // Baja Volatilidad (Compresion)
   REGIME_MEDIUM = 1, // Volatilidad Media (Normal)
   REGIME_HIGH = 2    // Alta Volatilidad (Expansion)
};

enum ENUM_GAP_DIR
{
   GAP_NONE = 0,
   GAP_UP   = 1,
   GAP_DOWN = -1
};

//+------------------------------------------------------------------+
//| INPUTS DE USUARIO (CON SANITY CHECKS)                            |
//+------------------------------------------------------------------+
input group "1. Deteccion de Gap de Apertura"
input double   InpGapThresholdATR  = 1.0;     // Umbral de Gap (k_gap * ATR_D14)
input double   InpMaxRetracePct    = 0.5;     // Retroceso Maximo Permitido (0.0 a 1.0) del rango M15
input int      InpSessionStartHour = 9;       // Hora Apertura Sesion (Hora Servidor) - CALIBRAR a 09:30 ET
input int      InpSessionStartMin  = 30;      // Minuto Apertura Sesion (Hora Servidor) - CALIBRAR a 09:30 ET

input group "2. Regimen de Volatilidad MTF (D1)"
input int      InpFastAtrPeriod    = 5;       // Periodo ATR Rapido (D1)
input int      InpSlowAtrPeriod    = 14;      // Periodo ATR Lento (D1)
input int      InpZScoreWindow     = 20;      // Ventana Z-Score (Dias)
input double   InpZScoreThreshold  = 0.67;    // Umbral Z-Score Alta Volatilidad

input group "3. Salidas: Triple Barrier Method"
input double   InpProfitMultiplier = 2.0;     // Multiplicador B1 (Take Profit * ATR D1)
input double   InpStopMultiplier   = 1.0;     // Multiplicador B2 (Stop Loss * ATR Intradia)
input int      InpMaxHoldingBars   = 26;      // Limite Temporal B3 (Barras M15)

input group "4. Gestion de Orden y Trazabilidad"
input double   InpLotSize          = 0.10;    // Tamaño de Lote Fijo
input ulong    InpMagicNumber      = 20260902;// Magic Number Unico
input string   InpStrategyID       = "STRAT-20260902-USGAP_MOM-M15-v1.0"; // Strategy ID

//+------------------------------------------------------------------+
//| CLASE UTILIDAD: DETECTOR DE NUEVA BARRA                          |
//+------------------------------------------------------------------+
class CIsNewBar
{
private:
   datetime m_last_bar_time;
public:
   CIsNewBar() { m_last_bar_time = 0; }
   bool IsNewBar(ENUM_TIMEFRAMES tf = PERIOD_CURRENT)
   {
      datetime cur_bar_time = iTime(_Symbol, tf, 0);
      if(cur_bar_time != m_last_bar_time && cur_bar_time != 0)
      {
         m_last_bar_time = cur_bar_time;
         return true;
      }
      return false;
   }
};

//+------------------------------------------------------------------+
//| VARIABLES GLOBALES Y HANDLES                                     |
//+------------------------------------------------------------------+
CTrade      g_trade;
CIsNewBar   g_bar_detector_m15;
int         g_handle_atr5_d1  = INVALID_HANDLE;
int         g_handle_atr14_d1 = INVALID_HANDLE;
int         g_handle_atr_m15  = INVALID_HANDLE;

// Estado del gap del dia en curso
ENUM_GAP_DIR g_gap_direction     = GAP_NONE;
double       g_gap_value         = 0.0;
double       g_session_open      = 0.0;
datetime     g_last_processed_day = 0; // Evita recalcular/re-evaluar mas de 1 vez por sesion

//+------------------------------------------------------------------+
//| FUNCION DE INICIALIZACION (OnInit)                               |
//+------------------------------------------------------------------+
int OnInit()
{
   if(InpProfitMultiplier <= 0 || InpStopMultiplier <= 0 || InpMaxHoldingBars <= 0 || InpGapThresholdATR <= 0)
   {
      Print("[ERROR] Parametros de Gap/Triple Barrera incorrectos. Deben ser mayores a 0.");
      return(INIT_PARAMETERS_INCORRECT);
   }
   if(InpSessionStartHour < 0 || InpSessionStartHour > 23 || InpSessionStartMin < 0 || InpSessionStartMin > 59)
   {
      Print("[ERROR] Hora/Minuto de sesion invalidos.");
      return(INIT_PARAMETERS_INCORRECT);
   }

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(20);

   g_handle_atr5_d1  = iATR(_Symbol, PERIOD_D1, InpFastAtrPeriod);
   g_handle_atr14_d1 = iATR(_Symbol, PERIOD_D1, InpSlowAtrPeriod);
   g_handle_atr_m15  = iATR(_Symbol, PERIOD_CURRENT, 14);

   if(g_handle_atr5_d1 == INVALID_HANDLE || g_handle_atr14_d1 == INVALID_HANDLE || g_handle_atr_m15 == INVALID_HANDLE)
   {
      Print("[ERROR] No se pudieron inicializar los handles de ATR.");
      return(INIT_FAILED);
   }

   PrintFormat("[INIT OK] %s inicializado correctamente.", InpStrategyID);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| FUNCION DE DESINICIALIZACION (OnDeinit)                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   IndicatorRelease(g_handle_atr5_d1);
   IndicatorRelease(g_handle_atr14_d1);
   IndicatorRelease(g_handle_atr_m15);
   Comment("");
}

//+------------------------------------------------------------------+
//| CALCULO DEL Z-SCORE DE VOLATILIDAD DIARIA                        |
//+------------------------------------------------------------------+
ENUM_VOL_REGIME CalculateDailyVolatilityZScore(double &out_zscore, double &out_atr5, double &out_atr14)
{
   double atr5_buf[], atr14_buf[];
   ArraySetAsSeries(atr5_buf, true);
   ArraySetAsSeries(atr14_buf, true);

   if(CopyBuffer(g_handle_atr5_d1,  0, 1, InpZScoreWindow, atr5_buf)  < InpZScoreWindow ||
      CopyBuffer(g_handle_atr14_d1, 0, 1, InpZScoreWindow, atr14_buf) < InpZScoreWindow)
   {
      out_zscore = 0.0;
      return(REGIME_MEDIUM);
   }

   out_atr5  = atr5_buf[0];
   out_atr14 = atr14_buf[0];

   double diff_buf[];
   ArrayResize(diff_buf, InpZScoreWindow);
   double sum = 0.0;

   for(int i = 0; i < InpZScoreWindow; i++)
   {
      diff_buf[i] = atr5_buf[i] - atr14_buf[i];
      sum += diff_buf[i];
   }

   double mean = sum / (double)InpZScoreWindow;
   double sq_diff = 0.0;
   for(int i = 0; i < InpZScoreWindow; i++)
      sq_diff += MathPow(diff_buf[i] - mean, 2.0);

   double stdev = MathSqrt(sq_diff / (double)InpZScoreWindow);
   out_zscore = (stdev > 0.0) ? (diff_buf[0] - mean) / stdev : 0.0;

   if(out_zscore > InpZScoreThreshold)  return(REGIME_HIGH);
   if(out_zscore < -InpZScoreThreshold) return(REGIME_LOW);
   return(REGIME_MEDIUM);
}

//+------------------------------------------------------------------+
//| BUCLE PRINCIPAL DE EJECUCION (OnTick)                            |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Guarda de Calentamiento de Datos D1
   int d1_bars = Bars(_Symbol, PERIOD_D1);
   if(d1_bars < (InpSlowAtrPeriod + InpZScoreWindow))
   {
      Comment(StringFormat("[WARMUP] Esperando historial D1 (%d/%d barras)...", d1_bars, InpSlowAtrPeriod + InpZScoreWindow));
      return;
   }

   double years_d1 = (double)d1_bars / 252.0;
   double z_score = 0.0, atr5_d1 = 0.0, atr14_d1 = 0.0;
   ENUM_VOL_REGIME vol_regime = CalculateDailyVolatilityZScore(z_score, atr5_d1, atr14_d1);

   // 2. Actualizacion de HUD Neutro en Pantalla
   string history_badge = (years_d1 >= 5.0) ? StringFormat("%.1f Anos (%d D1) [OK]", years_d1, d1_bars) :
                                             StringFormat("%.1f Anos [ALERTA: < 5 ANOS]", years_d1);
   string regime_str = (vol_regime == REGIME_HIGH) ? "ALTA (EXPANSION)" :
                       (vol_regime == REGIME_LOW)  ? "BAJA (COMPRESION)" : "MEDIA (ESTACIONARIA)";
   string gap_str = (g_gap_direction == GAP_UP) ? "ALCISTA" : (g_gap_direction == GAP_DOWN) ? "BAJISTA" : "SIN GAP VALIDO";

   string hud_text = StringFormat("--- %s ---\n"
                                  "Historial D1: %s\n"
                                  "Regimen Volatilidad: %s (Z=%.2f)\n"
                                  "Gap de Hoy: %s (%.5f)\n"
                                  "ATR D1: ATR5=%.5f | ATR14=%.5f\n"
                                  "Triple Barrera: B1=+%.1fx ATR_D1 | B2=-%.1fx ATR | B3=%db\n"
                                  "Estado: OPERATIVO",
                                  InpStrategyID, history_badge, regime_str, z_score, gap_str, g_gap_value, atr5_d1, atr14_d1,
                                  InpProfitMultiplier, InpStopMultiplier, InpMaxHoldingBars);
   Comment(hud_text);

   // 3. Gestion de Posiciones Abiertas (Barrera 3: Time-Stop manual; B1/B2 via SL/TP nativos)
   if(PositionsTotal() > 0)
   {
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         ulong ticket = PositionGetTicket(i);
         if(ticket > 0 && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         {
            datetime pos_time = (datetime)PositionGetInteger(POSITION_TIME);
            int bars_held = iBarShift(_Symbol, PERIOD_CURRENT, pos_time);

            if(bars_held >= InpMaxHoldingBars)
            {
               g_trade.PositionClose(ticket);
               PrintFormat("{\"event\":\"EXIT_B3_TIME\", \"ticket\":%d, \"bars_held\":%d, \"time\":\"%s\"}",
                           ticket, bars_held, TimeToString(TimeCurrent()));
            }
         }
      }
   }

   // 4. Evaluacion Sincronizada al Cierre de Barra M15 (IsNewBar)
   if(!g_bar_detector_m15.IsNewBar(PERIOD_CURRENT)) return;

   // 5. Deteccion de la Vela de Apertura de Sesion (Gap + Confirmacion en un solo paso)
   datetime bar_time = iTime(_Symbol, PERIOD_CURRENT, 1); // vela M15 recien cerrada
   MqlDateTime dt;
   TimeToStruct(bar_time, dt);
   datetime day_start = bar_time - (dt.hour * 3600 + dt.min * 60 + dt.sec);

   bool is_session_open_bar = (dt.hour == InpSessionStartHour && dt.min == InpSessionStartMin);
   if(!is_session_open_bar || day_start == g_last_processed_day) return;

   g_last_processed_day = day_start; // Solo se evalua 1 vez por sesion

   // Recalculo del Gap de Apertura: Open_hoy - Close_dia_previo, vs k_gap * ATR_D(14)
   double today_open = iOpen(_Symbol, PERIOD_D1, 0);
   double prev_close = iClose(_Symbol, PERIOD_D1, 1);
   g_session_open = today_open;
   g_gap_value    = today_open - prev_close;

   if(g_gap_value >= (InpGapThresholdATR * atr14_d1))
      g_gap_direction = GAP_UP;
   else if(g_gap_value <= -(InpGapThresholdATR * atr14_d1))
      g_gap_direction = GAP_DOWN;
   else
      g_gap_direction = GAP_NONE;

   if(PositionsTotal() > 0) return;              // Solo operamos si estamos flat
   if(vol_regime != REGIME_HIGH) return;          // Filtro de Regimen: Z-Score Alto
   if(g_gap_direction == GAP_NONE) return;

   double c1 = iClose(_Symbol, PERIOD_CURRENT, 1);
   double h1 = iHigh(_Symbol, PERIOD_CURRENT, 1);
   double l1 = iLow(_Symbol, PERIOD_CURRENT, 1);
   double bar_range = h1 - l1;
   if(bar_range <= 0) return;

   double atr_m15[];
   ArraySetAsSeries(atr_m15, true);
   CopyBuffer(g_handle_atr_m15, 0, 1, 1, atr_m15);

   // Condicion de Confirmacion Alcista (Gap_UP + cierre en la mitad superior del rango)
   if(g_gap_direction == GAP_UP && c1 > g_session_open && c1 >= (l1 + InpMaxRetracePct * bar_range))
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = ask - (InpStopMultiplier * atr_m15[0]);
      double tp  = ask + (InpProfitMultiplier * atr14_d1); // B1: Take Profit anclado a ATR_D1(14)

      if(g_trade.Buy(InpLotSize, _Symbol, ask, sl, tp, InpStrategyID))
         PrintFormat("{\"event\":\"ENTRY_BUY\", \"strategy_id\":\"%s\", \"price\":%.5f, \"gap\":%.5f, \"z_vol\":%.2f, \"tp_d1\":%.5f, \"sl\":%.5f}",
                     InpStrategyID, ask, g_gap_value, z_score, tp, sl);
   }
   // Condicion de Confirmacion Bajista (Gap_DOWN + cierre en la mitad inferior del rango)
   else if(g_gap_direction == GAP_DOWN && c1 < g_session_open && c1 <= (h1 - InpMaxRetracePct * bar_range))
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = bid + (InpStopMultiplier * atr_m15[0]);
      double tp  = bid - (InpProfitMultiplier * atr14_d1); // B1: Take Profit anclado a ATR_D1(14)

      if(g_trade.Sell(InpLotSize, _Symbol, bid, sl, tp, InpStrategyID))
         PrintFormat("{\"event\":\"ENTRY_SELL\", \"strategy_id\":\"%s\", \"price\":%.5f, \"gap\":%.5f, \"z_vol\":%.2f, \"tp_d1\":%.5f, \"sl\":%.5f}",
                     InpStrategyID, bid, g_gap_value, z_score, tp, sl);
   }
}
//+------------------------------------------------------------------+
