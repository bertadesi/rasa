# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

from configparser import ConfigParser
import configparser
from rasa_sdk.events import SlotSet
import tracemalloc


from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer, models
from torch import nn
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import mysql.connector
from datetime import datetime




#Read config.ini file

config_file = 'config.ini'
config = configparser.ConfigParser()

conn = mysql.connector.connect(host='localhost', user='root', password='admin123#', database='koncoku')


try:
    config.read(config_file)
    print("File loaded successfully")
    config.sections()
    
except configparser.Error as e:
    print(f"Error reading file: {str(e)}")





intent_greet = "Apa kabar hari ini? Salam dari Koncomu ini adalah layanan konsultasi Psikologi gratis untuk pemeriksaan dini mandiri. Tertarik untuk cek-cek dulu?"
intent_general = "Ga papa kalo belum tertarik. next time ya "
intent_health_greet = "Nah, terima kasih udah mau lihat-lihat dulu. Kamu lagi pengen ngapain nih? Pilih salah satu ya."
intent_jokes ="this page is intended to be blank...(lol) ini bener nya maksudnya ga ada ide"
message_anxiety ='Banyak pilihan untuk dapat melakukan pengecekan dini tentang kondisi psikismu, pilih salah satu ya'
message_intro_dass ='Penasaran ya DASS itu apa? Dass bisa digunakan untuk cek kondisi sesaat apakah kalian sedang mengalami kecemasan. Beberapa pertanyaan akan dihitung untuk melihat seberapa cemas kamu saat ini. Mau coba? yuk'
message_dass_1='Apakah mulutmu akhir2 ini terasa kering?'
message_dass_2='Apakah sering merasakan gangguan dalam bernapas ( seperti napas cepat atau sulit bernapas)?'
message_dass_3='Apakah kamu merasakan kelemahan pada anggota tubuh?'
message_dass_4='Apakah kamu merasa cemas yang berlebihan dalam suatu situasi namun bisa lega jika hal/situasi itu berakhir?'
message_dass_5='Apakah kamu sering merasa kelelahan?'
message_dass_6='Apakah sering berkeringat (misal: tangan berkeringat) tanpa stimulasi oleh cuaca maupun latihan fisik'
message_dass_7='Apakah sering ketakutan tanpa alasan yang jelas?'
message_dass_8='Apakah sering merasa kesulitan dalam menelan?'
message_dass_9='Apakah kamu mengalami perubahan kegiatan jantung dan denyut nadi tanpa stimulasi oleh latihan fisik?'
message_dass_10='Apakah kamu mudah panik dalam menghadapi sesuatu?'
message_dass_11='Apakah kamu takut diri terhambat oleh tugas-tugas yang tidak biasa dilakukan?'
message_dass_12='Apakah kamu sering merasakan ketakutan?'
message_dass_13='Apakah kamu merasa khawatir dengan situasi saat diri Anda mungkin menjadi panik dan mempermalukan diri sendiri?'
message_dass_14='Apakah kamu sering merasakan gemetar?'
message_confirmation='Okay, sepertinya kita harus ngobrol lebih dalam nih. Kalo boleh tahu apa yang kamu rasakan sekarang?'
message_dass_Close='Wow, terima kasih sudah berbincang-bincang. Saya lihat level cemas Anda masih dalam skala normal. Selamat beraktivitas dan tetap semangat'



def insertMeasurement(sender_id,code_measurement):
   
    try:
            
        if  'dass' in code_measurement:
       
                type_measurement ='DASS'
       
                score = code_measurement[-1]
           
       
        elif 'gad' in code_measurement:
           
                type_measurement ='GAD7'
                score = code_measurement[-1]
           
        else:
       
                type_measurement='STAIT5'
                score = code_measurement[-1]
   
       
 
     # Create a connection
               
        print('kesini ga?')
               # Execute an INSERT query to save the feedback
        cursor = conn.cursor()
        cursor.execute("INSERT INTO measurement (session_id, type_measurement, code_measurement,score)"
                              "VALUES  (%s, %s, %s, %s)", (sender_id,type_measurement,code_measurement,score))
        conn.commit()
   
   
    except mysql.connector.Error as err:
            
               print(err)
   
    finally:
               # Close the database connection
               cursor.close()
               conn.close()

      
    return None


