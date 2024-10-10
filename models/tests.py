from django.test import TestCase
from customtools import ModelTools
# Create your tests here.

rajesh = ModelTools()

test_input = rajesh.preprocessing(['yellowish_skin', 'headache', 'yellowing_of_eyes', 'yellow_urine', 'mild_fever'])
# tfidf_input = rajesh.tfidf.transform([test_input])
print(rajesh.predict(test_input))


