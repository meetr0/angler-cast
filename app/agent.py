# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-98ad64e09af9")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types

MODEL = "gemini-3.8-flash"
GCP_PROJECT_ID = "qwiklabs-gcp-04-98ad64e09af9"
COLLECTION_NAME = "fishing_spots"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client pinned to the hardcoded GCP project ID."""
    return firestore.Client(project=GCP_PROJECT_ID)


def list_fishing_spots(region: Optional[str] = None, target_fish: Optional[str] = None) -> List[Dict[str, Any]]:
    """List or search fishing spots in the catalog with optional filters by region or target fish species.

    Args:
        region: Optional filter by region name (e.g. 'California', 'Rockies', 'Maryland', 'Alabama').
        target_fish: Optional filter by target fish species (e.g. 'Bass', 'Trout', 'Striped Bass').

    Returns:
        A list of matching fishing spot summaries.
    """
    db = _get_firestore_client()
    spots_ref = db.collection(COLLECTION_NAME)
    docs = spots_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        
        # Apply optional filters
        if region and region.lower() not in data.get("region", "").lower() and region.lower() not in data.get("name", "").lower():
            continue
        if target_fish:
            species_list = [s.lower() for s in data.get("target_species", [])]
            if not any(target_fish.lower() in s for s in species_list):
                continue
        
        results.append(data)
    return results


def get_fishing_spot_details(spot_id: str) -> Dict[str, Any]:
    """Retrieve full details, access directions, and catch tips for a specific fishing spot.

    Args:
        spot_id: The unique identifier or slug of the fishing spot (e.g. 'clear-lake-cove', 'blue-river-canyon').

    Returns:
        A dictionary with complete details of the fishing spot.
    """
    db = _get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(spot_id).get()
    if not doc.exists:
        return {"error": f"Fishing spot with ID '{spot_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_fishing_spot(
    spot_id: str,
    name: str,
    region: str,
    water_type: str,
    target_species: List[str],
    difficulty: str,
    access_directions: str,
    best_season: str,
    catch_tips: str,
    recommended_tackle: str,
) -> Dict[str, Any]:
    """Add a new fishing spot or update an existing one in the Firestore catalog.

    Args:
        spot_id: Unique slug identifier for the spot (e.g. 'shasta-lake-inlet').
        name: Name of the fishing spot.
        region: Geographic region or state.
        water_type: Type of water body (e.g. 'Lake', 'River', 'Estuary', 'Ocean Pier').
        target_species: List of fish species available to catch.
        difficulty: Skill difficulty level ('Beginner', 'Intermediate', 'Advanced', 'All Levels').
        access_directions: Route and access instructions on how to get there.
        best_season: Best times of year or season to fish.
        catch_tips: Practical tips, lures, baits, and techniques for catching fish here.
        recommended_tackle: Recommended rod, reel, line, and terminal tackle setup.

    Returns:
        A dictionary confirming successful save.
    """
    db = _get_firestore_client()
    spot_data = {
        "id": spot_id,
        "name": name,
        "region": region,
        "water_type": water_type,
        "target_species": target_species,
        "difficulty": difficulty,
        "access_directions": access_directions,
        "best_season": best_season,
        "catch_tips": catch_tips,
        "recommended_tackle": recommended_tackle,
    }
    db.collection(COLLECTION_NAME).document(spot_id).set(spot_data)
    return {"status": "success", "message": f"Fishing spot '{name}' saved successfully.", "spot": spot_data}


CATCHES_COLLECTION = "user_catches"


def calculate_solunar_peak_times(spot_name: str, target_date: Optional[str] = None) -> Dict[str, Any]:
    """Calculate the best peak major and minor feeding windows and lunar activity rating for fishing.

    Args:
        spot_name: Name or region of the fishing spot.
        target_date: Optional ISO date string (YYYY-MM-DD). Defaults to today if not provided.

    Returns:
        A dictionary with major/minor peak feeding hours, lunar rating, and tactical advice.
    """
    if not target_date:
        target_date = datetime.date.today().isoformat()

    # Determine day of year to calculate realistic solunar variations
    try:
        dt = datetime.date.fromisoformat(target_date)
    except Exception:
        dt = datetime.date.today()

    day_seed = dt.timetuple().tm_yday
    # Approximate moon phase (0 to 29.5 day lunar cycle)
    lunar_age = (day_seed + 14) % 30
    if lunar_age in [0, 1, 28, 29]:
        rating = "Excellent (New Moon Peak)"
        multiplier = "Maximum activity"
    elif 13 <= lunar_age <= 16:
        rating = "Excellent (Full Moon Peak)"
        multiplier = "Maximum activity"
    elif lunar_age in [7, 8, 21, 22]:
        rating = "Average (Quarter Moon)"
        multiplier = "Moderate activity"
    else:
        rating = "Good (Crescent / Gibbous)"
        multiplier = "Steady activity"

    return {
        "spot": spot_name,
        "date": dt.isoformat(),
        "solunar_rating": rating,
        "activity_level": multiplier,
        "major_feeding_windows": [
            {"period": "Morning Major", "time": "06:15 AM - 08:15 AM", "notes": "Sunrise align with lunar transit - peak predator strike window"},
            {"period": "Evening Major", "time": "06:45 PM - 08:45 PM", "notes": "Sunset transition with feeding surge"}
        ],
        "minor_feeding_windows": [
            {"period": "Midday Minor", "time": "12:30 PM - 01:30 PM", "notes": "Short feeding burst near solar zenith"},
            {"period": "Night Minor", "time": "11:45 PM - 12:45 AM", "notes": "Active for nocturnal hunters (catfish/trout pools)"}
        ],
        "tactical_advice": "Target shallow structures during the morning major window, and switch to deeper drop-offs or topwater frogs near the evening window."
    }


def log_catch_record(
    spot_id: str,
    species: str,
    weight_or_length: str,
    lure_or_bait: str,
    notes: Optional[str] = "",
    angler_id: Optional[str] = "default_angler",
) -> Dict[str, Any]:
    """Log a caught fish and trip record to your personal catch log.

    Args:
        spot_id: The ID or name of the spot where caught (e.g. 'clear-lake-cove', 'blue-river-canyon').
        species: Fish species caught (e.g. 'Largemouth Bass', 'Rainbow Trout').
        weight_or_length: Measured size (e.g. '4.2 lbs', '18 inches').
        lure_or_bait: Lure, fly pattern, or bait used (e.g. 'Green Pumpkin Senko', 'Pheasant Tail Nymph #16').
        notes: Optional angler observation (e.g. 'Caught under fallen log at dusk').
        angler_id: Identifier of the angler. Defaults to 'default_angler'.

    Returns:
        Confirmation of logged catch.
    """
    db = _get_firestore_client()
    catch_id = f"catch_{int(datetime.datetime.now().timestamp())}"
    catch_data = {
        "catch_id": catch_id,
        "spot_id": spot_id,
        "species": species,
        "size": weight_or_length,
        "lure_or_bait": lure_or_bait,
        "notes": notes,
        "angler_id": angler_id,
        "logged_at": datetime.datetime.now().isoformat(),
    }
    db.collection(CATCHES_COLLECTION).document(catch_id).set(catch_data)
    return {"status": "success", "message": f"Logged {species} ({weight_or_length}) at {spot_id}!", "catch": catch_data}


def list_user_catches(angler_id: Optional[str] = "default_angler") -> List[Dict[str, Any]]:
    """Retrieve personal logged catches and trip history for an angler.

    Args:
        angler_id: The angler ID to fetch catches for. Defaults to 'default_angler'.

    Returns:
        List of recorded catches.
    """
    db = _get_firestore_client()
    docs = db.collection(CATCHES_COLLECTION).where("angler_id", "==", angler_id).stream()
    catches = [doc.to_dict() for doc in docs]
    return catches


import json
import urllib.parse
import urllib.request


def get_live_fishing_weather(location_name: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
    """Fetch real-time live weather, wind conditions, and barometric pressure for any fishing spot or coordinate.
    Uses the free Open-Meteo weather API (no API key required).

    Args:
        location_name: Name of the fishing spot or city (e.g. 'Clear Lake', 'Silverthorne CO', 'Annapolis MD').
        latitude: Optional latitude. If not provided, coordinates are resolved based on the location.
        longitude: Optional longitude.

    Returns:
        A dictionary with live temperature (°F), wind speed (mph), wind direction, barometric pressure (hPa), and angler weather impact assessment.
    """
    coords_map = {
        "clear lake": (39.0143, -122.9097),
        "blue river": (39.6300, -106.0742),
        "silverthorne": (39.6300, -106.0742),
        "chesapeake": (38.9800, -76.3500),
        "annapolis": (38.9784, -76.4922),
        "guntersville": (34.3581, -86.2947),
        "san francisco": (37.7749, -122.4194),
        "new york": (40.7128, -74.0060),
    }

    lat, lon = latitude, longitude
    if lat is None or lon is None:
        loc_clean = location_name.lower()
        for key, coords in coords_map.items():
            if key in loc_clean:
                lat, lon = coords
                break
        
        # If still not found, try Open-Meteo geocoding API
        if lat is None or lon is None:
            try:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location_name)}&count=1&language=en&format=json"
                req = urllib.request.Request(geo_url, headers={"User-Agent": "AnglerCast/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    geo_data = json.loads(resp.read().decode())
                    if geo_data.get("results"):
                        lat = geo_data["results"][0]["latitude"]
                        lon = geo_data["results"][0]["longitude"]
            except Exception:
                lat, lon = 39.0, -122.9  # Default fallback

    if lat is None or lon is None:
        lat, lon = 39.0, -122.9

    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure"
        f"&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&forecast_days=1"
    )

    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "AnglerCast/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            curr = data.get("current", {})
            temp = curr.get("temperature_2m", 65.0)
            wind_speed = curr.get("wind_speed_10m", 5.0)
            wind_dir = curr.get("wind_direction_10m", 180)
            pressure = curr.get("surface_pressure", 1013.2)
            humidity = curr.get("relative_humidity_2m", 50)

            # Pressure trend analysis for fish activity
            if pressure < 1008:
                baro_impact = "Low/falling pressure: Fish may feed actively ahead of incoming weather front."
            elif pressure > 1020:
                baro_impact = "High/rising pressure: Clear skies, fish may hold tight to bottom/deep structure."
            else:
                baro_impact = "Stable barometric pressure: Normal feeding and active strike patterns."

            return {
                "location": location_name,
                "coordinates": {"latitude": lat, "longitude": lon},
                "temperature_f": temp,
                "wind_speed_mph": wind_speed,
                "wind_direction_deg": wind_dir,
                "barometric_pressure_hpa": pressure,
                "humidity_percent": humidity,
                "angler_assessment": baro_impact,
                "source": "Open-Meteo Live API"
            }
    except Exception as e:
        return {
            "location": location_name,
            "error": f"Live weather lookup unavailable: {str(e)}",
            "fallback_temperature_f": 68.0,
            "fallback_wind_speed_mph": 6.0
        }


from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage

IMAGE_MODEL = "gemini-3.1-flash-lite-image"
GCS_BUCKET_NAME = "bwg3-qwiklabs-gcp-04-98ad64e09af9"


async def generate_fishing_image(
    prompt: str,
    item_name: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a realistic scenic illustration of a fishing spot, fish species, or rigging technique.
    Saves the image artifact to the Playground UI and uploads to public Cloud Storage.

    Args:
        prompt: Descriptive visual prompt detailing the fishing spot, fish species, water setting, lighting, or gear.
        item_name: Short identifier or name for the file (e.g. 'clear-lake-scenic', 'rainbow-trout-portrait').
        tool_context: ADK ToolContext for saving the artifact in the Playground.

    Returns:
        A dictionary containing the public Cloud Storage URL and status.
    """
    client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location="global")

    # Generate image using gemini-3.1-flash-lite-image in global location
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "image/jpeg"
            break

    if not image_bytes:
        return {"error": "Failed to generate image from model response."}

    # Clean filename
    clean_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in item_name.lower())
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"{clean_name}_{int(datetime.datetime.now().timestamp())}.{ext}"

    # 1. Save to ToolContext artifact
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename, artifact_part)

    # 2. Upload to public Cloud Storage bucket
    gcs_client = storage.Client(project=GCP_PROJECT_ID)
    bucket = gcs_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"fishing_images/{filename}")
    blob.upload_from_string(image_bytes, content_type=mime_type)
    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{blob.name}"

    return {
        "status": "success",
        "image_url": public_url,
        "artifact_name": filename,
        "prompt": prompt,
    }


