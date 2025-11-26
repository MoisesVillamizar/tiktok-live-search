"""API package - Example code for TikAPI usage"""
# This file contains example functions for reference
# The actual API routes are in routes.py

import json
from tikapi import TikAPI, ValidationException, ResponseException

def extraer_room_ids(json_texto):
    """Extract room IDs from TikAPI search response"""
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

def extraer_display_ids(json_str):
    """Extract display IDs from TikAPI search response"""
    try:
        datos = json.loads(json_str)

        for item in datos.get("data", []):
            display_id = item.get("live_info", {}).get("owner", {}).get("display_id")
            if display_id:
                print(display_id)

    except (json.JSONDecodeError, TypeError) as e:
        print("Error procesando el JSON:", e)

def extraer_display_ids_recommended(json_str, lista=None):
    """Extract display IDs from TikAPI recommended response"""
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

# Example usage (commented out to prevent execution on import):
"""
api = TikAPI("HTe7e6Fq7dzbC7TC7gKBZwZ6IjuYEMBaDsWzcfXqwnpyHxGc")
User = api.user(accountKey="mNK7QKSW7sZgOSNaRcI1pqGk9L1p68X36mh5ezEH0ro5FLmg")

try:
    response = User.live.search(query="maquillaje")
except ValidationException as e:
    print(e, e.field)
except ResponseException as e:
    print(e, e.response.status_code)

extraer_display_ids(response.text)
respose_rooms_ids = extraer_room_ids(response.text)

lista = []
for room_id in respose_rooms_ids:
    try:
        response1 = User.live.recommend(room_id=str(room_id))
        extraer_display_ids_recommended(response1.text, lista)
    except ValidationException as e:
        print(e, e.field)
    except ResponseException as e:
        print(e, e.response.status_code)

lista_unica = list(dict.fromkeys(lista))

for display_id in lista_unica:
    print(display_id)
"""

