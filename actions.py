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

import pandas as pd
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





intent_greet = "Apa kabar hari ini? Salam dari Koncomu ini adalah layanan konsultasi Psikologi gratis untuk membantu mendapatkan gambaran umum apakah kamu mengalami anxiety disorder atau tidak. Semua hasil harus diverifikasi lagi pada Unit Konsultasi Psikologi, atau Psikolog ya.Tertarik untuk cek-cek dulu?"
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
message_intro_gad='GAD-7 (Generalized Anxiety Disorder 7) adalah sebuah alat penilaian yang digunakan untuk mengukur tingkat kecemasan pada seseorang. Yuk boleh dicoba ya... selama 2 minggu terakhir, seberapa sering kamu terganggu oleh masalah-masalah berikut?'
message_gad_1='Merasa gelisah, cemas atau tegang'
message_gad_2='Tidak mampu menghentikan atau mengendalikan rasa khawatir'
message_gad_3='Terlalu mengkhawatirkan berbagai hal'
message_gad_4='Sulit untuk santai'
message_gad_5='Sangat gelisah sehingga sulit duduk diam'
message_gad_6='Menjadi mudah jengkel atau lekas marah'
message_gad_7='Merasa takut seolah-olah sesuatu yang mengerikan mungkin terjadi'
message_gad_Close='Wow, test GAD-7 mu sudah selesai. Saya lihat level cemas Anda masih dalam skala normal. Selamat beraktivitas dan tetap semangat'
message_intro_stait='STAIT/STAIS 5 merupakan bentuk test kecemasan versi pendek dari Spielberger. Ada 10 jenis pernyataan, silahkan dijawab tanpa berpikir lama yang mendeskripsikan perasaanmu saat ini. Selamat mencoba...'
message_stait_1='saya merasa kecewa'
message_stait_2='saya merasa ketakutan'
message_stait_3='saya merasa cemas'
message_stait_4='saya merasa gelisah / gugup'
message_stait_5='saya merasa bingung'
message_stait_6='Saya merasa masalah bertumpuk hingga sulit untuk mengatasinya'
message_stait_7='Saya terlalu khawatir tentang sesuatu yang sebenarnya tidak begitu penting.'
message_stait_8='Beberapa pikiran yang tidak penting muncul dalam pikiran saya dan mengganggu saya.'
message_stait_9='Saya begitu merasa kecewa sehingga sulit bagi saya untuk melupakan mereka.'
message_stait_10='Saya merasa kacau atau tegang ketika sesuatu hal mengganggu saya'
message_stait_Close='Well done! Terima kasih sudah mencoba menjawab semua pertanyaan. Tidak ada yang perlu dikawatirkan, tetap semangat dan jaga kesehatan..'

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
              if 'cursor' in locals():
                 cursor.close()
              if 'conn' in locals():
                 conn.close()

      
    return None



def insertSurvey(sender_id,code_measurement):
   
    try:
            
            
        score = code_measurement[-1]
           
 
     # Create a connection
               
        print('survey')
               # Execute an INSERT query to save the feedback
        cursor = conn.cursor()
        cursor.execute("INSERT INTO survey (session_id, components,score)"
                              "VALUES  (%s, %s, %s)", (sender_id,code_measurement,score))
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


def insertCurhat(sender_id,text,is_anxiety):
   
    try:
            
 
     # Create a connection
               
        print('curhat')
               # Execute an INSERT query to save the feedback
        cursor = conn.cursor()
        cursor.execute("INSERT INTO result (session_id, symptom,is_anxiety)"
                              "VALUES  (%s, %s, %s)", (sender_id,text,is_anxiety))
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

def deleteSurvey(sender_id,code_measurement):
   
    try:
            
    
        code = code_measurement[:-1]      
        print(code)
        query1 = "delete from survey  where session_id='" + sender_id+ "' and components like'%"+code +"%'"
       
 
     # Create a connection
               
        print('delete survey?')
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
                code = code_measurement[:-1]   
                query1="SELECT count(*) FROM measurement WHERE type_measurement='GAD7'" 
                query2 = " and code_measurement like '%"+  code+"%'"   
        else:
       
                code = code_measurement[:-1]  
                query1="SELECT count(*) FROM measurement WHERE type_measurement='STAIT5'"
                query2 = " and code_measurement like '%"+  code+"%'"   
 
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