from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

AGENT_ENGINE_RUNTIME_ID = "projects/643914080598/locations/us-central1/reasoningEngines/2892872542161207296"

sandbox_code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=AGENT_ENGINE_RUNTIME_ID
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Vertex AI Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are AnglerCast, an expert fishing trip and itinerary concierge.
You remember the user's stated angling preferences, skill level, favorite species, gear setups, and facts from previous conversations and use them to personalize your recommendations.
You help anglers discover top fishing spots, calculate peak solunar feeding times, look up live real-time marine weather and barometric pressure, generate scenic spot/species images, get directions/catch tips, and log/review personal catches.
You can safely execute Python code using the sandbox code executor for accurate mathematical calculations, tide/lunar modeling, distance estimation, or budget analysis.
Use the tools:
- `PreloadMemoryTool` (automatic turn preload) for cross-session long-term memory
- `list_fishing_spots`, `get_fishing_spot_details`, `save_fishing_spot` for fishing spots catalog
- `calculate_solunar_peak_times` to calculate best feeding hours and solunar ratings
- `log_catch_record` and `list_user_catches` for personal catch history
- `get_live_fishing_weather` for real-time live temperature, wind speed, and barometric pressure data
- `generate_fishing_image` to generate scenic illustrations of fishing spots, fish species, or lures and return public URLs
Be enthusiastic, accurate, and provide practical angling advice.""",
    tools=[
        PreloadMemoryTool(),
        list_fishing_spots,
        get_fishing_spot_details,
        save_fishing_spot,
        calculate_solunar_peak_times,
        log_catch_record,
        list_user_catches,
        get_live_fishing_weather,
        generate_fishing_image,
    ],
    code_executor=sandbox_code_executor,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