def deleteMeasurement(sender_id,code_measurement):
   
    try:
            
    
        code = code_measurement[:-1]      
        print(code)
        query1 = "delete from measurement  where session_id='" + sender_id+ "' and code_measurement like'%"+code +"%'"
       
 
     # Create a connection
               
        print('delete?')
               # Execute an INSERT query to save the feedback
        cursor = conn.cursor()
        cursor.execute(query1)
        conn.commit()
   
   
    except mysql.connector.Error as err:
            
        print(err)
   
    finally:
               # Close the database connection
        
        if 'cursor' in locals():
           cursor.close()
        if 'conn' in locals():
           conn.close()
        

      
    return None


def ValidateMeasurement(sender_id,code_measurement):
    
    result_string =""
    try:
            
        if  'dass' in code_measurement:
                
                code = code_measurement[:-1]   
                query1="SELECT count(*) FROM measurement WHERE type_measurement='DASS'" 
                query2 = " and code_measurement like '%"+  code+"%'"               
       
        elif 'gad' in code_measurement:
           
                query1="SELECT count(*) FROM measurement WHERE type_measurement='GAD7'" 
                query2 = " and code_measurement ="+  code_measurement    
        else:
       
                
                query1="SELECT count(*) FROM measurement WHERE type_measurement='STAIT5'"
                query2 = " and code_measurement ="+  code_measurement    
 
     # Create a connection
        cursor = conn.cursor()       
        query = query1 + query2 +" and session_id = %s"
        cursor.execute(query, (sender_id,))

# Fetch the results if needed
        result = cursor.fetchone()
        result_string = str(result[0])
        print(result_string)
        print('validate')
   
    except mysql.connector.Error as err:
            
               print(err)
   
    finally:
               # Close the database connection
               if 'cursor' in locals():
                  cursor.close()
               if 'conn' in locals():
                  conn.close()

      
    return result_string


def countMeasurement(sender_id,code_measurement):
    
    result_string =""
    try:
            
        if  'dass' in code_measurement:
                
                query1="SELECT sum(score) FROM measurement where type_measurement='DASS' and session_id='"+ sender_id+"'"
                
       
        elif 'gad' in code_measurement:
           
                query1="SELECT sum(score) FROM measurement where type_measurement='GAD7' and session_id='"+ sender_id+"'"
                
           
        else:
       
                query1="SELECT sum(score) FROM measurement where type_measurement='STAIT5' and session_id='"+ sender_id+"'"
                
   
       
 
     # Create a connection
               
        print('count measurement')
               # Execute an INSERT query to save the feedback
        cursor = conn.cursor()
        cursor.execute(query1)
        result = cursor.fetchone()
        result_string = str(result[0])
   
   
    except mysql.connector.Error as err:
            
               print(err)
   
    finally:
               # Close the database connection
               if 'cursor' in locals():
                  cursor.close()
               if 'conn' in locals():
                  conn.close()

      
    return result_string

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
        print(timestamp)
        
        # Connect with the Telegram API to retrieve the message
        telegram_message = self.get_telegram_message(sender_id, message_id, timestamp)

        
           
               

        if telegram_message:
            # Example: Send a response to the Telegram message
            message = f'Halo {telegram_message}! {intent_greet}'
           
            dispatcher.utter_message(text=message,buttons=[
                        {"title": "Ya", "payload": "/health"},
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
            timestamp = datetime.now()
            try:
                    # Create a connection
                    
        
                    # Execute an INSERT query to save the feedback
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO session (session_id, name, session_start)"
                                   "VALUES  (%s, %s, %s)", (sender_id,username,timestamp))
                    conn.commit()
        
                   
        
            except mysql.connector.Error as err:
                    print(err)
        
            finally:
                    # Close the database connection
                    cursor.close()
                    conn.close()

            return username
        else:
            return None
     

class ActionIntentGeneral(Action):

    def name(self) -> Text:
        return "action_intent_general"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        api_key = "pMTJDhjh5Alc5Hb27BXzMBIWMNhHXYTBylRoIKFf"
        url = "https://quotes.rest/qod.json"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers)
        try:
                # Create a connection
                
                sender_id = tracker.sender_id
                # Execute an INSERT query to save the feedback
                cursor = conn.cursor()
                query = "SELECT DISTINCT name FROM session WHERE session_id = %s"
                cursor.execute(query, (sender_id,))

