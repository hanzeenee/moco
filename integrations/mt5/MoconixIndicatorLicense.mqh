#ifndef MOCONIX_INDICATOR_LICENSE_MQH
#define MOCONIX_INDICATOR_LICENSE_MQH
#include "MoconixAuthProtocol.mqh"

class CMoconixIndicatorLicense
{
private:
   bool m_authorized,m_sent,m_finished,m_transport_reported,m_transport_queued;
   long m_login;
   string m_server,m_product,m_nonce,m_expected,m_label;

   void Status(const string message,const color tint=clrGold)
   {
      if(ObjectFind(0,m_label)<0) ObjectCreate(0,m_label,OBJ_LABEL,0,0,0);
      ObjectSetInteger(0,m_label,OBJPROP_CORNER,CORNER_LEFT_UPPER);
      ObjectSetInteger(0,m_label,OBJPROP_XDISTANCE,12);
      ObjectSetInteger(0,m_label,OBJPROP_YDISTANCE,28);
      ObjectSetInteger(0,m_label,OBJPROP_COLOR,tint);
      ObjectSetInteger(0,m_label,OBJPROP_FONTSIZE,9);
      ObjectSetInteger(0,m_label,OBJPROP_SELECTABLE,false);
      ObjectSetInteger(0,m_label,OBJPROP_HIDDEN,true);
      ObjectSetString(0,m_label,OBJPROP_TEXT,"MOCONIX: "+message);
      ChartRedraw();
   }

   void WaitForTransport(const string operation,const int error)
   {
      if(m_transport_reported) return;
      m_transport_reported=true;
      Print("MOCONIX auth 1.02: ",operation,"; waiting and retrying local delivery. error=",error);
   }

   void CleanupFiles()
   {
      FileDelete(MocoAuthPath(m_nonce,"request"));
      FileDelete(MocoAuthPath(m_nonce,"reply"));
   }

   void Deny(const string reason)
   {
      m_authorized=false;
      m_finished=true;
      CleanupFiles();
      Status(reason,clrTomato);
      Print("MOCONIX: ",reason);
   }

public:
   CMoconixIndicatorLicense(void):m_authorized(false),m_sent(false),m_finished(false),m_transport_reported(false),m_transport_queued(false),m_login(0) {}

   bool Start(const string product)
   {
      m_authorized=false; m_sent=false; m_finished=false; m_transport_reported=false; m_transport_queued=false;
      m_login=AccountInfoInteger(ACCOUNT_LOGIN);
      m_server=AccountInfoString(ACCOUNT_SERVER);
      m_product=product;
      const long sequence=MocoNonceSequence();
      if(sequence<0) return false;
      const string seed=(string)m_login+"|"+m_server+"|"+product+"|"+(string)ChartID()+"|"+(string)(long)TimeLocal()+"|"+(string)GetTickCount64()+"|"+(string)GetMicrosecondCount()+"|"+(string)sequence;
      uchar bytes[],digest[];
      if(!MocoStringBytes(seed,bytes) || !MocoSha256(bytes,digest)) return false;
      m_nonce=StringSubstr(MocoHexString(digest),0,32);
      m_label="MOCONIX_AUTH_"+m_nonce;
      m_expected=MocoAuthMessage(m_login,m_server,m_product,m_nonce);
      if(MQLInfoInteger(MQL_TESTER) || m_login<=0 || m_server=="")
      {
         Deny("온라인 인증 계좌가 필요합니다 / Online authorization requires a trading account, outside Strategy Tester.");
         return false;
      }
      Print("MOCONIX auth 1.02: waiting for AuthBridge; local delivery retries enabled.");
      Status("인증 도우미 확인 중 / Waiting for AuthBridge");
      return true;
   }

   void Poll()
   {
      if(m_finished) return;
      if(AccountInfoInteger(ACCOUNT_LOGIN)!=m_login || AccountInfoString(ACCOUNT_SERVER)!=m_server)
      { Deny("계좌가 변경되었습니다 / Account changed; reattach the indicator."); return; }
      if(!m_sent)
      {
         const long bridge=MocoFindBridge();
         // Wait locally without a deadline. Do not contact the server until a helper exists.
         if(bridge<0) return;
         const string request=(string)m_login+"|"+m_server+"|"+m_product+"|"+m_nonce;
         ResetLastError();
         if(!MocoWriteText(MocoAuthPath(m_nonce,"request"),request))
         { WaitForTransport("request mailbox not ready",GetLastError()); return; }
         // This means published locally, not delivered or authorized. Never rewrite
         // it after the helper consumes it; consumption precedes the one HTTP check.
         m_sent=true;
      }
      const string request_path=MocoAuthPath(m_nonce,"request");
      if(FileIsExist(request_path))
      {
         const long bridge=MocoFindBridge();
         if(bridge>=0)
         {
            ResetLastError();
            if(!EventChartCustom(bridge,MOCO_AUTH_REQUEST,ChartID(),0,m_nonce))
               WaitForTransport("AuthBridge event queue not ready",GetLastError());
            else if(!m_transport_queued)
            {
               m_transport_queued=true;
               Status("등록 계좌 확인 중 / Checking registered account");
            }
         }
      }
      // An event accepted while the EA is attaching can be lost before its handler
      // is ready. Wake it again only while the same unconsumed request still exists.
      const string path=MocoAuthPath(m_nonce,"reply");
      if(!FileIsExist(path)) return;
      string reply;
      if(!MocoReadText(path,reply) || !MocoVerifyReply(reply,m_expected))
      { Deny("인증되지 않은 계좌 또는 응답 / Authorization denied or invalid response."); return; }
      if(AccountInfoInteger(ACCOUNT_LOGIN)!=m_login || AccountInfoString(ACCOUNT_SERVER)!=m_server)
      { Deny("계좌가 변경되었습니다 / Account changed."); return; }
      m_authorized=true; m_finished=true;
      CleanupFiles();
      ObjectDelete(0,m_label);
      Print("MOCONIX: 지표 시작 인증 완료 / Indicator startup authorization complete.");
      ChartRedraw();
   }

   bool Authorized()
   {
      if(m_authorized && (AccountInfoInteger(ACCOUNT_LOGIN)!=m_login || AccountInfoString(ACCOUNT_SERVER)!=m_server))
         Deny("계좌가 변경되었습니다 / Account changed; reattach the indicator.");
      return m_authorized;
   }
   bool Finished() { return m_finished; }
   void Stop() { CleanupFiles(); if(m_label!="") ObjectDelete(0,m_label); }
};
#endif
