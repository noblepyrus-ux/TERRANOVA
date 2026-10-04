import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from database import engine

print("🔄 Insertando alcances base en la base de datos...")

try:
    with engine.connect() as conn:
        # Verificar si ya existen registros
        result = conn.execute(text("SELECT COUNT(*) FROM alcances"))
        count = result.scalar()
        
        if count < 4:
            conn.execute(text("""
                INSERT INTO alcances (id, tipo) VALUES 
                (1, 'Finca'),
                (2, 'Lote'),
                (3, 'Cultivo'),
                (4, 'General')
                ON CONFLICT (id) DO NOTHING;
            """))
            conn.commit()
            print("✅ Alcances base insertados correctamente.")
        else:
            print(f"ℹ️  La tabla 'alcances' ya tiene {count} registros. No se hizo nada.")
except Exception as e:
    print(f"❌ Error: {e}")