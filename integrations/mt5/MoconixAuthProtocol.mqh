// MOCONIX indicator authorization: terminal-local mailboxes + RSA-PSS/SHA-256.
// Public verification code only. No trading calls, DLLs or embedded private key.
#ifndef MOCONIX_AUTH_PROTOCOL_MQH
#define MOCONIX_AUTH_PROTOCOL_MQH
#define MOCO_AUTH_REQUEST 4172
#define MOCO_AUTH_REPLY 4173
#define MOCO_RSA_LIMBS 64
const string MOCO_BRIDGE_NAME = "MOCONIX_AuthBridge";
const string MOCO_INDICATOR_KEY_N = "BF56C6E0972BE8F350835C67E5D89DB654D8B364E48A0B474B8B626965EF3A6620D74565B4E19A72D984D37077107097D87F8AD2E687815159504D6FEA3C90C4A8B3F0D1A9061A6F2D0EB37A6CD94C55C997871FF0216F013EC1029BBD5642ED70D6C5E2679E6FFEBACA432A388EA0C477DB2AB2136EBEAF2463AD86BA70AC01DCF7A8D2180A6A621C3EC3646D0D3203328AA84671320AC26C72F1EFC1D4860590B4F1683E0E6662A0C7583B0266AD3AFEC005AE0A57EC1101FF77BFA3EF5C04C3DE21D7A1FC49D74A5E252DE39E92280C9E681A6E96FAFC0463D5313F5927A02D956031CEB27B1AB0075F4254E7A42D19D4B6E49685D36BCB5BB7D3F1E4E559";

bool MocoHex(const string hex, uchar &bytes[])
{
   const int length=StringLen(hex);
   if(length==0 || length%2!=0) return false;
   ArrayResize(bytes,length/2);
   for(int i=0;i<length;i++)
   {
      const ushort c=StringGetCharacter(hex,i);
      int value=-1;
      if(c>='0' && c<='9') value=(int)c-'0';
      else if(c>='A' && c<='F') value=(int)c-'A'+10;
      else if(c>='a' && c<='f') value=(int)c-'a'+10;
      if(value<0) return false;
      if(i%2==0) bytes[i/2]=(uchar)(value<<4);
      else bytes[i/2]|=(uchar)value;
   }
   return true;
}

string MocoHexString(const uchar &bytes[])
{
   string hex="";
   for(int i=0;i<ArraySize(bytes);i++) hex+=StringFormat("%02X",bytes[i]);
   return hex;
}

bool MocoSha256(const uchar &bytes[],uchar &digest[])
{
   uchar key[];
   return CryptEncode(CRYPT_HASH_SHA256,bytes,key,digest)==32;
}

