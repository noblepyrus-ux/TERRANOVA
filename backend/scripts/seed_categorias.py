import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from database import engine

print("🔄 Insertando categorías base para insumos...")

try:
    with engine.connect() as conn:
        # Verificar si ya existen registros
        result = conn.execute(text("SELECT COUNT(*) FROM categorias"))
        count = result.scalar()
        
        if count == 0:
            conn.execute(text("""
                INSERT INTO categorias (id, nombre) VALUES 
                (1, 'Fertilizantes'),
                (2, 'Pesticidas'),
                (3, 'Semillas'),
                (4, 'Herramientas'),
                (5, 'Otros')
                ON CONFLICT (id) DO NOTHING;
            """))
            conn.commit()
            print("✅ Categorías base insertadas correctamente.")
        else:
            print(f"ℹ️  La tabla 'categorias' ya tiene {count} registros. No se hizo nada.")
except Exception as e:
    print(f"❌ Error: {e}")