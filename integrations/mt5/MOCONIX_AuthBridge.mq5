#property strict
#property version "1.00"
#property description "MOCONIX indicator authorization helper. No orders, DLLs or periodic server checks."
#include "MoconixAuthProtocol.mqh"

string MocoQuote(string value)
{
   StringReplace(value,"\\","\\\\"); StringReplace(value,"\"","\\\"");
   return "\""+value+"\"";
}

int OnInit()
{
   if(MQLInfoInteger(MQL_TESTER)) return INIT_FAILED;
   for(long chart=ChartFirst();chart>=0;chart=ChartNext(chart))
      if(chart!=ChartID() && ChartGetString(chart,CHART_EXPERT_NAME)==MOCO_BRIDGE_NAME)
      { Print("MOCONIX: AuthBridge는 터미널당 하나만 사용하세요 / Use one AuthBridge per terminal."); return INIT_FAILED; }
   Print("MOCONIX AuthBridge: 인증 요청 대기 / Ready. No trading operations or periodic HTTP requests.");
   return INIT_SUCCEEDED;
}

void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &nonce)
{
   if(id!=CHARTEVENT_CUSTOM+MOCO_AUTH_REQUEST || !MocoNonceValid(nonce)) return;
   const string request_path=MocoAuthPath(nonce,"request");
   string request,fields[];
   if(!MocoReadText(request_path,request,512) || StringSplit(request,'|',fields)!=4) return;
   const long login=AccountInfoInteger(ACCOUNT_LOGIN);
   const string server=AccountInfoString(ACCOUNT_SERVER);
   if(fields[0]!=(string)login || fields[1]!=server || fields[3]!=nonce || login<=0) return;
   // Delete before HTTP: duplicate events cannot trigger a second request.
   FileDelete(request_path);
   const string expected=MocoAuthMessage(login,server,fields[2],nonce);
   const string payload="{\"protocol\":2,\"account_number\":"+MocoQuote((string)login)
                        +",\"server\":"+MocoQuote(server)+",\"product\":"+MocoQuote(fields[2])
                        +",\"nonce\":"+MocoQuote(nonce)+"}";
   char data[],result[];
   int count=StringToCharArray(payload,data,0,WHOLE_ARRAY,CP_UTF8);
   if(count<=1) return;
   ArrayResize(data,count-1);
   string headers;
   ResetLastError();
   const int status=WebRequest("POST","https://moconix.com/api/licenses/indicator/",
                              "Content-Type: application/json\r\nAccept: text/plain\r\n",5000,data,result,headers);
   const int error=GetLastError();
   string response="ERROR|"+(string)status;
   if(status==200 && ArraySize(result)<=2048)
   {
      const string wire=CharArrayToString(result,0,ArraySize(result),CP_UTF8);
      // Cheap binding check here; the indicator independently verifies the signature.
      if(StringFind(wire,expected+"\n")==0 && StringLen(wire)==StringLen(expected)+1+512)
         response=wire;
   }
   if(AccountInfoInteger(ACCOUNT_LOGIN)!=login || AccountInfoString(ACCOUNT_SERVER)!=server)
      response="ERROR|ACCOUNT_CHANGED";
   if(status==-1) Print("MOCONIX AuthBridge: WebRequest error ",error,"; allow https://moconix.com in MT5 settings.");
   else if(status!=200) Print("MOCONIX AuthBridge: authorization HTTP ",status);
   if(MocoWriteText(MocoAuthPath(nonce,"reply"),response))
      EventChartCustom(lparam,MOCO_AUTH_REPLY,0,0,nonce);
}
