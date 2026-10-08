# recrear_db.py
# ⚠️ ADVERTENCIA: Este script BORRA todas las tablas existentes y las recrea.
# Úsalo SOLO en entorno de desarrollo.

from database import engine, Base

def main():
    print("🔄 Iniciando proceso de recreación de la base de datos...")
    
    # 1. Borrar todas las tablas definidas en models.py
    print("🗑️  Eliminando tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. Crear todas las tablas con la nueva estructura (incluyendo fincas_cuentas)
    print("🛠️  Creando nuevas tablas...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ ¡Base de datos recreada exitosamente con la nueva estructura N:M!")
    print("   - Tabla 'fincas' actualizada (sin cuenta_id)")
    print("   - Nueva tabla 'fincas_cuentas' creada")
    print("   - Tabla 'cuentas' actualizada con relación inversa")

if __name__ == "__main__":
    main()


#utilidad de desarrollo
