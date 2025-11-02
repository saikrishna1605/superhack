"""
Fix client IDs - replace random UUID with sequential CL#### format
"""
from database import SessionLocal
from models.models import Client

def fix_client_ids():
    db = SessionLocal()
    try:
        # Get all clients
        clients = db.query(Client).order_by(Client.id).all()
        
        print(f"Found {len(clients)} clients in database\n")
        
        # Show current client IDs
        print("Current client IDs:")
        for client in clients:
            print(f"  ID: {client.id}, ClientID: {client.client_id}, Name: {client.name}")
        
        print("\n" + "="*60)
        
        # Find clients with incorrect format (not matching CL####)
        import re
        cl_pattern = re.compile(r'^CL\d{4}$')
        
        incorrect_clients = [c for c in clients if not cl_pattern.match(c.client_id or '')]
        
        if not incorrect_clients:
            print("\nAll client IDs are already in correct format!")
            return
        
        print(f"\nFound {len(incorrect_clients)} client(s) with incorrect ID format:")
        for client in incorrect_clients:
            print(f"  ClientID: {client.client_id}, Name: {client.name}")
        
        # Get the highest CL number currently in use
        valid_clients = [c for c in clients if cl_pattern.match(c.client_id or '')]
        if valid_clients:
            max_num = max([int(c.client_id[2:]) for c in valid_clients])
        else:
            max_num = 0
        
        print(f"\nHighest CL number in use: {max_num}")
        
        # Fix incorrect IDs
        next_num = max_num + 1
        for client in incorrect_clients:
            old_id = client.client_id
            new_id = f"CL{str(next_num).zfill(4)}"
            client.client_id = new_id
            print(f"\nUpdating: {old_id} -> {new_id} ({client.name})")
            next_num += 1
        
        # Commit changes
        db.commit()
        print("\n" + "="*60)
        print("✓ Database updated successfully!")
        
        # Show updated client IDs
        clients = db.query(Client).order_by(Client.id).all()
        print("\nUpdated client IDs:")
        for client in clients:
            print(f"  ID: {client.id}, ClientID: {client.client_id}, Name: {client.name}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_client_ids()
