from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import pickle
from .customtools import ModelTools
import re

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

            context = {
                'symptoms': clean_symptoms,
                'disease': predicted_disease
            }
        


    return render(request, 'model1.html', context)


def results(request):
    symptoms = request.GET.get('symptoms', '').split(',')
    clean_symtomps = tool.preprocessing(symptoms=symptoms)
    predicted_disease = tool.predict(input_symptoms=clean_symtomps)

    # prediction = pickle.load(open('pipe.pkl' , 'rb'))

    return render(request, "update_profile.html", context)