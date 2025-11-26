#!/usr/bin/env python3
"""
TikTok Live Streamer Search - Standalone Script
Busca streamers en vivo y muestra sus display_ids en terminal
"""
import os
import sys
import json
from dotenv import load_dotenv
from tikapi import TikAPI, ValidationException, ResponseException

# Load environment variables
load_dotenv()

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
        print("❌ Error: El texto proporcionado no es un JSON válido.")
        return []

def extraer_display_ids(json_str):
    """Extract display IDs from TikAPI search response"""
    display_ids = []
    try:
        datos = json.loads(json_str)

        for item in datos.get("data", []):
            display_id = item.get("live_info", {}).get("owner", {}).get("display_id")
            if display_id:
                print(f"  📺 @{display_id}")
                display_ids.append(display_id)

    except (json.JSONDecodeError, TypeError) as e:
        print(f"❌ Error procesando el JSON: {e}")

    return display_ids

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
        print(f"❌ Error procesando el JSON: {e}")

    return lista

def main():
    """Main function"""
    print("=" * 70)
    print("🔴 TikTok Live Streamer Search")
    print("=" * 70)

    # Get credentials from environment
    api_key = os.getenv("TIKAPI_KEY")
    account_key = os.getenv("TIKAPI_ACCOUNT_KEY")

    if not api_key or not account_key:
        print("❌ Error: Credenciales de TikAPI no configuradas")
        print("   Por favor configura TIKAPI_KEY y TIKAPI_ACCOUNT_KEY en .env")
        sys.exit(1)

    # Get query from command line or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "maquillaje"

    print(f"\n🔍 Buscando streamers en vivo con query: '{query}'")
    print("-" * 70)

    try:
        # Initialize TikAPI
        api = TikAPI(api_key)
        user = api.user(accountKey=account_key)

        # Search for live streams
        print("\n1️⃣ Buscando transmisiones en vivo...")
        response = user.live.search(query=query)

        print("\n📋 Streamers de búsqueda directa:")
        search_display_ids = extraer_display_ids(response.text)

        # Extract room IDs for recommendations
        respose_rooms_ids = extraer_room_ids(response.text)
        print(f"\n🏠 Encontrados {len(respose_rooms_ids)} rooms para obtener recomendaciones")

        # Get recommended streamers
        print("\n2️⃣ Obteniendo streamers recomendados...")
        lista = []
        for i, room_id in enumerate(respose_rooms_ids, 1):
            try:
                print(f"   Procesando room {i}/{len(respose_rooms_ids)}...", end="\r")
                response1 = user.live.recommend(room_id=str(room_id))
                extraer_display_ids_recommended(response1.text, lista)
            except ValidationException as e:
                print(f"\n   ⚠️  Validation error en room {room_id}: {e.field}")
            except ResponseException as e:
                print(f"\n   ⚠️  Response error en room {room_id}: {e.response.status_code}")

        print("\n")  # New line after progress

        # Combine and remove duplicates
        all_display_ids = search_display_ids + lista
        lista_unica = list(dict.fromkeys(all_display_ids))

        # Print results
        print("=" * 70)
        print(f"✅ RESULTADO FINAL: {len(lista_unica)} streamers únicos encontrados")
        print("=" * 70)

        for i, display_id in enumerate(lista_unica, 1):
            print(f"{i:3d}. @{display_id}")

        print("=" * 70)
        print(f"📊 Estadísticas:")
        print(f"   - Búsqueda directa: {len(search_display_ids)} streamers")
        print(f"   - Recomendados: {len(lista)} streamers")
        print(f"   - Total único: {len(lista_unica)} streamers")
        print("=" * 70)

    except ValidationException as e:
        print(f"\n❌ Error de validación: {e}")
        print(f"   Campo: {e.field}")
        sys.exit(1)
    except ResponseException as e:
        print(f"\n❌ Error de respuesta: {e}")
        print(f"   Status code: {e.response.status_code}")
        if e.response.status_code == 401:
            print("   💡 Verifica que tus credenciales de TikAPI sean correctas")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
