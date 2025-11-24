import requests
from flask import Flask, render_template, request

aplicacion = Flask(__name__)

CLAVE_API = "2mVbF6kxK7xneQO7arHpkEhocL3fieky45ymC89t" 
URL_BASE_BUSQUEDA = "https://api.nal.usda.gov/fdc/v1/foods/search"
URL_BASE_DETALLE = "https://api.nal.usda.gov/fdc/v1/food/"


def obtener_fdc_id_y_calorias_base(nombre_ingrediente):
    """
    Busca el FDC ID para un ingrediente y luego obtiene las calorías por 100g.
    Devuelve las calorías por 100g (kcal) y el nombre de la descripción del alimento.
    """
    parametros_busqueda = {
        "api_key": CLAVE_API,
        "query": nombre_ingrediente,
        "pageSize": 1
    }
    
    try:
        respuesta_busqueda = requests.get(URL_BASE_BUSQUEDA, params=parametros_busqueda)
        
        if respuesta_busqueda.status_code != 200:
            print(f"Error de estado HTTP en búsqueda: {respuesta_busqueda.status_code}")
            return None

        resultados = respuesta_busqueda.json()
        
        if not resultados.get('foods'):
            return None 
        
        id_fdc = resultados['foods'][0]['fdcId']
        
        url_detalle = f"{URL_BASE_DETALLE}{id_fdc}"
        parametros_detalle = {"api_key": CLAVE_API} 

        respuesta_detalle = requests.get(url_detalle, params=parametros_detalle)
        
        if respuesta_detalle.status_code != 200:
            print(f"Error de estado HTTP en detalle: {respuesta_detalle.status_code}")
            return None

        datos_detalle = respuesta_detalle.json()
        
        for nutriente in datos_detalle.get('foodNutrients', []):
            if nutriente.get('nutrient', {}).get('name') == "Energy":
                return {
                    "descripcion": datos_detalle.get('description'),
                    "calorias_por_100g": nutriente.get('amount', 0)
                } 

        return None 

    except requests.exceptions.RequestException as e:
        print(f"Error de Conexión (fuera de HTTP status): {e}")
        return None

@aplicacion.route('/', methods=['GET'])
def indice():
    """Muestra la interfaz principal de la calculadora (sin resultados iniciales)."""
    return render_template('index.html', total_calorias=None, detalle_ingredientes=None)

@aplicacion.route('/calculate', methods=['POST'])
def calcular():
    calorias_totales = 0
    detalle_ingredientes = []
    ingredientes_formulario = []
    

    for i in range(1, 11):
        nombre_key = f'nombre_{i}'
        gramos_key = f'gramos_{i}'
        
        nombre = request.form.get(nombre_key, '').strip()
        gramos_str = request.form.get(gramos_key, '0').strip()
        
        try:
            gramos = float(gramos_str)
        except ValueError:
            gramos = 0
        
        if nombre and gramos > 0:
            ingredientes_formulario.append({
                "nombre": nombre,
                "gramos": gramos,
                "nombre_campo": nombre_key, 
                "gramos_campo": gramos_key
            })
            
            datos_base = obtener_fdc_id_y_calorias_base(nombre)
            
            if datos_base and datos_base["calorias_por_100g"] > 0:
                factor = gramos / 100
                contribucion_calorias = datos_base["calorias_por_100g"] * factor
                calorias_totales += contribucion_calorias

                detalle_ingredientes.append({
                    "nombre": nombre,
                    "gramos": gramos,
                    "calorias": round(contribucion_calorias, 2),
                    "encontrado": True
                })
            else:
                detalle_ingredientes.append({
                    "nombre": f"{nombre} (No encontrado o 0 Kcal)",
                    "gramos": gramos,
                    "calorias": 0,
                    "encontrado": False
                })

    if not ingredientes_formulario:
        return render_template('index.html', total_calorias=None, detalle_ingredientes=None, submitted_data={})
    return render_template('index.html',
                            total_calorias=round(calorias_totales, 2),
                            detalle_ingredientes=detalle_ingredientes,
                            submitted_data={k: request.form.get(k) for k in request.form}
                            )

if __name__ == '__main__':
    aplicacion.run(debug=True)