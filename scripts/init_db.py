from agents.inventory_manager import database as inv_db
from agents.life_organizer import database as org_db
from agents.smart_home import database as sh_db

# Importing the modules triggers table creation via metadata.create_all
print("Databases initialized.")
