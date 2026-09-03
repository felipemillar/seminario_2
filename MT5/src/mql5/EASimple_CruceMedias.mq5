//+------------------------------------------------------------------+
//|                                        EASimple_CruceMedias.mq5  |
//|                                  Copyright 2026, Felipe Millar   |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, Felipe Millar"
#property link        "https://www.mql5.com"
#property version     "1.00"
#property description "Estrategia simple de prueba: Cruce de Medias Móviles (EMA)"

//--- Inclusión de librerías estándar para gestión de órdenes
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

//--- Parámetros de Entrada (Configurables en MT5 / Strategy Tester)
input group "=== Parámetros de Trading ==="
input double   InpLotSize         = 0.01;        // Volumen de Lote
input int      InpStopLossPoints  = 200;         // Stop Loss en Puntos (0 = Desactivado)
input int      InpTakeProfitPoints= 400;         // Take Profit en Puntos (0 = Desactivado)
input ulong    InpMagicNumber     = 20260902;    // Identificador único (Magic Number)

input group "=== Configuración de Medias Móviles ==="
input int               InpFastPeriod   = 9;            // Periodo Media Rápida
input int               InpSlowPeriod   = 21;           // Periodo Media Lenta
input ENUM_MA_METHOD    InpMAMethod     = MODE_EMA;     // Tipo de Media (EMA, SMA, etc.)
input ENUM_APPLIED_PRICE InpAppliedPrice = PRICE_CLOSE;  // Precio Aplicado

//--- Objetos globales y manejadores
CTrade         trade;
CPositionInfo  posInfo;
int            handleFastMA = INVALID_HANDLE;
int            handleSlowMA = INVALID_HANDLE;
datetime       lastBarTime  = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Asignar el Magic Number a la instancia de trading
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);

   // Crear los indicadores de medias móviles
   handleFastMA = iMA(_Symbol, _Period, InpFastPeriod, 0, InpMAMethod, InpAppliedPrice);
   if(handleFastMA == INVALID_HANDLE)
   {
      Print("[ERROR] Error al crear indicador Media Rápida. Código: ", GetLastError());
      return(INIT_FAILED);
   }

   handleSlowMA = iMA(_Symbol, _Period, InpSlowPeriod, 0, InpMAMethod, InpAppliedPrice);
   if(handleSlowMA == INVALID_HANDLE)
   {
      Print("[ERROR] Error al crear indicador Media Lenta. Código: ", GetLastError());
      return(INIT_FAILED);
   }

   Print("[OK] EA Simple Cruce de Medias inicializado con éxito en ", _Symbol, " (", EnumToString(_Period), ")");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Liberar manejadores de indicadores
   if(handleFastMA != INVALID_HANDLE) IndicatorRelease(handleFastMA);
   if(handleSlowMA != INVALID_HANDLE) IndicatorRelease(handleSlowMA);
   Print("[STOP] EA Simple Cruce de Medias detenido. Razón: ", reason);
}

//+------------------------------------------------------------------+
//| Función auxiliar: Verifica si hay una nueva barra cerrada        |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if(currentBarTime != lastBarTime)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Función auxiliar: Cuenta posiciones abiertas por este EA         |
//+------------------------------------------------------------------+
void GetCurrentPositions(int &buyCount, int &sellCount)
{
   buyCount  = 0;
   sellCount = 0;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i))
      {
         if(posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
         {
            if(posInfo.PositionType() == POSITION_TYPE_BUY)
               buyCount++;
            else if(posInfo.PositionType() == POSITION_TYPE_SELL)
               sellCount++;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Función auxiliar: Cierra posiciones de un tipo específico        |
//+------------------------------------------------------------------+
void ClosePositions(ENUM_POSITION_TYPE typeToClose)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i))
      {
         if(posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
         {
            if(posInfo.PositionType() == typeToClose)
            {
               trade.PositionClose(posInfo.Ticket());
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Operar únicamente al cierre de cada barra (evita ruido intratick)
   if(!IsNewBar()) return;

   // Arrays dinámicos para capturar los valores de las medias en orden serie
   double fastMA[];
   double slowMA[];
   ArraySetAsSeries(fastMA, true);
   ArraySetAsSeries(slowMA, true);

   // Copiar 2 barras cerradas: índice 1 (barra anterior) e índice 2 (ante-anterior)
   if(CopyBuffer(handleFastMA, 0, 1, 2, fastMA) < 2) return;
   if(CopyBuffer(handleSlowMA, 0, 1, 2, slowMA) < 2) return;

   // Lógica de cruce:
   // fastMA[0] = valor en barra 1 (recién cerrada)
   // fastMA[1] = valor en barra 2 (anterior)
   bool buySignal  = (fastMA[1] <= slowMA[1]) && (fastMA[0] > slowMA[0]);
   bool sellSignal = (fastMA[1] >= slowMA[1]) && (fastMA[0] < slowMA[0]);

   int currentBuys, currentSells;
   GetCurrentPositions(currentBuys, currentSells);

   // Precios actuales
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   int    digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);

   //--- SEÑAL DE COMPRA (Cruce Alcista)
   if(buySignal)
   {
      // Cerrar ventas abiertas si las hay
      if(currentSells > 0)
         ClosePositions(POSITION_TYPE_SELL);

      // Si no hay compra abierta, abrimos BUY
      if(currentBuys == 0)
      {
         double sl = (InpStopLossPoints > 0)   ? NormalizeDouble(ask - InpStopLossPoints * _Point, digits)   : 0.0;
         double tp = (InpTakeProfitPoints > 0) ? NormalizeDouble(ask + InpTakeProfitPoints * _Point, digits) : 0.0;

         if(trade.Buy(InpLotSize, _Symbol, ask, sl, tp, "EASimple Cruce Alcista"))
         {
            Print("[SIGNAL] Orden BUY ejecutada a ", ask, " | SL: ", sl, " | TP: ", tp);
         }
         else
         {
            Print("[ERROR] Error al enviar orden BUY: ", trade.ResultRetcodeDescription());
         }
      }
   }
   //--- SEÑAL DE VENTA (Cruce Bajista)
   else if(sellSignal)
   {
      // Cerrar compras abiertas si las hay
      if(currentBuys > 0)
         ClosePositions(POSITION_TYPE_BUY);

      // Si no hay venta abierta, abrimos SELL
      if(currentSells == 0)
      {
         double sl = (InpStopLossPoints > 0)   ? NormalizeDouble(bid + InpStopLossPoints * _Point, digits)   : 0.0;
         double tp = (InpTakeProfitPoints > 0) ? NormalizeDouble(bid - InpTakeProfitPoints * _Point, digits) : 0.0;

         if(trade.Sell(InpLotSize, _Symbol, bid, sl, tp, "EASimple Cruce Bajista"))
         {
            Print("[DOWN] Orden SELL ejecutada a ", bid, " | SL: ", sl, " | TP: ", tp);
         }
         else
         {
            Print("[ERROR] Error al enviar orden SELL: ", trade.ResultRetcodeDescription());
         }
      }
   }
}
//+------------------------------------------------------------------+
