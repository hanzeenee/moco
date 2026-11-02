// MOCONIX native startup authorization, protocol 1. No trading strategy.
#ifndef MOCONIX_ACCOUNT_LICENSE_MQH
#define MOCONIX_ACCOUNT_LICENSE_MQH

class CMoconixAccountLicense
{
private:
   bool   m_authorized;
   long   m_login;
   string m_server;

   string Quote(const string value)
   {
      string escaped = value;
      StringReplace(escaped, "\\", "\\\\");
      StringReplace(escaped, "\"", "\\\"");
      StringReplace(escaped, "\r", "\\r");
      StringReplace(escaped, "\n", "\\n");
      StringReplace(escaped, "\t", "\\t");
      return "\"" + escaped + "\"";
   }

   bool Fail(const string message)
   {
      m_authorized = false;
      m_login = 0;
      m_server = "";
      Print("MOCONIX: ", message);
      Alert("MOCONIX: ", message);
      return false;
   }

public:
   CMoconixAccountLicense(void) : m_authorized(false), m_login(0), m_server("") {}

   // Call once from OnInit, before any strategy initialization or trade action.
   bool Authorize(const string product)
   {
      m_authorized = false;
      m_login = 0;
      m_server = "";
      if(MQLInfoInteger(MQL_TESTER))
         return Fail("온라인 인증 EA는 전략 테스터를 지원하지 않습니다. Online licensing is unavailable in Strategy Tester.");

      const long login = AccountInfoInteger(ACCOUNT_LOGIN);
      const string server = AccountInfoString(ACCOUNT_SERVER);
      if(login <= 0 || StringLen(server) == 0)
         return Fail("MT5 거래 계좌에 로그인해 주세요. Sign in to your MT5 trading account.");

      // Nonce binds this response to this initialization; it is not a password.
      const string nonce = StringFormat("%08X%08X%08X%08X", (uint)GetTickCount(),
                                       (uint)GetMicrosecondCount(), (uint)TimeLocal(), (uint)ChartID());
      const string identity = "\"account_number\":" + Quote((string)login)
                            + ",\"server\":" + Quote(server)
                            + ",\"product\":" + Quote(product)
                            + ",\"nonce\":" + Quote(nonce);
      const string payload = "{\"protocol\":1," + identity + "}";
      char request[], response[];
      const int copied = StringToCharArray(payload, request, 0, WHOLE_ARRAY, CP_UTF8);
      if(copied <= 1)
         return Fail("인증 요청을 만들 수 없습니다. Could not prepare the license request.");
      ArrayResize(request, copied - 1); // Exclude the trailing NUL from HTTP body.
      string response_headers;
      ResetLastError();
      const int status = WebRequest("POST", "https://moconix.com/api/licenses/check/",
                                   "Content-Type: application/json\r\nAccept: application/json\r\n",
                                   5000, request, response, response_headers);
      const int error = GetLastError();
      if(status == -1)
      {
         Print("MOCONIX WebRequest error: ", error);
         return Fail("인증 서버 연결 실패. MT5 WebRequest 허용 URL에 https://moconix.com 을 추가하고 인터넷 연결을 확인해 주세요. License connection failed; allow https://moconix.com in MT5 WebRequest settings.");
      }
      if(status != 200)
      {
         Print("MOCONIX license HTTP status: ", status);
         if(status == 403)
            return Fail("허용된 계좌·서버·EA인지 관리자에게 확인해 주세요. This account, server or EA is not authorized.");
         return Fail("인증 서버가 요청을 처리하지 못했습니다. 잠시 후 다시 적용해 주세요. License service unavailable; attach the EA again later.");
      }
      if(ArraySize(response) > 2048)
         return Fail("잘못된 인증 응답입니다. Invalid license response.");
      // Compare every field, not an unbound substring such as 'allowed:true'.
      const string expected = "{\"protocol\":1,\"allowed\":true," + identity + "}";
      const string received = CharArrayToString(response, 0, ArraySize(response), CP_UTF8);
      if(received != expected || AccountInfoInteger(ACCOUNT_LOGIN) != login
         || AccountInfoString(ACCOUNT_SERVER) != server)
         return Fail("계좌 또는 인증 응답이 일치하지 않습니다. License response or current account does not match.");
      m_login = login;
      m_server = server;
      m_authorized = true;
      Print("MOCONIX: 시작 인증 완료. Startup authorization complete.");
      return true;
   }

   // Memory-only guard: no WebRequest, timers, disk or cached cross-run grants.
   bool IsCurrentAccountAuthorized(void)
   {
      return m_authorized && AccountInfoInteger(ACCOUNT_LOGIN) == m_login
             && AccountInfoString(ACCOUNT_SERVER) == m_server;
   }
};

#endif