def ValidateSurvey(sender_id,code_measurement):
    
    result_string =""
    try:
            
        code = code_measurement[:-1] 
        query1="SELECT count(*) FROM survey WHERE components  like '%"+  code+"%'"               
       
       
 
     # Create a connection
        cursor = conn.cursor()       
        query = query1  +" and session_id = %s"
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
                
           
        elif 'stata' in code_measurement:
       
                query1="SELECT sum(score) FROM measurement where type_measurement='STAIT5' and session_id='"+ sender_id+"'"
                
        else:
       
                query1="SELECT sum(score) FROM measurement where session_id='"+ sender_id+"'"
 
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


def SBERTModel(text):
    
    model_name = "indobenchmark/indobert-base-p1"
    word_embedding_model = models.Transformer(model_name, max_seq_length=256)
    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
    dense_model = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(), out_features=256, activation_function=nn.Tanh())
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_model])

    input_text = text
    
    df = pd.read_csv('data/dataset.csv')
    reference_texts = df['symptom'].tolist()

    input_embedding = model.encode([input_text])[0]
    reference_embeddings = model.encode(reference_texts)

    similarity_scores = cosine_similarity([input_embedding], reference_embeddings)[0]
    sorted_indices = np.argsort(similarity_scores)[::-1]
    #sorted_texts = [reference_texts[i] for i in sorted_indices]
    max_similarity_score = similarity_scores[sorted_indices[0]]
    
    if max_similarity_score > 0.8:
        is_anxiety ='Y'
        
    else:
        is_anxiety ='N'
    
    return is_anxiety

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
                        {"title": "Tidak", "payload": "/general"}
                        
                    ])

    

        return []
    
        
     def get_telegram_message(self, sender_id: Text, message_id: Text, timestamp: float) -> Dict[Text, Any]:
        # Make the necessary API call to retrieve the Telegram message using the provided information
        # Update the URL to point to your Ngrok URL
       

        telegram_token = "6681142425:AAFJDy1oG-9EKr3RdV5KRRTbXv0H2a_OQxg"
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
                
                    if 'cursor' in locals():
                       cursor.close()
                    if 'conn' in locals():
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
                if 'cursor' in locals():
                   cursor.close()
        quote=''
        author=''

        if response.status_code == 200:
            data = response.json()
            quote = data["contents"]["quotes"][0]["quote"]
            author = data["contents"]["quotes"][0]["author"]
            print(f"Random Quote: '{quote}' - {author}")
        else:
            print("Failed to retrieve a random quote.")
        
        dispatcher.utter_message(text=quote+"  "+author)
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
          sender_id =  tracker.sender_id
          
          print(message_id)
          message2 = "Tapi kalo mau cek level cemasmu kamu bisa ketik: anxietylevel"
          cekCount = countMeasurement(sender_id, '')
             
          is_anxiety=SBERTModel(message_id)
          
          if cekCount ==0:
              if is_anxiety=='Y':
                  
                 insertCurhat(sender_id, message_id, is_anxiety)
                 message ='oh sepertinya kamu terdeteksi sedang mengalami gejala kecemasan berlebih, ada baiknya untuk konsultasi atau baca2 artikel tentang hal ini'
                 message3 ='Tips mengatasi gejala cemas: latihan pernafasan (Seperti yoga, meditasi), jaga pola makan, tidur yang cukup, jika masih merasa cemas, harus konsultasi ke PSikolog. Jangan disimpen sendiri dan dibiarin ya'
                
                 dispatcher.utter_message(text=message+" ")
                 dispatcher.utter_message(text=message3+" ")
                 dispatcher.utter_message(text=message2+" ")
                 
              else:
                 insertCurhat(sender_id, message_id, is_anxiety)
                 message ='Walaupun moodmu lagi ga bagus tapi sepertinya kamu tidak mengalami gejala cemas berlebih. Tapi ada baiknya kamu cek level cemasmu ya, kamu bisa ketik:anxietylevel' 
                 dispatcher.utter_message(text=message+" ")
              
              
          else:
              
              
              if is_anxiety=='Y':
                  
                 insertCurhat(sender_id, message_id, is_anxiety)
                 message ='oh sepertinya kamu terdeteksi sedang mengalami gejala kecemasan berlebih, ada baiknya untuk konsultasi atau baca2 artikel tentang hal ini. '
                 message3 ='Tips mengatasi gejala cemas: latihan pernafasan (Seperti yoga, meditasi), jaga pola makan, tidur yang cukup, jika masih merasa cemas, harus konsultasi ke PSikolog. Jangan disimpen sendiri dan dibiarin ya'
                 message2='Bisa ketik : psikolog atau artikel, untuk info lebih lanjut ya'
                 dispatcher.utter_message(text=message+" ")
                 dispatcher.utter_message(text=message3+" ")
                 dispatcher.utter_message(text=message2+" ")
                 
              else:
                 insertCurhat(sender_id, message_id, is_anxiety)
                 message ='Dari hasil cek tadi memang benar skor level cemas diatas rata-rata, tetapi kemungkinan itu hanya kondisi sesaat saja' 
                 message2='Tertarik untuk baca-baca info? Bisa ketik: psikolog atau artikel, untuk info lebih lanjut ya'
                 message3 ='Tips mengatasi gejala cemas: latihan pernafasan (Seperti yoga, meditasi), jaga pola makan, tidur yang cukup, jika masih merasa cemas, harus konsultasi ke PSikolog. Jangan disimpen sendiri dan dibiarin ya'
                
                 dispatcher.utter_message(text=message+" ")
                 dispatcher.utter_message(text=message3+" ")
                 dispatcher.utter_message(text=message2+" ")
              
          
          
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
        
         
         df = pd.read_csv('data/dataset_happy.csv')
         reference_texts = df['comment'].tolist()

         input_embedding = model.encode([input_text])[0]
         reference_embeddings = model.encode(reference_texts)

         similarity_scores = cosine_similarity([input_embedding], reference_embeddings)[0]
         sorted_indices = np.argsort(similarity_scores)[::-1]
         
             # Retrieve the original texts based on the sorted indices
         sorted_texts = [reference_texts[i] for i in sorted_indices]
         print(sorted_texts[0]) 
         message1 = sorted_texts[0]
         message2 = "Salam dari KoncoKu selalu ya, tapi kalo mau cek level cemasmu kamu bisa ketik: anxietylevel"
            
         
         dispatcher.utter_message(text=message1)
         dispatcher.utter_message(text=message2)
                     
    
          
          
