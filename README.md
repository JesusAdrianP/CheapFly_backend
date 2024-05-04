Para ejecutar el proyecto:

En la ruta CheapFly_backend/ ejecutar el siguiente comando:  
python -m venv venv  

Para instalar las librerías y requerimientos del proyecto, primero activar el ambiente virtual:  
En windows:    
source venv/Scripts/activate  
En linux:    
source venv/bin/activate  

Luego instalar los requerimientos con pip:  
pip install -r requirements.txt  

Debe solicitar una api_key en openai, luego crear un archivo secrets.json en la carpeta del proyecto, con la siguiente estructura:  

{
    "OPENAI_KEY": your_api_key
}  

Para correr el servidor:  
python manage.py runserver
