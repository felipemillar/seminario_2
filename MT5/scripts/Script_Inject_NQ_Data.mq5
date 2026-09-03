//+------------------------------------------------------------------+
//|                                        Script_Inject_NQ_Data.mq5 |
//|                                  Copyright 2026, QRT Solutions   |
//|                    https://github.com/felipemillar/seminario_2   |
//+------------------------------------------------------------------+
#property copyright "QRT Solutions"
#property link      "https://github.com/felipemillar/seminario_2"
#property version   "1.00"
#property script_show_inputs

input string InpSymbolName = "CUSTOM_NQ_M5";            // Simbolo de destino
input string InpFileName   = "NQ_5M_MT5_2020_2026.csv"; // Archivo CSV (en MQL5/Files)

//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("[INICIO] Iniciando inyeccion automatica en: ", InpSymbolName);
   Print("[INFO] Leyendo archivo desde MQL5/Files: ", InpFileName);
   
   int handle = FileOpen(InpFileName, FILE_READ | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
   {
      Print("[ERROR] No se pudo abrir el archivo ", InpFileName, " en MQL5/Files. Error: ", GetLastError());
      return;
   }
   
   // Leer linea de encabezado
   string header_line = FileReadString(handle);
   Print("[INFO] Encabezado detectado: ", header_line);
   
   MqlRates rates[];
   ArrayResize(rates, 500000);
   int count = 0;
   
   while(!FileIsEnding(handle))
   {
      string line = FileReadString(handle);
      if(StringLen(line) < 10) 
         continue;
      
      string parts[];
      int n_parts = StringSplit(line, ',', parts);
      if(n_parts < 6) 
         continue;
      
      // Formato: 2020.01.02, 00:00, Open, High, Low, Close, TickVol, Vol
      string time_str = parts[0] + " " + parts[1];
      datetime bar_time = StringToTime(time_str);
      if(bar_time <= 0)
         continue;
         
      rates[count].time        = bar_time;
      rates[count].open        = StringToDouble(parts[2]);
      rates[count].high        = StringToDouble(parts[3]);
      rates[count].low         = StringToDouble(parts[4]);
      rates[count].close       = StringToDouble(parts[5]);
      rates[count].tick_volume = (n_parts > 6) ? (long)StringToInteger(parts[6]) : 100;
      rates[count].real_volume = (n_parts > 7) ? (long)StringToInteger(parts[7]) : rates[count].tick_volume;
      rates[count].spread      = 10;
      
      count++;
      if(count >= ArraySize(rates))
         ArrayResize(rates, count + 100000);
   }
   
   FileClose(handle);
   ArrayResize(rates, count);
   Print("[OK] Lectura finalizada: ", count, " barras procesadas en memoria.");
   
   if(count == 0)
   {
      Print("[ERROR] No se obtuvieron barras validas del archivo.");
      return;
   }
   
   Print("[INFO] Inyectando en la base de datos de ", InpSymbolName, "...");
   ResetLastError();
   
   int updated = CustomRatesReplace(InpSymbolName, rates[0].time, rates[count - 1].time, rates, count);
   if(updated < 0)
   {
      Print("[WARN] CustomRatesReplace arrojo error ", GetLastError(), ". Probando CustomRatesUpdate...");
      ResetLastError();
      updated = CustomRatesUpdate(InpSymbolName, rates, count);
   }
   
   if(updated >= 0)
   {
      Print("[EXITO] Se inyectaron exitosamente ", updated, " barras M5 en ", InpSymbolName);
      Print("[INFO] Periodo: ", TimeToString(rates[0].time), " hasta ", TimeToString(rates[count - 1].time));
      ChartSetSymbolPeriod(0, InpSymbolName, PERIOD_M5);
      ChartRedraw(0);
   }
   else
   {
      Print("[ERROR] Fallo critico en CustomRatesUpdate. Codigo de error: ", GetLastError());
   }
}
