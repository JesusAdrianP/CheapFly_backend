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
from .filters import CustomFilter
from django_filters import rest_framework as filters
from .serializers import FlightSerializer
# Create your views here.
api_key = "openai_key"
openai.api_key=api_key
base_url = "https://www.kayak.com.co/flights/"
flights = []

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

def set_url(origin="", destination="", departure_date="", return_date="",adults=1,children=0):
    valid_url = False
    cities = ""
    url = ""
    if origin is not None and destination is not None:
        cities = f"{origin}-{destination}"
        url = f"{base_url}{cities}?sort=price_a"
        if departure_date is not None and return_date is not None:
            url = f"{base_url}{cities}/{departure_date}/{return_date}?sort=price_a"
            valid_url = True
            if adults is not None:
                url = f"{base_url}{cities}/{departure_date}/{return_date}/{adults}adults?sort=price_a"
                if children is not None:
                    if children>0:
                        number_of_children = "children"
                        for number in range(children):
                            number_of_children += "-11"
                        print("niños: ",number_of_children) 
                        url = f"{base_url}{cities}/{departure_date}/{return_date}/{adults}adults/{number_of_children}?sort=price_a"
            else:
                if children is not None:
                    if children>0:
                        number_of_children = "children"
                        for number in range(children):
                            number_of_children += "-11"
                        print("niños: ",number_of_children) 
                        url = f"{base_url}{cities}/{departure_date}/{return_date}/1adults/{number_of_children}?sort=price_a"  
        elif return_date is None:
            url = f"{base_url}{cities}/{departure_date}?sort=price_a"
            valid_url = True
            if adults is not None:
                url = f"{base_url}{cities}/{departure_date}/{return_date}/{adults}adults?sort=price_a"
                if children is not None:
                    if children>0:
                        number_of_children = "children"
                        for number in range(children):
                            number_of_children += "-11"
                        print("niños: ",number_of_children) 
                        url = f"{base_url}{cities}/{departure_date}/{return_date}/{adults}adults/{number_of_children}?sort=price_a"
            else:
                if children is not None:
                    if children>0:
                        number_of_children = "children"
                        for number in range(children):
                            number_of_children += "-11"
                        print("niños: ",number_of_children) 
                        url = f"{base_url}{cities}/{departure_date}/{return_date}/1adults/{number_of_children}?sort=price_a" 
        else :
            valid_url = False
    else:
        valid_url = False
    return [valid_url, url]



def get_general_info(url, more_than_one_passeger=False):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    flights_rows = driver.find_elements(By.XPATH,"//div[@class='nrc6 nrc6-mod-pres-default']")
    general_info = []

    for webElement in flights_rows:
        if more_than_one_passeger:
            elementHTML= webElement.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML,'html.parser')
            price = elementSoup.find("div", class_="f8F1-small-emph f8F1-multiple-ptc-total-price")
            airline = elementSoup.find("div", class_="J0g6-operator-text")
            flight_time_element = elementSoup.find("div", class_="xdW8 xdW8-mod-full-airport")
            flight_time = flight_time_element.find("div", class_="vmXl vmXl-mod-variant-default")
            print(flight_time)
            general_info.append({"airline": airline.text,"price":price.text, "flight_time":flight_time.text})
        else:
            elementHTML= webElement.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML,'html.parser')
            price = elementSoup.find("div", class_="f8F1-price-text")
            airline = elementSoup.find("div", class_="J0g6-operator-text")
            flight_time_element = elementSoup.find("div", class_="xdW8 xdW8-mod-full-airport")
            flight_time = flight_time_element.find("div", class_="vmXl vmXl-mod-variant-default")
            print(flight_time)
            general_info.append({"airline": airline.text,"price":price.text, "flight_time":flight_time.text})

    driver.quit()
    return general_info


# Verifica que la solicitud fue exitosa

class GetFlightsView(APIView):
    def get(self, request):
        global flights
        origin = request.GET.get('ciudad_origen')
        destination = request.GET.get('ciudad_destino')
        date = request.GET.get('fecha')
        adults = request.GET.get('adultos')
        children = request.GET.get('niños')
        final_url = set_url(origin=origin,destination=destination,departure_date=date,adults=adults,children=children)
        if final_url[0] == True:
            print("url: ",final_url[1])
            if adults is not None or children is not None:
                general_info = get_general_info(final_url[1],more_than_one_passeger=True)
                flights = general_info
                return Response(general_info, status=status.HTTP_200_OK)
            else:
                print("url: ",final_url[1])
                general_info = get_general_info(final_url[1])
                flights = general_info
                return Response(general_info, status=status.HTTP_200_OK)

        else: 
            return Response({'error':'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
        

class FilterFlightsView(APIView):
    def get(self, request):
        queryset = flights
        airline = request.GET.get('airline')
        minimun_price = request.GET.get('minimun_price')
        maximun_price = request.GET.get('maximun_price')
        if airline is not None:
            queryset = [flight for flight in queryset if flight.get('airline').lower() == airline.lower()]
        if maximun_price is not None:
            queryset = [flight for flight in queryset if int(flight.get('price')[1:].replace(".", "")) < int(maximun_price.replace(".", ""))]

        if len(queryset)>0:
            return Response(queryset, status=status.HTTP_200_OK)
        elif len(queryset)==0:
            return Response({'messagge':'No flights to show'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'messagge':'An error has ocurred'}, status=status.HTTP_404_NOT_FOUND)

