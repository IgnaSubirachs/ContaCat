"""
Script de verificació del mòdul d'Inventari i la seva integració.
Prova la creació d'articles, moviments d'estoc i validacions bàsiques.
"""
import sys
import os
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.db.base import init_db, SessionLocal
from app.domain.inventory.services import InventoryService
from app.infrastructure.persistence.inventory.repositories import SqlAlchemyStockItemRepository, SqlAlchemyStockMovementRepository
from app.domain.inventory.entities import StockItem, StockMovement

def verify_inventory():
    print("=" * 60)
    print("VERIFICACIÓ MÒDUL D'INVENTARI (STOCK)")
    print("=" * 60)

    print("\n1. Inicialitzant base de dades...")
    init_db()
    
    session = SessionLocal()
    
    try:
        # Repositories & Services
        item_repo = SqlAlchemyStockItemRepository(session)
        movement_repo = SqlAlchemyStockMovementRepository(session)
        service = InventoryService(item_repo, movement_repo)
        
        # 1. Create Data
        print("\n[Step 1] Creant article de prova...")
        code = "PROD-TEST-001"
        existing = item_repo.find_by_code(code)
        if existing:
            # Clean up for clean test
            # Note: Cascade delete might be needed if there are movements, 
            # but usually we just want to ensure we start fresh or reuse
            # For this test, let's reuse if exists or modify quantity to 0
            print(f"   - L'article {code} ja existeix. Reset del stock a 0.")
            existing.quantity = 0
            item_repo.save(existing)
            item = existing
        else:
            item = StockItem(
                code=code,
                name="Portàtil Developer",
                description="Portàtil d'alt rendiment",
                unit_price=1500.0,
                quantity=0, # Start with 0
                location="Magatzem Central"
            )
            item = service.create_item(item)
            print(f"✓ Article creat: {item.name}")

        print(f"   - Stock Inicial: {item.quantity}")

        # 2. Register Entry (Purchase)
        print("\n[Step 2] Registrant entrada de stock (Compra)...")
        in_movement = StockMovement(
            stock_item_code=code,
            date=date.today(),
            quantity=10,
            description="Recepció comanda C-2024-001"
        )
        service.register_movement(in_movement)
        
        # Verify
        updated_item = service.get_item(item.id)
        print(f"✓ Moviment registrat correctament")
        print(f"   - Stock actual: {updated_item.quantity} (Esperat: 10)")
        
        if updated_item.quantity != 10:
             print("⚠ ERROR: L'estoc no coincideix!")
             return False

        # 3. Register Output (Sale)
        print("\n[Step 3] Registrant sortida de stock (Venda)...")
        out_movement = StockMovement(
            stock_item_code=code,
            date=date.today(),
            quantity=-2,
            description="Lliurament comanda V-2024-005"
        )
        service.register_movement(out_movement)
        
        # Verify
        updated_item = service.get_item(item.id)
        print(f"✓ Sortida registrada correctament")
        print(f"   - Stock actual: {updated_item.quantity} (Esperat: 8)")
        
        if updated_item.quantity != 8:
             print("⚠ ERROR: L'estoc no coincideix després de la venda!")
             return False
             
        # 4. Check Stock Insufficient
        print("\n[Step 4] Verificant control d'estoc negatiu...")
        try:
            bad_movement = StockMovement(
                stock_item_code=code,
                date=date.today(),
                quantity=-100, # More than 8 available
                description="Intent de sortida excessiva"
            )
            service.register_movement(bad_movement)
            print("⚠ ERROR: S'hauria d'haver llançat una excepció per falta d'estoc!")
            return False
        except ValueError as e:
            print(f"✓ Correcte: S'ha evitat l'estoc negatiu ({e})")

        # 5. List Movements
        print("\n[Step 5] Llistant moviments de l'article...")
        movements = service.list_movements(code)
        print(f"✓ Trobats {len(movements)} moviments")
        for m in movements:
            type_str = "ENTRADA" if m.quantity > 0 else "SORTIDA"
            print(f"   - {m.date} | {type_str:<7} | Qty: {abs(m.quantity)} | {m.description}")

        print("\n✅ Verificació d'Inventari completada correctament!")
        return True

    except Exception as e:
        print(f"\n✗ ERROR CRÍTIC: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_inventory()
    sys.exit(0 if success else 1)
