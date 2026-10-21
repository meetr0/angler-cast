# Copyright 2026 Google LLC
import logging
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-04-98ad64e09af9"
COLLECTION_NAME = "fishing_spots"

SEED_SPOTS = [
    {
        "id": "clear-lake-cove",
        "name": "Clear Lake Cove",
        "region": "Northern California",
        "water_type": "Freshwater Lake",
        "target_species": ["Largemouth Bass", "Crappie", "Catfish"],
        "difficulty": "Beginner to Intermediate",
        "access_directions": "Highway 20 East to Lakeport exit, follow Lakeshore Blvd north for 3 miles to the public boat launch.",
        "best_season": "Spring and Fall",
        "catch_tips": "Use Texas-rigged plastic worms or spinnerbaits near the submerged weedlines early in the morning.",
        "recommended_tackle": "Medium-heavy spinning or baitcasting rod with 12lb fluorocarbon line."
    },
    {
        "id": "blue-river-canyon",
        "name": "Blue River Canyon",
        "region": "Colorado Rockies",
        "water_type": "Freestone River",
        "target_species": ["Rainbow Trout", "Brown Trout"],
        "difficulty": "Intermediate to Advanced",
        "access_directions": "Take I-70 to Silverthorne exit, head north on Hwy 9 for 8 miles, park at the canyon trailhead turnout.",
        "best_season": "Summer (June to September)",
        "catch_tips": "Dead-drift beadhead pheasant tail nymphs (#16-#18) below a strike indicator through deep riffles.",
        "recommended_tackle": "9ft 5-weight fly rod with 5X fluorocarbon tippet and floating line."
    },
    {
        "id": "chesapeake-bay-point",
        "name": "Chesapeake Bay Point",
        "region": "Maryland Eastern Shore",
        "water_type": "Saltwater / Estuary",
        "target_species": ["Striped Bass (Rockfish)", "Red Drum", "Bluefish"],
        "difficulty": "Intermediate",
        "access_directions": "US-50 across Bay Bridge, take MD-8 South down Kent Island to the public pier and jetty access.",
        "best_season": "Autumn (October - November)",
        "catch_tips": "Troll bunker spoons or jig 1oz white bucktails with paddle tail swimbaits along tidal drop-offs.",
        "recommended_tackle": "7ft medium-heavy saltwater spinning rod, 30lb braided main line with 25lb mono leader."
    },
    {
        "id": "lake-guntersville-flats",
        "name": "Lake Guntersville Flats",
        "region": "Northern Alabama",
        "water_type": "Reservoir / River Chain",
        "target_species": ["Largemouth Bass", "Smallmouth Bass"],
        "difficulty": "All Levels",
        "access_directions": "US-431 to Guntersville State Park entrance, proceed to the south boat ramp and fishing pier.",
        "best_season": "Spring (Pre-spawn March-April)",
        "catch_tips": "Fish lipless crankbaits over hydrilla patches and work topwater frogs during evening low light.",
        "recommended_tackle": "7ft 3in heavy action baitcasting rod with 50lb braided line for punching heavy vegetation."
    }
]

def seed_data():
    db = firestore.Client(project=PROJECT_ID)
    logger.info(f"Connected to Firestore project: {PROJECT_ID}")
    
    for spot in SEED_SPOTS:
        doc_id = spot["id"]
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc_ref.set(spot)
        logger.info(f"Seeded spot: {spot['name']} (ID: {doc_id})")
        
    logger.info(f"Successfully seeded {len(SEED_SPOTS)} fishing spots into '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    seed_data()
