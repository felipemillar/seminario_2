//+------------------------------------------------------------------+
//|                               Script_Create_NQ_Custom_Symbol.mq5 |
//|                                  Copyright 2026, QRT Solutions   |
//|                    https://github.com/felipemillar/seminario_2   |
//+------------------------------------------------------------------+
#property copyright "QRT Solutions"
#property link      "https://github.com/felipemillar/seminario_2"
#property version   "1.00"
#property script_show_inputs

input string InpCustomSymbol = "CUSTOM_NQ_M5";     // Nombre del Simbolo Personalizado
input string InpBaseSymbol   = "US100";             // Simbolo Base para clonar (US100 / USTEC / NAS100)
input string InpGroup        = "Custom\\Futures";   // Grupo en Observacion del Mercado

//+------------------------------------------------------------------+
//| Script program execution function                                |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("[INICIO] Configurando Custom Symbol para NQ M5: ", InpCustomSymbol);
   
   // Si el simbolo ya existe, avisar
   if(SymbolInfoInteger(InpCustomSymbol, SYMBOL_EXIST))
   {
      Print("[INFO] El simbolo ", InpCustomSymbol, " ya existe en la terminal.");
   }
   else
   {
      // Buscar el mejor simbolo base para clonar propiedades financieras
      string base = InpBaseSymbol;
      if(!SymbolInfoInteger(base, SYMBOL_EXIST))
      {
         if(SymbolInfoInteger("USTEC", SYMBOL_EXIST)) base = "USTEC";
         else if(SymbolInfoInteger("NAS100", SYMBOL_EXIST)) base = "NAS100";
         else if(SymbolInfoInteger("US100.cash", SYMBOL_EXIST)) base = "US100.cash";
         else if(SymbolInfoInteger("NQ", SYMBOL_EXIST)) base = "NQ";
         else if(SymbolInfoInteger("BTCUSD", SYMBOL_EXIST)) base = "BTCUSD"; // Fallback
      }
      
      ResetLastError();
      if(!CustomSymbolCreate(InpCustomSymbol, InpGroup, base))
      {
         Print("[ERROR] No se pudo crear el simbolo personalizado ", InpCustomSymbol, ". Error: ", GetLastError());
         return;
      }
      Print("[OK] Simbolo ", InpCustomSymbol, " creado con exito clonando propiedades de: ", base);
   }
   
   // Ajustar propiedades descriptivas e institucionales
   CustomSymbolSetString(InpCustomSymbol, SYMBOL_DESCRIPTION, "Nasdaq 100 E-mini Futuros M5 (Data Externa)");
   CustomSymbolSetInteger(InpCustomSymbol, SYMBOL_DIGITS, 2);
   CustomSymbolSetDouble(InpCustomSymbol, SYMBOL_POINT, 0.01);
   
   // Asegurar visibilidad en Observacion del Mercado (Market Watch)
   SymbolSelect(InpCustomSymbol, true);
   Print("[OK] Simbolo ", InpCustomSymbol, " visible y activado en Market Watch.");
   Print("[LISTO] Ahora puedes importar las barras en Ctrl + U -> Barras -> M5 -> Importar Barras.");
}