# Fetch the results if needed
                result = cursor.fetchone()
                result_string = str(result[0])
               
    
               
    
        except mysql.connector.Error as err:
                print(err)
    
        finally:
                # Close the database connection
                cursor.close()
               

        if response.status_code == 200:
            data = response.json()
            quote = data["contents"]["quotes"][0]["quote"]
            author = data["contents"]["quotes"][0]["author"]
            print(f"Random Quote: '{quote}' - {author}")
        else:
            print("Failed to retrieve a random quote.")
        dispatcher.utter_message(text=quote+" by "+author)
        dispatcher.utter_message(text=intent_general+" "+result_string+" salam sehat selalu :) tetep semangat")

class ActionIntentJokes(Action):

    def name(self) -> Text:
        return "action_intent_jokes"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        dispatcher.utter_message(text=intent_jokes,buttons=[
                {"title": "Halaman depan", "payload": "/start"},
                {"title": "Bye", "payload": "/survey"}
                
            ])

class ActionIntentHealth(Action):

    def name(self) -> Text:
        return "action_health_greet"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("disini")
    
        dispatcher.utter_message(text=intent_health_greet,buttons=[
                {"title": "Cek Level Cemas", "payload": "/anxietylevel"},
                {"title": "Ceritain apa masalahmu", "payload": "/curhat"}
                

                
            ])
        
class ActionIntentInform(Action):
    def name(self) -> Text:
        return "action_intent_inform"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
          print("submit form")
          
          
          self.submit(dispatcher, tracker, domain)
          
   
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
         
      
         
         print(name)
         # Perform actions based on slot values
         if (name is None and age is None and job is None and symptom is None):
             dispatcher.utter_message(  'Datanya belum dimasukkan ya, yuk di lengkapi dulu')
         elif (name is not None and age is None and job is None and symptom is None):
            dispatcher.utter_message(  f'Halo {name}! untuk data umur, pekerjaan dan gejala /symptom masih belum diisi ya')
         elif (name is not None and age is not None and job is None and symptom is None):
            dispatcher.utter_message(  f'Halo {name}! , {age}, untuk data  pekerjaan dan gejala /symptom masih belum diisi ya')
         elif (name is not None and age is not None and job is not  None and symptom is None):
           dispatcher.utter_message(  f'Halo {name}! , {age}, {job} untuk gejala /symptom masih belum diisi ya')
         elif (name is not None and age is not None and job is not  None and symptom is not None):
           dispatcher.utter_message(  f'Halo {name}! , {age}, {job} dengan {symptom} sudah terisi semuanya. Jika setuju silahkan pilih',
                                    buttons=[
                                            {"title": "Submit", "payload": "/submitformdata"},
                                            {"title": "Batal", "payload": "/batalformdata"}
                                            
                                        ])

         return []     
          
          
             
          
class ActionIntentFormData(Action):
    def name(self) -> Text:
        return "action_intent_formdata"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
          print("isi form")
          
          dispatcher.utter_message("Boleh isi form dengan format: ")
          dispatcher.utter_message("nama [isi dengan nama](name)")
          dispatcher.utter_message("umur [contoh: 25](age)")
          dispatcher.utter_message("Pekerjaan/Pendidikan [contoh :S1, Karyawan, Mahasiswa dll](job)")
          dispatcher.utter_message("Gejala/Masalah [isi dengan deskripsi masalah kesehatan mental](symptom)")
          
          # return self.resetSlot(dispatcher, tracker, domain)
          
    def resetSlot (
          self,
          dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any],
      ) -> List[Dict[Text, Any]]:
        
        print("reset")
        return [
            SlotSet("name", None),
            SlotSet("age", None),
            SlotSet("job", None),
            SlotSet("symptom", None)
        ]
          
class ActionIntentCurhat(Action):
     def name(self) -> Text:
         return "action_intent_curhat"

     def run(self, dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
           
           
           
           dispatcher.utter_message("Kalo boleh tahu apa ya masalahmu?")
           
class ActionCheckCurhatSedih(Action):
    def name(self) -> Text:
        return "action_intent_sad"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          
          
          print(message_id)
             
          model_name = "indobenchmark/indobert-base-p1"
          word_embedding_model = models.Transformer(model_name, max_seq_length=256)
          pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
          dense_model = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(), out_features=256, activation_function=nn.Tanh())
          model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_model])
     
          input_text = message_id
          reference_texts = ["mengalami perubahan nafsu makan",
             "mengalami perubahan tidur",
              "merasa kelelahan atau kekurangan energi",
              "kesulitan berkonsentrasi atau membuat keputusan",
              "merasa cemas atau gelisah",
              "mengalami serangan panik",
              "mengalami perubahan fisik yang tidak dapat dijelaskan",
              "memiliki pikiran atau keinginan untuk menyakiti diri sendiri atau berpikir tentang kematian"]
          input_embedding = model.encode([input_text])[0]
          reference_embeddings = model.encode(reference_texts)
     
          similarity_scores = cosine_similarity([input_embedding], reference_embeddings)[0]
          sorted_indices = np.argsort(similarity_scores)[::-1]
     
              # Retrieve the original texts based on the sorted indices
          sorted_texts = [reference_texts[i] for i in sorted_indices]
          print(sorted_texts[0]) 
             
          message ='oh kamu'
          dispatcher.utter_message(text=message+" "+sorted_texts[0])
          
          
