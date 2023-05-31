# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import cx_Oracle
import requests

from configparser import ConfigParser
import configparser

#Read config.ini file

config_file = 'config.ini'
config = configparser.ConfigParser()

try:
    config.read(config_file)
    print("File loaded successfully")
    config.sections()
    
except configparser.Error as e:
    print(f"Error reading file: {str(e)}")



#Get the password

# intent_greet = configread.get("intent_greet")
# intent_general = config.get("message","intent_general")
# intent_health_greet  = config.get("message","intent_health_greet")

intent_greet = "Apa kabar hari ini? Salam dari Koncomu ini adalah layanan konsultasi Psikologi gratis untuk pemeriksaan dini mandiri. Tertarik untuk cek-cek dulu?"
intent_general = "Ga papa kalo belum tertarik. Lagi pengen lihat-lihat apa? Boleh loh pilih salah 1 yaa..."
intent_health_greet = "Nah, terima kasih udah mau lihat-lihat dulu. Gampang kok isi beberapa info dulu ya, ga usah pake nama asli juga ga papa."



class ActionHelloWorld(Action):


    
     def name(self) -> Text:
         return "action_hello_world"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
        # DBHelper().__connect__()
       
        message_id = tracker.latest_message.get("message_id")  # Assuming the message_id is stored in the latest message
        sender_id = tracker.sender_id
        timestamp = tracker.latest_message.get("timestamp")
        print(sender_id)
        
        
        # Connect with the Telegram API to retrieve the message
        telegram_message = self.get_telegram_message(sender_id, message_id, timestamp)

        
           
               

        if telegram_message:
            # Example: Send a response to the Telegram message
            message = f'Halo {telegram_message}! {intent_greet}'
           
            dispatcher.utter_message(text=message,buttons=[
                        {"title": "Ya", "payload": "ya"},
                        {"title": "Tidak", "payload": "tidak"}
                        
                    ])

    

        return []
    
        
     def get_telegram_message(self, sender_id: Text, message_id: Text, timestamp: float) -> Dict[Text, Any]:
        # Make the necessary API call to retrieve the Telegram message using the provided information
        # Update the URL to point to your Ngrok URL
        
        telegram_token = "5866219252:AAGrKXI5Ib9Mi3wEQ5JNc60OSveh7pOQ-f0"
        telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/getChatMember?chat_id={sender_id}&user_id={sender_id}"
        
        response = requests.get(telegram_api_url)
        print(response.json())
        if response.status_code == 200:
            data = response.json()
            username = data["result"]["user"]["first_name"]
            return username
        else:
            return None
     

class ActionIntentGeneral(Action):

    def name(self) -> Text:
        return "action_intent_general"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        dispatcher.utter_message(text=intent_general,buttons=[
                {"title": "Games", "payload": "/games"},
                {"title": "Jokes", "payload": "/jokes"}
                
            ])


class ActionIntentHealth(Action):

    def name(self) -> Text:
        return "action_health_greet"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("disini")
    
        dispatcher.utter_message(text=intent_health_greet,buttons=[
                {"title": "Isi data", "payload": "/formdata"},
                {"title": "Cek Level Cemas", "payload": "/anxietylevel"},
                {"title": "Ceritain apa masalahmu", "payload": "/curhat"}
                
            ])
        
class ActionIntentFormdata(Action):
    def name(self) -> Text:
        return "action_intent_formdata"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["name", "age", "job","symptom"]

    def slot_mappings(self) -> Dict[Text, Any]:
        return {
            "name": self.from_entity(entity="name"),
            "age": self.from_entity(entity="age"),
            "job": self.from_intent(entity="job"),
            "symptom": self.from_intent(entity="symptom"),
        }
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Accessing slot values
        name = tracker.get_slot("name")
        age = tracker.get_slot("age")
        job = tracker.get_slot("job")
        symptom = tracker.get_slot("symptom")

        # Perform actions based on slot values
       
        dispatcher.utter_message(  f'Halo {name}! {age}, {job},{symptom}')

        return []
    
# class DBHelper:

#     def __init__(self):
#         self.host = "10.64.64.92"
#         self.user = "OMNI_PROD"
#         self.password = "dbadmin123"
#         self.db = "agent"

#     def __connect__(self):
#         self.con = cx_Oracle.connect(user="OMNI_PROD", password="dbadmin123",
#                                dsn="10.64.64.92/omnitrn")

#     def __disconnect__(self):
#         self.con.close()

#     def fetch(self, sql):
#         self.__connect__()
#         self.cur.execute(sql)
#         result = self.cur.fetchall()
#         self.__disconnect__()
#         return result

#     def execute(self, sql):
#         self.__connect__()
#         self.cur.execute(sql)
#         self.__disconnect__()