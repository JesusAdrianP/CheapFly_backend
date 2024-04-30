from bs4 import BeautifulSoup
import openai
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
api_key = "openai_key"
openai.api_key=api_key

def ask_open_ai(city, model="gpt-3.5-turbo-16k"):
    prompt = f'''Cuál es la abreviatura IATA de {city}, responde solo con la abreviatura, no digas nada más'''

    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens= 300,
        n=1
    )
    answer = response.choices[0].message
    if answer:
        message = answer.content
    else:
        message = "Sin respuesta"
    return message

url = ""

# Verifica que la solicitud fue exitosa

class TestView(APIView):
    def post(self, request):
        data = request.data
        cities= f"{data.get('ciudad_origen')}-{data.get('ciudad_destino')}"
        date = data.get('fecha')
        url = f"https://www.kayak.com.co/flights/{cities}/{date}?sort=bestflight_a"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        flights_rows = driver.find_elements(By.XPATH,"//div[@class='nrc6 nrc6-mod-pres-default']")

        general_info = []
        for webElement in flights_rows:
            elementHTML= webElement.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML,'html.parser')
            price = elementSoup.find("div", class_="f8F1-price-text")
            airline = elementSoup.find("div", class_="J0g6-operator-text")
            general_info.append({"airline": airline.text,"price":price.text})
        return Response(general_info, status=status.HTTP_200_OK)
    