class ActionCheckCurhatSeneng(Action):
    def name(self) -> Text:
        return "action_intent_great"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
         message_id = tracker.latest_message.get("text") 
         print(message_id)
            
         model_name = "indobenchmark/indobert-base-p1"
         word_embedding_model = models.Transformer(model_name, max_seq_length=256)
         pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
         dense_model = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(), out_features=256, activation_function=nn.Tanh())
         model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_model])
    
         input_text = message_id
         reference_texts = ["Mengalami peningkatan nafsu makan yang luar biasa! Makanan favorit kamu jadi lebih enak.",
                   "Tidurku semakin nyenyak dan pulas setiap malam. Bangun dengan semangat baru setiap pagi!",
                   "kamu merasa penuh energi dan semangat setiap hari. Tidak ada rasa lelah yang mengganggu!",
                   "Kemampuan kamu dalam berkonsentrasi dan membuat keputusan semakin baik. kamu merasa sangat fokus!",
                   "kamu merasa tenang dan bahagia setiap hari. Tidak ada rasa cemas atau gelisah yang mengganggu pikiran kamu.",
                   "Kehidupan kamu penuh kebahagiaan dan tidak ada ruang untuk serangan panik. kamu merasa kuat!",
                   "Tubuh kamu terasa segar dan sehat. Tidak ada perubahan fisik yang perlu dikhawatirkan.",
                   "kamu memiliki pikiran positif dan hanya ingin menjalani kehidupan dengan penuh kebahagiaan dan harapan."]
         input_embedding = model.encode([input_text])[0]
         reference_embeddings = model.encode(reference_texts)
    
         similarity_scores = cosine_similarity([input_embedding], reference_embeddings)[0]
         sorted_indices = np.argsort(similarity_scores)[::-1]
    
             # Retrieve the original texts based on the sorted indices
         sorted_texts = [reference_texts[i] for i in sorted_indices]
         print(sorted_texts[0]) 
            
         
         dispatcher.utter_message(text=sorted_texts[0])
                     
    
          
          
class ActionAnxietyLevel(Action):
    def name(self) -> Text:
        return "action_intent_anxietylevel"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_anxiety,buttons=[
                      {"title": "DASS", "payload": "/dass"},
                      {"title": "GAD-7", "payload": "/gad-7"},
                      {"title": "STAIT/STAIS-5", "payload": "/stait"}
         #             {"title": "Test Slot", "payload": "/formdata"}
                      
                      
                  ])

          
class ActionDASS(Action):
    def name(self) -> Text:
        return "action_intent_dass"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_intro_dass,buttons=[
                      {"title": "Mulai", "payload": "/mulaidass"},
                      {"title": "Batal", "payload": "/batal"}
                                            
                      
                  ])
    
class ActionDASS1(Action):
    def name(self) -> Text:
        return "action_intent_dass1"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_dass_1,buttons=[
                      {"title": "Tidak pernah", "payload": "dass10"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass11"},
                      {"title": "sering", "payload": "dass12"},
                      {"title": "setiap saat", "payload": "dass13"}
                                            
                      
                  ])    
          
