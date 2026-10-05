import sys
from pathlib import Path

# Agregar la carpeta padre (backend) al path de Python
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from database import engine

print("🔄 Agregando columna 'fecha_limite' a la tabla 'tareas'...")

try:
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tareas' AND column_name = 'fecha_limite'
        """))
        existe = result.scalar()
        
        if not existe:
            conn.execute(text("""
                ALTER TABLE tareas 
                ADD COLUMN fecha_limite DATE;
            """))
            conn.commit()
            print("✅ Columna 'fecha_limite' agregada correctamente a la tabla 'tareas'.")
        else:
            print("️  La columna 'fecha_limite' ya existe en la tabla 'tareas'. No se hizo nada.")
except Exception as e:
    print(f"❌ Error: {e}")