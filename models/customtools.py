import re
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# from sklearn.feature_extraction.text import TfidfVectorizer
import pickle


class ModelTools:
    def __init__(self):
        self.disease_dict = {0: 'GERD',
                            1: 'hepatitis A',
                            2: 'Hypothyroidism',
                            3: 'Chicken pox',
                            4: 'Diabetes ',
                            5: 'Dimorphic hemmorhoids(piles)',
                            6: 'Hypertension ',
                            7: 'Drug Reaction',
                            8: 'Arthritis',
                            9: 'Pneumonia',
                            10: 'Malaria',
                            11: 'Allergy',
                            12: 'Gastroenteritis',
                            13: 'Urinary tract infection',
                            14: 'Psoriasis',
                            15: 'Hypoglycemia',
                            16: 'Impetigo',
                            17: 'AIDS',
                            18: 'Varicose veins',
                            19: 'Paralysis (brain hemorrhage)',
                            20: 'Alcoholic hepatitis',
                            21: 'Tuberculosis',
                            22: 'Chronic cholestasis',
                            23: 'Acne',
                            24: 'Fungal infection',
                            25: 'Bronchial Asthma',
                            26: 'Hyperthyroidism',
                            27: 'Hepatitis B',
                            28: 'Heart attack',
                            29: 'Migraine',
                            30: '(vertigo) Paroymsal  Positional Vertigo',
                            31: 'Common Cold',
                            32: 'Peptic ulcer diseae',
                            33: 'Typhoid',
                            34: 'Cervical spondylosis',
                            35: 'Osteoarthristis',
                            36: 'Jaundice',
                            37: 'Hepatitis C',
                            38: 'Dengue',
                            39: 'Hepatitis E',
                            40: 'Hepatitis D'}
        # self.tfidf = pickle.load(open('vectorizer.pkl' , 'rb') , protocol=2)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        with fs.open('ml_models/vectorizer.pkl', 'rb') as f:
            self.tfidf = pickle.load(f)
        with fs.open('ml_models/pipe.pkl' , 'rb') as f:
            self.predict_pipe = pickle.load(f)
        

    @staticmethod
    def preprocessing(symptoms):
        symptoms = ','.join(symptoms)
        symptoms = re.sub(r'[\s_]+' , ' ' , symptoms)
        tokens = [token.strip().lower() for token in symptoms.split(',')]   
        tokens = ','.join(tokens) 
        return tokens

    def predict(self , input_symptoms):
        user_tfidf = self.tfidf.transform([input_symptoms])
        predicted_disease = self.predict_pipe.predict(user_tfidf)
        return self.disease_dict[predicted_disease[0]]

        


