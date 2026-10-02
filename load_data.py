import asyncio
import aiohttp
import asyncpg


API_BASE = "https://swapi-node.vercel.app/api"
BATCH_SIZE = 10


async def fetch_page(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch a single page from SWAPI."""
    async with session.get(url) as response:
        return await response.json()


async def fetch_all_pages(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch all characters from SWAPI, handling pagination."""
    all_characters = []
    url = f"{API_BASE}/people/?page=1&limit={BATCH_SIZE}"

    while url:
        data = await fetch_page(session, url)
        all_characters.extend(data["results"])
        url = data.get("next")
        await asyncio.sleep(0.1)  # Rate limiting

    return all_characters


async def resolve_name(session: aiohttp.ClientSession, url: str) -> str:
    """Resolve a SWAPI URL to a name (e.g., /people/1 -> Luke Skywalker)."""
    if not url or url == "":
        return ""
    try:
        async with session.get(url) as response:
            data = await response.json()
            return data.get("fields", {}).get("name", url.split("/")[-2])
    except Exception:
        return url.split("/")[-2]


async def resolve_paths_to_names(
    session: aiohttp.ClientSession, fields: dict
) -> dict:
    """Resolve homeworld, starships, vehicles URLs to names."""
    # Resolve homeworld
    homeworld_url = fields.get("homeworld", "")
    homeworld_name = await resolve_name(session, homeworld_url) if homeworld_url else ""

    # Resolve starships
    starships_urls = fields.get("starships", [])
    starship_tasks = [resolve_name(session, url) for url in starships_urls if url]
    if starship_tasks:
        starship_names = await asyncio.gather(*starship_tasks)
    else:
        starship_names = []

    # Resolve vehicles
    vehicles_urls = fields.get("vehicles", [])
    vehicle_tasks = [resolve_name(session, url) for url in vehicles_urls if url]
    if vehicle_tasks:
        vehicle_names = await asyncio.gather(*vehicle_tasks)
    else:
        vehicle_names = []

    # Films - can be empty string
    films = fields.get("films", [])

    return {
        "homeworld": homeworld_name,
        "starships": ", ".join(starship_names),
        "vehicles": ", ".join(vehicle_names),
        "films": ", ".join(films) if films else "",
    }


async def insert_character(
    session: aiohttp.ClientSession,
    conn: asyncpg.Connection,
    character: dict,
) -> None:
    """Insert a single character into PostgreSQL."""
    fields = character.get("fields", {})

    # Resolve path fields to names
    resolved = await resolve_paths_to_names(session, fields)

    swapi_id = fields.get("url", "").split("/")[-2]
    if swapi_id.isdigit():
        swapi_id = int(swapi_id)
    else:
        swapi_id = 0

    await conn.execute(
        """
        INSERT INTO people (swapi_id, name, height, mass, hair_color, 
                           skin_color, eye_color, birth_year, gender,
                           homeworld, starships, vehicles, films)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (swapi_id) DO UPDATE SET
            name = EXCLUDED.name,
            height = EXCLUDED.height,
            mass = EXCLUDED.mass,
            hair_color = EXCLUDED.hair_color,
            skin_color = EXCLUDED.skin_color,
            eye_color = EXCLUDED.eye_color,
            birth_year = EXCLUDED.birth_year,
            gender = EXCLUDED.gender,
            homeworld = EXCLUDED.homeworld,
            starships = EXCLUDED.starships,
            vehicles = EXCLUDED.vehicles,
            films = EXCLUDED.films
        """,
        swapi_id,
        fields.get("name", ""),
        fields.get("height", ""),
        fields.get("mass", ""),
        fields.get("hair_color", ""),
        fields.get("skin_color", ""),
        fields.get("eye_color", ""),
        fields.get("birth_year", ""),
        fields.get("gender", ""),
        resolved["homeworld"],
        resolved["starships"],
        resolved["vehicles"],
        resolved["films"],
    )


async def load_data():
    """Main function to load all data from SWAPI to PostgreSQL."""
    print("Starting data load...")

    async with aiohttp.ClientSession() as session:
        print("Fetching all characters from SWAPI...")
        characters = await fetch_all_pages(session)
        print(f"Fetched {len(characters)} characters")

        # Use asyncpg connection directly for inserts
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="swapi_db",
            user="swapi_user",
            password="swapi_password",
        )

        for i, character in enumerate(characters):
            await insert_character(session, conn, character)
            if (i + 1) % 10 == 0:
                print(f"Inserted {i + 1}/{len(characters)} characters...")

        await conn.close()
        print(f"Successfully loaded {len(characters)} characters!")


if __name__ == "__main__":
    asyncio.run(load_data())
