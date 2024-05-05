from bs4 import BeautifulSoup
import json
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
from datetime import datetime

# Create your views here.
base_url = "https://www.kayak.com.co/flights/"
flights = []

def get_secret_key():
    with open('secrets.json') as f:
        secrets = json.load(f)
    return secrets['OPENAI_KEY']

api_key = get_secret_key()
openai.api_key= api_key

def transformPricesToInt(price):
    return price[1:].replace(".", "")

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
            if adults is not None and int(adults)>1:
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
            print(return_date)
            url = f"{base_url}{cities}/{departure_date}?sort=price_a"
            valid_url = True
            if adults is not None and int(adults)>1:
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

def counting_scales(scales):
    elements_of_scales = scales.split(",")
    number_of_scales = 0
    if scales != "":
        number_of_scales = len(elements_of_scales)
    else:
        number_of_scales = 0
    return number_of_scales



def dateParser(date):
    date_format = datetime.strptime(date,"%d-%m-%Y")
    date_parsed = date_format.strftime("%Y-%m-%d")
    return date_parsed

def find_div_element_in_list(list_of_elements, class_):
    list_of_div_elements = []
    for i in list_of_elements:
        div_element = i.find("div", class_=class_)
        list_of_div_elements.append(div_element)
    return list_of_div_elements

def get_general_info(url, more_than_one_passeger=False, round_trip = False):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    flights_rows = driver.find_elements(By.XPATH,"//div[@class='nrc6 nrc6-mod-pres-default']")
    general_info = []

    for webElement in flights_rows:
        if more_than_one_passeger:
            if round_trip:
                elementHTML= webElement.get_attribute('outerHTML')
                elementSoup = BeautifulSoup(elementHTML,'html.parser')
                price = elementSoup.find("div", class_="f8F1-small-emph f8F1-multiple-ptc-total-price")
                airline = elementSoup.find("div", class_="J0g6-operator-text")
                flight_time_element = elementSoup.find_all("div", class_="xdW8 xdW8-mod-full-airport")
                flight_time = find_div_element_in_list(flight_time_element, "vmXl vmXl-mod-variant-default")
                scales_element = elementSoup.find_all("div",class_="JWEO")
                scales = find_div_element_in_list(scales_element, "c_cgF c_cgF-mod-variant-full-airport")
                outbound_trip_number_of_scales = counting_scales(scales[0].text)
                return_number_of_scales = counting_scales(scales[1].text)
                offer_button = elementSoup.find('div', class_="dOAU-main-btn-wrap")
                offer_class = offer_button.find('div', class_="oVHK")
                offer_link_element = offer_class.find('a')
                offer_link = f"www.kayak.com.co{offer_link_element.get("href")}"
                general_info.append({"airline": airline.text,"price":price.text, "outbound_trip_time":flight_time[0].text,"return_trip_time":flight_time[1].text,"outbound_trip_number_of_scales": outbound_trip_number_of_scales, "outbound_trip_scales": scales[0].text,"return_trip_number_of_scales": return_number_of_scales, "return_trip_scales": scales[1].text, "offer_link": offer_link})
            else:
                elementHTML= webElement.get_attribute('outerHTML')
                elementSoup = BeautifulSoup(elementHTML,'html.parser')
                price = elementSoup.find("div", class_="f8F1-small-emph f8F1-multiple-ptc-total-price")
                airline = elementSoup.find("div", class_="J0g6-operator-text")
                flight_time_element = elementSoup.find("div", class_="xdW8 xdW8-mod-full-airport")
                flight_time = flight_time_element.find("div", class_="vmXl vmXl-mod-variant-default")
                scales_element = elementSoup.find("div",class_="JWEO")
                scales = scales_element.find("div", class_="c_cgF c_cgF-mod-variant-full-airport")
                number_of_scales = counting_scales(scales.text)
                offer_button = elementSoup.find('div', class_="dOAU-main-btn-wrap")
                offer_class = offer_button.find('div', class_="oVHK")
                offer_link_element = offer_class.find('a')
                offer_link = f"www.kayak.com.co{offer_link_element.get("href")}"
                general_info.append({"airline": airline.text,"price":price.text, "flight_time":flight_time.text,"number_of_scales": number_of_scales, "scales": scales.text, "offer_link": offer_link})
        else:
            if round_trip:
                elementHTML= webElement.get_attribute('outerHTML')
                elementSoup = BeautifulSoup(elementHTML,'html.parser')
                price = elementSoup.find("div", class_="f8F1-price-text")
                airline = elementSoup.find("div", class_="J0g6-operator-text")
                flight_time_element = elementSoup.find_all("div", class_="xdW8 xdW8-mod-full-airport")
                flight_time = find_div_element_in_list(flight_time_element, "vmXl vmXl-mod-variant-default")
                scales_element = elementSoup.find_all("div",class_="JWEO")
                scales = find_div_element_in_list(scales_element, "c_cgF c_cgF-mod-variant-full-airport")
                outbound_trip_number_of_scales = counting_scales(scales[0].text)
                return_number_of_scales = counting_scales(scales[1].text)
                offer_button = elementSoup.find('div', class_="dOAU-main-btn-wrap")
                offer_class = offer_button.find('div', class_="oVHK")
                offer_link_element = offer_class.find('a')
                offer_link = f"www.kayak.com.co{offer_link_element.get("href")}"
                general_info.append({"airline": airline.text,"price":price.text, "outbound_trip_time":flight_time[0].text,"return_trip_time":flight_time[1].text,"outbound_trip_number_of_scales": outbound_trip_number_of_scales, "outbound_trip_scales": scales[0].text,"return_trip_number_of_scales": return_number_of_scales, "return_trip_scales": scales[1].text, "offer_link": offer_link})
            else:
                elementHTML= webElement.get_attribute('outerHTML')
                elementSoup = BeautifulSoup(elementHTML,'html.parser')
                price = elementSoup.find("div", class_="f8F1-price-text")
                airline = elementSoup.find("div", class_="J0g6-operator-text")
                flight_time_element = elementSoup.find("div", class_="xdW8 xdW8-mod-full-airport")
                flight_time = flight_time_element.find("div", class_="vmXl vmXl-mod-variant-default")
                scales_element = elementSoup.find("div",class_="JWEO")
                scales = scales_element.find("div", class_="c_cgF c_cgF-mod-variant-full-airport")
                number_of_scales = counting_scales(scales.text)
                offer_button = elementSoup.find('div', class_="dOAU-main-btn-wrap")
                offer_class = offer_button.find('div', class_="oVHK")
                offer_link_element = offer_class.find('a')
                offer_link = f"www.kayak.com.co{offer_link_element.get("href")}"
                general_info.append({"airline": airline.text,"price":price.text, "flight_time":flight_time.text,"number_of_scales": number_of_scales, "scales": scales.text, "offer_link": offer_link})

    driver.quit()
    return general_info


