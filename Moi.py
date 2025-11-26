#!/usr/bin/env python3
import json
import sys
from tikapi import TikAPI, ValidationException, ResponseException

def extraer_room_ids(json_texto):
    try:
        datos = json.loads(json_texto)
        room_ids = []

        for item in datos.get("data", []):
            room_info = item.get("live_info", {}).get("owner", {}).get("own_room", {})
            ids = room_info.get("room_ids", [])
            room_ids.extend(ids)

        return room_ids

    except json.JSONDecodeError:
        print("Error: El texto proporcionado no es un JSON válido.")
        return []

def extraer_display_ids(json_str, lista=None):
    """
    Extrae los 'display_id' de cada objeto en 'data'.
    """
    if lista is None:
        lista = []
    try:
        datos = json.loads(json_str)

        for item in datos.get("data", []):
            display_id = item.get("live_info", {}).get("owner", {}).get("display_id")
            if display_id:
                lista.append(str(display_id))

    except (json.JSONDecodeError, TypeError) as e:
        print("Error procesando el JSON:", e)

    return lista

def extraer_display_ids_recommended(json_str, lista=None):
    """
    Extrae los 'display_id' de cada objeto en 'data' de recomendados.
    """
    if lista is None:
        lista = []
    try:
        datos = json.loads(json_str)

        for item in datos.get("data", []):
            display_id = item.get("owner", {}).get("display_id")
            if display_id:
                lista.append(str(display_id))

    except (json.JSONDecodeError, TypeError) as e:
        print("Error procesando el JSON:", e)

    return lista

def main():
    # Obtener query de argumentos o usar default
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "tap"

    print(f"Buscando streamers para: {query}")
    print("-" * 40)

    api = TikAPI("HTe7e6Fq7dzbC7TC7gKBZwZ6IjuYEMBaDsWzcfXqwnpyHxGc")
    User = api.user(
        accountKey="mNK7QKSW7sZgOSNaRcI1pqGk9L1p68X36mh5ezEH0ro5FLmg"
    )

    lista = []

    try:
        response = User.live.search(query=query)

        # Extraer display_ids de la búsqueda
        extraer_display_ids(response.text, lista)

        # Extraer room_ids para recomendaciones
        respose_rooms_ids = extraer_room_ids(response.text)

        # Obtener recomendados de cada room
        for room_id in respose_rooms_ids:
            try:
                response1 = User.live.recommend(room_id=str(room_id))
                extraer_display_ids_recommended(response1.text, lista)

            except ValidationException as e:
                print(f"Error de validación: {e}, campo: {e.field}")

            except ResponseException as e:
                print(f"Error de respuesta: {e}, status: {e.response.status_code}")

    except ValidationException as e:
        print(f"Error de validación: {e}, campo: {e.field}")
        sys.exit(1)

    except ResponseException as e:
        print(f"Error de respuesta: {e}, status: {e.response.status_code}")
        sys.exit(1)

    # Eliminar duplicados
    lista_unica = list(dict.fromkeys(lista))

    print(f"\nTotal: {len(lista_unica)} streamers encontrados\n")

    # Imprimir usernames
    for display_id in lista_unica:
        print(display_id)

if __name__ == "__main__":
    main()