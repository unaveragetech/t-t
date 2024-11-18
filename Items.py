import os
import shutil
import json
from datetime import datetime

# Create catalog directory
catalog_dir = "catalog"
os.makedirs(catalog_dir, exist_ok=True)

def load_catalog():
    """Load catalog from file."""
    catalog_file = os.path.join(catalog_dir, "catalog.json")
    if not os.path.exists(catalog_file):
        return []
    try:
        with open(catalog_file, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return []

def save_catalog(data):
    """Save catalog to file."""
    catalog_file = os.path.join(catalog_dir, "catalog.json")
    try:
        with open(catalog_file, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving catalog: {e}")

def search_catalog(query, field=None):
    """Search for entries in the catalog."""
    catalog = load_catalog()
    if field:
        results = [entry for entry in catalog if field in entry and query.lower() in str(entry[field]).lower()]
    else:
        results = [entry for entry in catalog if any(query.lower() in str(value).lower() for value in entry.values())]
    return results

def edit_entry(product_code):
    """Edit an entry in the catalog."""
    catalog = load_catalog()
    for entry in catalog:
        if entry["product_code"] == product_code:
            if entry.get("locked", False):
                print("This entry is locked and cannot be edited.")
                return
            print(f"Editing entry: {entry}")
            for key in entry.keys():
                if key in ["product_code", "image", "locked"]:
                    continue  # Do not allow changes to these fields
                new_value = input(f"Enter new value for {key} (leave blank to keep '{entry[key]}'): ").strip()
                if new_value:
                    entry[key] = new_value
            save_catalog(catalog)
            print("Entry updated.")
            return
    print("Entry not found.")

def lock_entry(product_code):
    """Lock an entry to prevent editing."""
    catalog = load_catalog()
    for entry in catalog:
        if entry["product_code"] == product_code:
            entry["locked"] = True
            save_catalog(catalog)
            print(f"Entry {product_code} locked.")
            return
    print("Entry not found.")

def export_entry(product_code):
    """Export an entry and its image to a directory."""
    catalog = load_catalog()
    for entry in catalog:
        if entry["product_code"] == product_code:
            if not entry.get("locked", False):
                print("This entry must be locked before export.")
                return
            export_dir = os.path.join(catalog_dir, entry["ring_name"].replace(" ", "_"))
            os.makedirs(export_dir, exist_ok=True)
            
            # Export JSON
            export_file = os.path.join(export_dir, f"{entry['ring_name']}.json")
            with open(export_file, "w") as file:
                json.dump(entry, file, indent=4)
            
            # Copy image
            shutil.copy(entry["image"], export_dir)
            print(f"Entry exported to {export_dir}")
            return
    print("Entry not found.")

def main_menu():
    """Main menu for catalog operations."""
    while True:
        print("\nCatalog Menu:")
        print("1. Add a new ring")
        print("2. Search catalog")
        print("3. Edit an entry")
        print("4. Lock an entry")
        print("5. Export an entry")
        print("6. Exit")
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            main()
        elif choice == "2":
            query = input("Enter search query: ").strip()
            field = input("Enter field to search (or leave blank for all fields): ").strip()
            results = search_catalog(query, field if field else None)
            if results:
                print("Search results:")
                for result in results:
                    print(result)
            else:
                print("No results found.")
        elif choice == "3":
            product_code = input("Enter product code to edit: ").strip()
            edit_entry(product_code)
        elif choice == "4":
            product_code = input("Enter product code to lock: ").strip()
            lock_entry(product_code)
        elif choice == "5":
            product_code = input("Enter product code to export: ").strip()
            export_entry(product_code)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