class ActionDASS2(Action):
    def name(self) -> Text:
        return "action_intent_dass2"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
              
          dispatcher.utter_message(text=message_dass_2,buttons=[
                      {"title": "Tidak pernah", "payload": "dass20"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass21"},
                      {"title": "sering", "payload": "dass22"},
                      {"title": "setiap saat", "payload": "dass23"}
                                            
                      
                  ])    

class ActionDASS3(Action):
    def name(self) -> Text:
        return "action_intent_dass3"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          dispatcher.utter_message(text=message_dass_3,buttons=[
                      {"title": "Tidak pernah", "payload": "dass30"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass31"},
                      {"title": "sering", "payload": "dass32"},
                      {"title": "setiap saat", "payload": "dass33"}
                                            
                      
                  ])   
    
    
class ActionDASS4(Action):
    def name(self) -> Text:
        return "action_intent_dass4"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          dispatcher.utter_message(text=message_dass_4,buttons=[
                      {"title": "Tidak pernah", "payload": "dass40"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass41"},
                      {"title": "sering", "payload": "dass42"},
                      {"title": "setiap saat", "payload": "dass43"}
                                            
                      
                  ])     
          
class ActionDASS5(Action):
    def name(self) -> Text:
        return "action_intent_dass5"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
         
             
              dispatcher.utter_message(text=message_dass_5,buttons=[
                          {"title": "Tidak pernah", "payload": "dass50"},
                          {"title": "Kadang-kadang atau jarang", "payload": "dass51"},
                          {"title": "sering", "payload": "dass52"},
                          {"title": "setiap saat", "payload": "dass53"}
                                                
                          
                      ])  
          
class ActionDASS6(Action):
    def name(self) -> Text:
        return "action_intent_dass6"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
              dispatcher.utter_message(text=message_dass_6,buttons=[
                      {"title": "Tidak pernah", "payload": "dass60"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass61"},
                      {"title": "sering", "payload": "dass62"},
                      {"title": "setiap saat", "payload": "dass63"}
                                            
                      
                  ])            



class ActionDASS7(Action):
    def name(self) -> Text:
        return "action_intent_dass7"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_7,buttons=[
                      {"title": "Tidak pernah", "payload": "dass70"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass71"},
                      {"title": "sering", "payload": "dass72"},
                      {"title": "setiap saat", "payload": "dass73"}
                                            
                      
                  ]) 
          
class ActionDASS8(Action):
    def name(self) -> Text:
        return "action_intent_dass8"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          insertMeasurement(sender_id,message_id)
          dispatcher.utter_message(text=message_dass_8,buttons=[
                      {"title": "Tidak pernah", "payload": "dass80"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass81"},
                      {"title": "sering", "payload": "dass82"},
                      {"title": "setiap saat", "payload": "dass83"}
                                            
                      
                  ]) 
          
class ActionDASS9(Action):
    def name(self) -> Text:
        return "action_intent_dass9"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_9,buttons=[
                      {"title": "Tidak pernah", "payload": "dass90"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass91"},
                      {"title": "sering", "payload": "dass92"},
                      {"title": "setiap saat", "payload": "dass93"}
                                            
                      
                  ]) 
          
class ActionDASS10(Action):
    def name(self) -> Text:
        return "action_intent_dass10"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_10,buttons=[
                      {"title": "Tidak pernah", "payload": "dass100"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass101"},
                      {"title": "sering", "payload": "dass102"},
                      {"title": "setiap saat", "payload": "dass103"}
                                            
                      
                  ]) 
          
class ActionDASS11(Action):
    def name(self) -> Text:
        return "action_intent_dass11"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_11,buttons=[
                      {"title": "Tidak pernah", "payload": "dass110"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass11"},
                      {"title": "sering", "payload": "dass112"},
                      {"title": "setiap saat", "payload": "dass113"}
                                            
                      
                  ]) 
          
class ActionDASS12(Action):
    def name(self) -> Text:
        return "action_intent_dass12"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_12,buttons=[
                      {"title": "Tidak pernah", "payload": "dass120"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass121"},
                      {"title": "sering", "payload": "dass122"},
                      {"title": "setiap saat", "payload": "dass123"}
                                            
                      
                  ]) 
          
          
          
class ActionDASS13(Action):
    def name(self) -> Text:
        return "action_intent_dass13"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_13,buttons=[
                      {"title": "Tidak pernah", "payload": "dass130"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass131"},
                      {"title": "sering", "payload": "dass132"},
                      {"title": "setiap saat", "payload": "dass133"}
                                            
                      
                  ]) 
          
          
class ActionDASS14(Action):
    def name(self) -> Text:
        return "action_intent_dass14"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_14,buttons=[
                      {"title": "Tidak pernah", "payload": "dass140"},
                      {"title": "Kadang-kadang atau jarang", "payload": "dass141"},
                      {"title": "sering", "payload": "dass142"},
                      {"title": "setiap saat", "payload": "dass143"}
                                            
                      
                  ]) 
             
class ActionDASSClose(Action):
    def name(self) -> Text:
        return "action_intent_dassClose"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          
          cekTotalScore = countMeasurement(sender_id, message_id)
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= 14:
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_Close)             
             