# Verifica que la solicitud fue exitosa

class GetFlightsView(APIView):
    def get(self, request):
        departure_date_parsed = None
        return_date_parsed = None
        global flights
        origin = ask_open_ai(request.GET.get('city_of_origin'))
        destination = ask_open_ai(request.GET.get('destination_city'))
        departure_date = request.GET.get('departure_date')
        return_date = request.GET.get('return_date')
        if departure_date is not None:
            departure_date_parsed = dateParser(departure_date)
            if return_date is not None:
                return_date_parsed = dateParser(return_date)
        adults = request.GET.get('adults')
        children = request.GET.get('children')
        final_url = set_url(origin=origin,destination=destination,departure_date=departure_date_parsed,return_date=return_date_parsed,adults=adults,children=children)
        if final_url[0] == True:
            print("url: ",final_url[1])
            if (adults is not None and int(adults)>1) or children is not None:
                if return_date is not None:
                    general_info = get_general_info(final_url[1],more_than_one_passeger=True, round_trip= True)
                    flights = general_info
                    return Response(general_info, status=status.HTTP_200_OK)

                else:
                    general_info = get_general_info(final_url[1],more_than_one_passeger=True, round_trip=False)
                    flights = general_info
                    return Response(general_info, status=status.HTTP_200_OK)
            else:
                if return_date is not None:
                    print("url: ",final_url[1])
                    general_info = get_general_info(final_url[1], round_trip= True)
                    flights = general_info
                    return Response(general_info, status=status.HTTP_200_OK)
                else:
                    print("url: ",final_url[1])
                    general_info = get_general_info(final_url[1], round_trip= False)
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
        number_of_scales = request.GET.get('number_of_scales')
        if airline is not None:
            queryset = [flight for flight in queryset if airline.lower() in flight.get('airline').lower()]
        if minimun_price is not None:
            queryset = [flight for flight in queryset if int(transformPricesToInt(flight.get('price'))) > int(minimun_price)]
        if maximun_price is not None:
            queryset = [flight for flight in queryset if int(transformPricesToInt(flight.get('price'))) < int(maximun_price)]
        if number_of_scales is not None:
            queryset = [flight for flight in queryset if flight.get('number_of_scales') == int(number_of_scales)]
        if len(queryset)>0:
            return Response(queryset, status=status.HTTP_200_OK)
        elif len(queryset)==0:
            return Response({'messagge':'No flights to show'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'messagge':'An error has ocurred'}, status=status.HTTP_404_NOT_FOUND)