class ActionAnxietyLevel(Action):
    def name(self) -> Text:
        return "action_intent_anxietylevel"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_anxiety,buttons=[
                      {"title": "DASS", "payload": "/dass"},
                      {"title": "GAD-7", "payload": "/gad"},
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          if cekTotalScore >= "14.00":
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
          
          cekTotalScore = int(countMeasurement(sender_id, message_id))
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= "14.00":
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_Close)             

class ActionGAD(Action):
    def name(self) -> Text:
        return "action_intent_gad"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_intro_gad,buttons=[
                      {"title": "Mulai", "payload": "/mulaigad"},
                      {"title": "Batal", "payload": "/batal"}
                                            
                      
                  ])          
          
class ActionGAD1(Action):
    def name(self) -> Text:
        return "action_intent_gad1"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_gad_1,buttons=[
                      {"title": "Tidak pernah", "payload": "gadd10"},
                      {"title": "Beberapa hari", "payload": "gadd11"},
                      {"title": "lebih dari seminggu", "payload": "gadd12"},
                      {"title": "Hampir setiap hari", "payload": "gadd13"}
                                            
                      
                  ])  
          
class ActionGAD2(Action):
    def name(self) -> Text:
        return "action_intent_gad2"

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
              
          dispatcher.utter_message(text=message_gad_2,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd20"},
                     {"title": "Beberapa hari", "payload": "gadd21"},
                     {"title": "lebih dari seminggu", "payload": "gadd22"},
                     {"title": "Hampir setiap hari", "payload": "gadd23"}
                                            
                      
                  ])  
          
class ActionGAD3(Action):
    def name(self) -> Text:
        return "action_intent_gad3"

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
              
          dispatcher.utter_message(text=message_gad_3,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd30"},
                     {"title": "Beberapa hari", "payload": "gadd31"},
                     {"title": "lebih dari seminggu", "payload": "gadd32"},
                     {"title": "Hampir setiap hari", "payload": "gadd33"}
                                            
                      
                  ])  
          
class ActionGAD4(Action):
    def name(self) -> Text:
        return "action_intent_gad4"

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
              
          dispatcher.utter_message(text=message_gad_4,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd40"},
                     {"title": "Beberapa hari", "payload": "gadd41"},
                     {"title": "lebih dari seminggu", "payload": "gadd42"},
                     {"title": "Hampir setiap hari", "payload": "gadd43"}
                                            
                      
                  ])  
          
