from sqlalchemy import text
from database import engine

print("🔄 Sincronizando la tabla 'tareas' con el modelo de Python...")

try:
    with engine.connect() as conn:
        # 1. Agregar lote_id si no existe
        conn.execute(text("""
            ALTER TABLE tareas 
            ADD COLUMN IF NOT EXISTS lote_id INTEGER;
        """))
        
        # 2. Agregar cultivo_id si no existe (por si acaso también falta)
        conn.execute(text("""
            ALTER TABLE tareas 
            ADD COLUMN IF NOT EXISTS cultivo_id INTEGER;
        """))

        conn.commit()
        print("✅ ¡Éxito! Las columnas 'lote_id' y 'cultivo_id' se agregaron a la tabla 'tareas'.")
        print("💡 Ahora las tareas pueden vincularse opcionalmente a un lote o a un cultivo.")
except Exception as e:
    print(f"❌ Error al sincronizar: {e}")