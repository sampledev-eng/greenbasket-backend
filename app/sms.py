import os
import base64
import urllib.parse
import urllib.request

class SMSProvider:
    def send_sms(self, to: str, message: str) -> None:
        raise NotImplementedError

class TwilioProvider(SMSProvider):
    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_ = os.getenv("TWILIO_FROM")

    def send_sms(self, to: str, message: str) -> None:
        if not all([self.sid, self.token, self.from_]):
            print("Twilio credentials not set")
            return
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json"
        data = urllib.parse.urlencode({"To": to, "From": self.from_, "Body": message}).encode()
        req = urllib.request.Request(url, data=data)
        auth = base64.b64encode(f"{self.sid}:{self.token}".encode()).decode()
        req.add_header("Authorization", f"Basic {auth}")
        try:
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Twilio send failed: {e}")

class NexmoProvider(SMSProvider):
    def __init__(self):
        self.key = os.getenv("NEXMO_KEY")
        self.secret = os.getenv("NEXMO_SECRET")
        self.from_ = os.getenv("NEXMO_FROM", "GreenBasket")

    def send_sms(self, to: str, message: str) -> None:
        if not self.key or not self.secret:
            print("Nexmo credentials not set")
            return
        url = "https://rest.nexmo.com/sms/json"
        data = urllib.parse.urlencode({
            "api_key": self.key,
            "api_secret": self.secret,
            "to": to,
            "from": self.from_,
            "text": message,
        }).encode()
        try:
            urllib.request.urlopen(url, data=data)
        except Exception as e:
            print(f"Nexmo send failed: {e}")

def get_sms_driver() -> SMSProvider:
    provider = os.getenv("SMS_PROVIDER", "twilio").lower()
    if provider == "nexmo":
        return NexmoProvider()
    return TwilioProvider()