class ActionGAD5(Action):
    def name(self) -> Text:
        return "action_intent_gad5"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
              
          if cekTotalScore >= "10.00":
              dispatcher.utter_message(text=message_confirmation) 
          else:
               
           dispatcher.utter_message(text=message_gad_5,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd50"},
                     {"title": "Beberapa hari", "payload": "gadd51"},
                     {"title": "lebih dari seminggu", "payload": "gadd52"},
                     {"title": "Hampir setiap hari", "payload": "gadd53"}
                                            
                      
                  ])  
          
class ActionGAD6(Action):
    def name(self) -> Text:
        return "action_intent_gad6"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
              
          if cekTotalScore >= "10.00":
               dispatcher.utter_message(text=message_confirmation) 
          else:    
               dispatcher.utter_message(text=message_gad_6,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd60"},
                     {"title": "Beberapa hari", "payload": "gadd61"},
                     {"title": "lebih dari seminggu", "payload": "gadd62"},
                     {"title": "Hampir setiap hari", "payload": "gadd63"}
                                            
                      
                  ])  
          
class ActionGAD7(Action):
    def name(self) -> Text:
        return "action_intent_gad7"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          if cekTotalScore >= "10.00":
                dispatcher.utter_message(text=message_confirmation) 
          else:        
                dispatcher.utter_message(text=message_gad_7,buttons=[
                     {"title": "Tidak pernah", "payload": "gadd70"},
                     {"title": "Beberapa hari", "payload": "gadd71"},
                     {"title": "lebih dari seminggu", "payload": "gadd72"},
                     {"title": "Hampir setiap hari", "payload": "gadd73"}
                                            
                      
                  ]) 
                
class ActionGADClose(Action):
    def name(self) -> Text:
        return "action_intent_gadClose"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          
          cekTotalScore = int(countMeasurement(sender_id, message_id))
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          
          if cekTotalScore >= "14.00":
             dispatcher.utter_message(text=message_confirmation) 
          else:
             dispatcher.utter_message(text=message_dass_Close)    
                
class ActionSTAIT(Action):
    def name(self) -> Text:
        return "action_intent_stait"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
              dispatcher.utter_message(text=message_intro_stait,buttons=[
                      {"title": "Mulai", "payload": "/startstait"},
                      {"title": "Batal", "payload": "/batal"}
                ])      
 
class ActionSTAIT1(Action):
    def name(self) -> Text:
        return "action_intent_stait1"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          
          dispatcher.utter_message(text=message_stait_1,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata11"},
                      {"title": "Sedikit", "payload": "stata12"},
                      {"title": "Lumayan", "payload": "stata13"},
                      {"title": "Sangat", "payload": "stata14"}
                                            
                      
                  ]) 



class ActionSTAIT2(Action):
    def name(self) -> Text:
        return "action_intent_stait2"

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
              
          dispatcher.utter_message(text=message_stait_2,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata21"},
                      {"title": "Sedikit", "payload": "stata22"},
                      {"title": "Lumayan", "payload": "stata23"},
                      {"title": "Sangat", "payload": "stata24"}
                                            
                      
                  ])   

class ActionSTAIT3(Action):
    def name(self) -> Text:
        return "action_intent_stait3"

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
              
          dispatcher.utter_message(text=message_stait_3,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata31"},
                      {"title": "Sedikit", "payload": "stata32"},
                      {"title": "Lumayan", "payload": "stata33"},
                      {"title": "Sangat", "payload": "stata34"}
                                            
                      
                  ])

class ActionSTAIT4(Action):
    def name(self) -> Text:
        return "action_intent_stait4"

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
              
          dispatcher.utter_message(text=message_stait_4,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata41"},
                      {"title": "Sedikit", "payload": "stata42"},
                      {"title": "Lumayan", "payload": "stata43"},
                      {"title": "Sangat", "payload": "stata44"}
                                            
                      
                  ])  

class ActionSTAIT5(Action):
    def name(self) -> Text:
        return "action_intent_stait5"

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
              
          dispatcher.utter_message(text=message_stait_5,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata51"},
                      {"title": "Sedikit", "payload": "stata52"},
                      {"title": "Lumayan", "payload": "stata53"},
                      {"title": "Sangat", "payload": "stata54"}
                                            
                      
                  ])  

class ActionSTAIT6(Action):
    def name(self) -> Text:
        return "action_intent_stait6"

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
              
          dispatcher.utter_message(text=message_stait_6,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stait61"},
                      {"title": "Sedikit", "payload": "stata62"},
                      {"title": "Lumayan", "payload": "stata63"},
                      {"title": "Sangat", "payload": "stata64"}
                                            
                      
                  ])  