bool MocoStringBytes(const string text,uchar &bytes[])
{
   int count=StringToCharArray(text,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(count<1) return false;
   return ArrayResize(bytes,count-1)>=0;
}

int MocoBigCompare(const uint &left[],const uint &right[])
{
   for(int i=MOCO_RSA_LIMBS-1;i>=0;i--)
   {
      if(left[i]>right[i]) return 1;
      if(left[i]<right[i]) return -1;
   }
   return 0;
}

void MocoBigAddMod(uint &target[],const uint &other[],const uint &modulus[])
{
   ulong carry=0;
   for(int i=0;i<MOCO_RSA_LIMBS;i++)
   {
      const ulong sum=(ulong)target[i]+(ulong)other[i]+carry;
      target[i]=(uint)sum;
      carry=sum>>32;
   }
   if(carry!=0 || MocoBigCompare(target,modulus)>=0)
   {
      ulong borrow=0;
      for(int i=0;i<MOCO_RSA_LIMBS;i++)
      {
         const ulong before=(ulong)target[i];
         const ulong sub=(ulong)modulus[i]+borrow;
         target[i]=(uint)(before-sub);
         borrow=(before<sub)?1:0;
      }
   }
}

void MocoBigMultiplyMod(const uint &left[],const uint &right[],const uint &modulus[],uint &output[])
{
   uint result[MOCO_RSA_LIMBS],factor[MOCO_RSA_LIMBS];
   ArrayInitialize(result,0);
   ArrayCopy(factor,left);
   for(int limb=0;limb<MOCO_RSA_LIMBS;limb++)
   {
      uint bits=right[limb];
      for(int bit=0;bit<32;bit++)
      {
         if((bits&1)!=0) MocoBigAddMod(result,factor,modulus);
         bits>>=1;
         if(limb!=MOCO_RSA_LIMBS-1 || bit!=31) MocoBigAddMod(factor,factor,modulus);
      }
   }
   ArrayCopy(output,result);
}

bool MocoBigFromHex(const string hex,uint &number[])
{
   uchar bytes[];
   if(StringLen(hex)!=512 || !MocoHex(hex,bytes)) return false;
   ArrayInitialize(number,0);
   for(int i=0;i<256;i++)
      number[(255-i)/4]|=((uint)bytes[i])<<(((255-i)%4)*8);
   return true;
}

// Fixed RSA-2048 / e=65537 / PSS-SHA256 / 32-byte salt verification.
// Complete PSS padding, MGF1, trailer and digest are checked, not a substring.
bool MocoVerifySignature(const string message,const string signature_hex)
{
   uint modulus[MOCO_RSA_LIMBS],base[MOCO_RSA_LIMBS],value[MOCO_RSA_LIMBS],next[MOCO_RSA_LIMBS];
   if(!MocoBigFromHex(MOCO_INDICATOR_KEY_N,modulus) || !MocoBigFromHex(signature_hex,base)) return false;
   if(MocoBigCompare(base,modulus)>=0) return false;
   ArrayCopy(value,base);
   for(int i=0;i<16;i++)
   {
      MocoBigMultiplyMod(value,value,modulus,next);
      ArrayCopy(value,next);
   }
   MocoBigMultiplyMod(value,base,modulus,next);
   uchar encoded[256];
   for(int i=0;i<256;i++) encoded[i]=(uchar)(next[(255-i)/4]>>(((255-i)%4)*8));
   if(encoded[255]!=0xBC || (encoded[0]&0x80)!=0) return false;
   uchar h[32],mask_input[36],mask[],hash[];
   for(int i=0;i<32;i++) { h[i]=encoded[223+i]; mask_input[i]=h[i]; }
   ArrayResize(mask,223);
   for(int counter=0;counter<7;counter++)
   {
      mask_input[32]=0; mask_input[33]=0; mask_input[34]=0; mask_input[35]=(uchar)counter;
      if(!MocoSha256(mask_input,hash)) return false;
      for(int i=0;i<32 && counter*32+i<223;i++) mask[counter*32+i]=hash[i];
   }
   uchar db[223];
   for(int i=0;i<223;i++) db[i]=encoded[i]^mask[i];
   db[0]&=0x7F;
   for(int i=0;i<190;i++) if(db[i]!=0) return false;
   if(db[190]!=1) return false;
   uchar content[],message_hash[],final_input[72],final_hash[];
   if(!MocoStringBytes(message,content) || !MocoSha256(content,message_hash)) return false;
   ArrayInitialize(final_input,0);
   for(int i=0;i<32;i++) { final_input[8+i]=message_hash[i]; final_input[40+i]=db[191+i]; }
   if(!MocoSha256(final_input,final_hash)) return false;
   int difference=0;
   for(int i=0;i<32;i++) difference|=(int)(final_hash[i]^h[i]);
   return difference==0;
}

bool MocoNonceValid(const string nonce)
{
   uchar bytes[];
   return StringLen(nonce)==32 && MocoHex(nonce,bytes);
}

long MocoNonceSequence()
{
   const string name="MOCONIX_AUTH_NONCE_SEQ";
   if(!GlobalVariableCheck(name) && !GlobalVariableTemp(name) && !GlobalVariableCheck(name)) return -1;
   for(int attempt=0;attempt<100;attempt++)
   {
      const double previous=GlobalVariableGet(name);
      if(previous<0 || previous>=9007199254740000.0) return -1;
      if(GlobalVariableSetOnCondition(name,previous+1.0,previous)) return (long)(previous+1.0);
   }
   return -1;
}

string MocoAuthMessage(const long login,const string server,const string product,const string nonce)
{
   return "MOCONIX-INDICATOR-1|"+(string)login+"|"+server+"|"+product+"|"+nonce;
}

bool MocoVerifyReply(const string reply,const string expected)
{
   const int newline=StringFind(reply,"\n");
   if(newline<0 || StringFind(reply,"\n",newline+1)>=0) return false;
   return StringSubstr(reply,0,newline)==expected
          && MocoVerifySignature(expected,StringSubstr(reply,newline+1));
}

string MocoAuthPath(const string nonce,const string extension)
{
   return "MoconixAuth\\"+nonce+"."+extension;
}

bool MocoWriteText(const string path,const string text)
{
   FolderCreate("MoconixAuth");
   const string temporary=path+".tmp";
   int handle=FileOpen(temporary,FILE_WRITE|FILE_TXT|FILE_ANSI,'\t',CP_UTF8);
   if(handle==INVALID_HANDLE) return false;
   const uint written=FileWriteString(handle,text);
   FileFlush(handle);
   FileClose(handle);
   if(written==0 || !FileMove(temporary,0,path,FILE_REWRITE)) { FileDelete(temporary); return false; }
   return true;
}

bool MocoReadText(const string path,string &text,const int maximum=2048)
{
   text="";
   int handle=FileOpen(path,FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ,'\t',CP_UTF8);
   if(handle==INVALID_HANDLE) return false;
   if(FileSize(handle)>(ulong)maximum) { FileClose(handle); return false; }
   while(!FileIsEnding(handle))
   {
      const string line=FileReadString(handle);
      if(text!="") text+="\n";
      text+=line;
   }
   FileClose(handle);
   return text!="";
}

long MocoFindBridge()
{
   for(long chart=ChartFirst();chart>=0;chart=ChartNext(chart))
      if(ChartGetString(chart,CHART_EXPERT_NAME)==MOCO_BRIDGE_NAME) return chart;
   return -1;
}

#endif
