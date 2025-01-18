from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import pickle
from .customtools import ModelTools
import re
from transformers import pipeline
from PIL import Image
import io

tool = ModelTools()



def model(request):
    return HttpResponse("This is the models page")

def multidisease(request):
    context = {}  

    if request.method == 'POST':
        symptoms = []
        for i in "abcdefghijklmonpqr":
            symptom = request.POST.get(f'symptom_{i}')
            if symptom:
                symptoms.append(symptom)
        
        if symptoms:
            clean_symptoms = tool.preprocessing(symptoms=symptoms)
            predicted_disease = tool.predict(input_symptoms=clean_symptoms)
            description = tool.disease_description[predicted_disease]
            # description = tool.description_dict[predicted_disease]

            context = {
                'symptoms': clean_symptoms,
                'disease': predicted_disease,
                'description':description
            }
        


    return render(request, 'model1.html', context)


def results(request):
    symptoms = request.GET.get('symptoms', '').split(',')
    clean_symtomps = tool.preprocessing(symptoms=symptoms)
    predicted_disease = tool.predict(input_symptoms=clean_symtomps)


    # prediction = pickle.load(open('pipe.pkl' , 'rb'))

    return render(request, "update_profile.html", context)


def skin_disease(request):
    predictions = []
    
    if request.method == 'POST' and request.FILES.get('skin_image'):
        # Get the uploaded image
        image_file = request.FILES['skin_image']
        
        try:
            # Convert the uploaded file to PIL Image
            image = Image.open(io.BytesIO(image_file.read()))
            
            # Initialize the pipeline
            pipe = pipeline("image-classification", 
                          model="kaanyvvz/ky-finetuned-skindiseaseicthuawei32")
            
            # Get predictions
            results = pipe(image)
            
            # Extract top 5 predictions
            predictions = [
                {
                    'label': result['label'],
                    'score': f"{result['score']*100:.2f}%"
                }
                for result in results[:5]
            ]
            
        except Exception as e:
            predictions = [{'label': f'Error: {str(e)}', 'score': ''}]
    
    context = {
        "disease": predictions
    }
    return render(request, "skin_disease.html", context)