class ActionSTAIT7(Action):
    def name(self) -> Text:
        return "action_intent_stait7"

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
              
          dispatcher.utter_message(text=message_stait_7,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata71"},
                      {"title": "Sedikit", "payload": "stata72"},
                      {"title": "Lumayan", "payload": "stata73"},
                      {"title": "Sangat", "payload": "stata74"}
                                            
                      
                  ])                           
          
          
class ActionSTAIT8(Action):
    def name(self) -> Text:
        return "action_intent_stait8"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          if cekTotalScore >= "24.00":
                dispatcher.utter_message(text=message_confirmation) 
          else:        
          
              
               dispatcher.utter_message(text=message_stait_8,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata81"},
                      {"title": "Sedikit", "payload": "stata82"},
                      {"title": "Lumayan", "payload": "stata83"},
                      {"title": "Sangat", "payload": "stata84"}
                                            
                      
                  ]) 
               
class ActionSTAIT9(Action):
    def name(self) -> Text:
        return "action_intent_stait9"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          if cekTotalScore >= "24.00":
                dispatcher.utter_message(text=message_confirmation) 
          else:        
          
              
               dispatcher.utter_message(text=message_stait_9,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata91"},
                      {"title": "Sedikit", "payload": "stata92"},
                      {"title": "Lumayan", "payload": "stata93"},
                      {"title": "Sangat", "payload": "stata94"}
                                            
                      
                  ])   

