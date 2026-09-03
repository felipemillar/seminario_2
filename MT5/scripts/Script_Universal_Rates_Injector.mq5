//+------------------------------------------------------------------+
//|                             Script_Universal_Rates_Injector.mq5 |
//|                                  Copyright 2026, QRT Solutions   |
//|                    https://github.com/felipemillar/seminario_2   |
//+------------------------------------------------------------------+
#property copyright "QRT Solutions"
#property link      "https://github.com/felipemillar/seminario_2"
#property version   "1.00"
#property script_show_inputs

// ==============================================================================
// PARÁMETROS DE CONFIGURACIÓN DEL SCRIPT
// ==============================================================================
input group "=== 1. Identificación del Símbolo Personalizado ==="
input string InpSymbolName   = "CUSTOM_ASSET_M5";         // Nombre del Símbolo Destino en MT5
input string InpBaseClone    = "US100";                   // Activo Base para clonar propiedades (US100/XAUUSD/BTCUSD)
input string InpGroup        = "Custom\\Quantitative";    // Jerarquía en Observación del Mercado
input int    InpDigits       = 2;                         // Dígitos decimales de precisión
input double InpPoint        = 0.01;                      // Tamaño del punto flotante (Point)

input group "=== 2. Archivo de Datos en MQL5/Files ==="
input string InpFileName     = "data_MT5.csv";            // Nombre del archivo CSV en MQL5/Files

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("[INICIO] Pipeline Universal de Inyección Cuantitativa");
   Print("[INFO] Símbolo objetivo: ", InpSymbolName, " | Archivo origen: MQL5/Files/", InpFileName);

   // ---------------------------------------------------------------------------
   // PASO 1: CREAR SÍMBOLO PERSONALIZADO SI NO EXISTE
   // ---------------------------------------------------------------------------
   if(!SymbolInfoInteger(InpSymbolName, SYMBOL_EXIST))
   {
      Print("[PASO 1] El símbolo no existe. Clonando propiedades desde ", InpBaseClone, "...");
      
      string base = InpBaseClone;
      // Detección de fallbacks si el símbolo del broker tiene sufijo
      if(!SymbolInfoInteger(base, SYMBOL_EXIST))
      {
         string candidates[] = {"US100", "USTEC", "NAS100", "XAUUSD", "GOLD", "BTCUSD", "EURUSD"};
         for(int i = 0; i < ArraySize(candidates); i++)
         {
            if(SymbolInfoInteger(candidates[i], SYMBOL_EXIST))
            {
               base = candidates[i];
               break;
            }
         }
      }

      ResetLastError();
      if(!CustomSymbolCreate(InpSymbolName, InpGroup, base))
      {
         Print("[ERROR] Falló CustomSymbolCreate para ", InpSymbolName, ". Error: ", GetLastError());
         return;
      }
      Print("[OK] Símbolo personalizado creado con éxito clonando de: ", base);
   }
   else
   {
      Print("[INFO] Símbolo ", InpSymbolName, " ya existe en la terminal.");
   }

   // Ajustar metadatos descriptivos
   CustomSymbolSetString(InpSymbolName, SYMBOL_DESCRIPTION, "Activo Cuantitativo Personalizado (Data Externa)");
   CustomSymbolSetInteger(InpSymbolName, SYMBOL_DIGITS, InpDigits);
   CustomSymbolSetDouble(InpSymbolName, SYMBOL_POINT, InpPoint);
   SymbolSelect(InpSymbolName, true);

   // ---------------------------------------------------------------------------
   // PASO 2: LECTURA Y PARSEO DEL ARCHIVO CSV DESDE MQL5/Files
   // ---------------------------------------------------------------------------
   int handle = FileOpen(InpFileName, FILE_READ | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
   {
      Print("[ERROR] No se pudo abrir MQL5/Files/", InpFileName, ". Código de error: ", GetLastError());
      Print("[AYUDA] Asegúrate de que el archivo exista en la carpeta MQL5/Files de tu terminal.");
      return;
   }

   // Descartar encabezado
   string header = FileReadString(handle);
   Print("[INFO] Encabezado CSV: ", header);

   MqlRates rates[];
   ArrayResize(rates, 500000);
   int count = 0;

   while(!FileIsEnding(handle))
   {
      string line = FileReadString(handle);
      if(StringLen(line) < 10) 
         continue;

      string parts[];
      int n = StringSplit(line, ',', parts);
      if(n < 6) 
         continue;

      // parts[0] = "YYYY.MM.DD", parts[1] = "HH:MM"
      string ts_str = parts[0] + " " + parts[1];
      datetime t = StringToTime(ts_str);
      if(t <= 0) 
         continue;

      rates[count].time        = t;
      rates[count].open        = StringToDouble(parts[2]);
      rates[count].high        = StringToDouble(parts[3]);
      rates[count].low         = StringToDouble(parts[4]);
      rates[count].close       = StringToDouble(parts[5]);
      rates[count].tick_volume = (n > 6) ? (long)StringToInteger(parts[6]) : 100;
      rates[count].real_volume = (n > 7) ? (long)StringToInteger(parts[7]) : rates[count].tick_volume;
      rates[count].spread      = 10;

      count++;
      if(count >= ArraySize(rates))
         ArrayResize(rates, count + 100000);
   }

   FileClose(handle);
   ArrayResize(rates, count);
   Print("[OK] Lectura finalizada: ", count, " barras parseadas.");

   if(count == 0)
   {
      Print("[ERROR] No se encontraron registros válidos para importar.");
      return;
   }

   // ---------------------------------------------------------------------------
   // PASO 3: INYECCIÓN DIRECTA EN LA BASE DE DATOS DE MT5
   // ---------------------------------------------------------------------------
   Print("[PASO 3] Inyectando ", count, " barras en ", InpSymbolName, "...");
   ResetLastError();

   int res = CustomRatesReplace(InpSymbolName, rates[0].time, rates[count - 1].time, rates, count);
   if(res < 0)
   {
      Print("[WARN] CustomRatesReplace arrojó código ", GetLastError(), ". Probando CustomRatesUpdate...");
      ResetLastError();
      res = CustomRatesUpdate(InpSymbolName, rates, count);
   }

   if(res >= 0)
   {
      Print("==================================================================");
      Print("[ÉXITO TOTAL] Se inyectaron ", res, " barras en ", InpSymbolName);
      Print("[INFO] Rango histórico: ", TimeToString(rates[0].time), " hasta ", TimeToString(rates[count - 1].time));
      Print("==================================================================");
      ChartSetSymbolPeriod(0, InpSymbolName, PERIOD_CURRENT);
      ChartRedraw(0);
   }
   else
   {
      Print("[ERROR] Falló la inyección en ", InpSymbolName, ". Código de error: ", GetLastError());
   }
}