class ActionSTAIT10(Action):
    def name(self) -> Text:
        return "action_intent_stait10"

    def run(self, dispatcher: CollectingDispatcher,
              tracker: Tracker,
              domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
          message_id = tracker.latest_message.get("text") 
          sender_id =  tracker.sender_id
          cekCurrent = ValidateMeasurement(sender_id, message_id)
          cekTotalScore = countMeasurement(sender_id, message_id)
          if cekCurrent == 0:
              insertMeasurement(sender_id,message_id)
          else:
              deleteMeasurement(sender_id, message_id)
              insertMeasurement(sender_id,message_id)
          if cekTotalScore >= "24.00":
                dispatcher.utter_message(text=message_confirmation) 
          else:        
          
              
               dispatcher.utter_message(text=message_stait_10,buttons=[
                      {"title": "Tidak sama sekali", "payload": "stata101"},
                      {"title": "Sedikit", "payload": "stata102"},
                      {"title": "Lumayan", "payload": "stata103"},
                      {"title": "Sangat", "payload": "stata104"}
                                            
                      
                  ]) 
               
    class ActionGetInformation(Action):
        def name(self) -> Text:
            return "action_intent_information"

        def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
             
                   url ='https://www.mayoclinichealthsystem.org/hometown-health/speaking-of-health/tips-to-help-ease-anxiety' 
                   message_anxiety = 'Coba kamu buka link ini '+url
                   message_closing = 'Apakah kamu terbantu dengan sesi bersama Koncoku?'
                   dispatcher.utter_message(text=message_anxiety)
                   dispatcher.utter_message(text=message_closing,buttons=[
                          {"title": "Ya", "payload": "yaSurvey"},
                          {"title": "Tidak", "payload": "tidakSurvey"}
                          
                
                      ]) 
                   
    class ActionGetKonsultasi(Action):
         def name(self) -> Text:
             return "action_intent_konsultasi"

         def run(self, dispatcher: CollectingDispatcher,
                   tracker: Tracker,
                   domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
              
                    url ='https://ukp.psikologi.ugm.ac.id/' 
                    message_anxiety = 'Kamu bisa melihat informasi unit konsultasi UGM di  '+url
                    message_closing = 'Apakah kamu terbantu dengan sesi bersama Koncoku?'
                    dispatcher.utter_message(text=message_anxiety)
                    dispatcher.utter_message(text=message_closing,buttons=[
                           {"title": "Ya", "payload": "yaSurvey"},
                           {"title": "Tidak", "payload": "tidakSurvey"}
                           
                 
                       ]) 
                    
    class ActionSurvey(Action):
         def name(self) -> Text:
             return "action_intent_yasurvey"

         def run(self, dispatcher: CollectingDispatcher,
                   tracker: Tracker,
                   domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
              
             
                   
                    message_1 ='Apakah chatbot ini dapat membantu Anda untuk melakukan pemeriksaan dini gejala anxiety?'
                    dispatcher.utter_message(text=message_1,buttons=[
                           {"title": "Sangat membantu", "payload": "quizioner15"},
                           {"title": "Membantu", "payload": "quizioner14"},
                           {"title": "Cukup membantu", "payload": "quizioner13"},
                           {"title": "Kurang membantu", "payload": "quizioner12"},
                           {"title": "Tidak membantu", "payload": "quizioner11"},
                 
                       ])
    
    class ActionSurvey2(Action):
         def name(self) -> Text:
             return "action_intent_kuisioner2"

         def run(self, dispatcher: CollectingDispatcher,
                   tracker: Tracker,
                   domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
              
                    
                    message_id = tracker.latest_message.get("text") 
                    sender_id =  tracker.sender_id
                    cekCurrent = ValidateSurvey(sender_id, message_id)
                    
                    if cekCurrent == 0:
                        insertSurvey(sender_id,message_id)
                    else:
                        deleteSurvey(sender_id, message_id)
                        insertSurvey(sender_id,message_id) 
                   
                    message_1 ='Apakah chatbot ini mudah digunakan?'
                    dispatcher.utter_message(text=message_1,buttons=[
                           {"title": "Sangat mudah", "payload": "quizioner25"},
                           {"title": "Mudah", "payload": "quizioner24"},
                           {"title": "Cukup mudah", "payload": "quizioner23"},
                           {"title": "Kurang mudah", "payload": "quizioner22"},
                           {"title": "Tidak mudah", "payload": "quizioner21"},
                 
                       ])
                    
    class ActionSurvey3(Action):
          def name(self) -> Text:
              return "action_intent_kuisioner3"

          def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
               
                     
                     message_id = tracker.latest_message.get("text") 
                     sender_id =  tracker.sender_id
                     cekCurrent = ValidateSurvey(sender_id, message_id)
                     
                     if cekCurrent == 0:
                         insertSurvey(sender_id,message_id)
                     else:
                         deleteSurvey(sender_id, message_id)
                         insertSurvey(sender_id,message_id) 
                    
                     message_1 ='Apakah anda mau merekomendasikan chatbot ini ke teman-teman?'
                     dispatcher.utter_message(text=message_1,buttons=[
                            {"title": "Sangat mau ", "payload": "quizioner35"},
                            {"title": "Mau", "payload": "quizioner34"},
                            {"title": "Cukup mau", "payload": "quizioner33"},
                            {"title": "Kurang mau", "payload": "quizioner32"},
                            {"title": "Tidak mau", "payload": "quizioner31"},
                  
                        ])
                     
                     
    
    
    class ActionSurveyClosing(Action):
          def name(self) -> Text:
              return "action_intent_closingsurvey"

          def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
               
                     
                     message_id = tracker.latest_message.get("text") 
                     sender_id =  tracker.sender_id
                     cekCurrent = ValidateSurvey(sender_id, message_id)
                     
                     if cekCurrent == 0:
                         insertSurvey(sender_id,message_id)
                     else:
                         deleteSurvey(sender_id, message_id)
                         insertSurvey(sender_id,message_id) 
                    
                     message_1 ='Terima kasih atas feedbacknya. Semoga Koncoku bisa membantu ya jaga kesehatan sampai jumpa dilain waktu'
                     dispatcher.utter_message(text=message_1)
                     
    class ActionTidakSurvey(Action):
          def name(self) -> Text:
              return "action_intent_tidaksurvey"

          def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
               
              
                    
                     message_1 ='Terima kasih, salam sehat selalu... God bless you'
                     dispatcher.utter_message(text=message_1)
                     
                     
    class ActionInput(Action):
          def name(self) -> Text:
              return "action_intent_input"

          def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
               
                    message_id = tracker.latest_message.get("text") 
                    sender_id =  tracker.sender_id
                    is_anxiety='Input'
                    
                    insertCurhat(sender_id, message_id, is_anxiety)
                    message_1 ='Terima kasih atas masukannya, salam sehat selalu... God bless you'
                    dispatcher.utter_message(text=message_1)
     
    class ActionFallback(Action):
              def name(self) -> Text:
                  return "action_default_fallback"

              def run(self, dispatcher: CollectingDispatcher,
                        tracker: Tracker,
                        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                   
                  
                        
                         message_1 ='Nah, Koncoku belum ngerti nih maksudnya apa. Kamu bisa sampaikan langsung ke pemiliknya: https://wa.me/6281915548083, thank you'
                         dispatcher.utter_message(text=message_1)
         
