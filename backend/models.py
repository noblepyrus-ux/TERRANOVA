from sqlalchemy import Column, Float, ForeignKey, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from database import Base

class Finca(Base):
    __tablename__ = "fincas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ubicacion = Column(String, nullable=True)
    area_total = Column(Float, nullable=True)
    propietarios = relationship("FincaCuenta", back_populates="finca", cascade="all, delete-orphan")
    lotes = relationship("Lote", back_populates="finca", cascade="all, delete-orphan")
    gastos_operativos = relationship("GastoOperativo", back_populates="finca", cascade="all, delete-orphan")

class FincaCuenta(Base):
    """Tabla intermedia para relación N:M entre Fincas y Cuentas.
    Permite que una finca tenga varios propietarios/usuarios
    y que un usuario tenga varias fincas."""
    __tablename__ = "fincas_cuentas"
    
    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id", ondelete="CASCADE"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id", ondelete="CASCADE"), nullable=False)
    rol_en_finca = Column(String, nullable=False, default="propietario")  # propietario, administrador, trabajador
    
    # Relaciones
    finca = relationship("Finca", back_populates="propietarios")
    cuenta = relationship("Cuenta", back_populates="fincas_asociadas")

class Lote(Base):
    __tablename__ = "lotes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    area = Column(Float, nullable=True)
    tipo_suelo = Column(String, nullable=True)
    altitud = Column(Float, nullable=True)
    clima = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)
    
    finca = relationship("Finca", back_populates="lotes")
    cultivos = relationship("Cultivo", back_populates="lote", cascade="all, delete-orphan")
    tareas = relationship("Tarea", back_populates="lote", cascade="all, delete-orphan")
    gastos_operativos = relationship("GastoOperativo", back_populates="lote", cascade="all, delete-orphan")

class Cultivo(Base):
    __tablename__ = "cultivos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    variedad = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    fecha_siembra = Column(Date, nullable=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    
    lote = relationship("Lote", back_populates="cultivos")
    tareas = relationship("Tarea", back_populates="cultivo", cascade="all, delete-orphan")
    cosechas = relationship("Cosecha", back_populates="cultivo", cascade="all, delete-orphan")
    gastos_operativos = relationship("GastoOperativo", back_populates="cultivo", cascade="all, delete-orphan")

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(Date, nullable=True)
    fecha_limite = Column(Date, nullable=True)
    estado = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    alcance_id = Column(Integer, ForeignKey("alcances.id"), nullable=False)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=True)
    cantidad_usada = Column(Float, nullable=True)
    
    # FKs opcionales para vincular la tarea a una entidad específica
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    cultivo_id = Column(Integer, ForeignKey("cultivos.id"), nullable=True)
    
    alcance = relationship("Alcance", back_populates="tareas")
    insumo = relationship("Insumo", back_populates="tareas")
    lote = relationship("Lote", back_populates="tareas")
    cultivo = relationship("Cultivo", back_populates="tareas")
    gastos_operativos = relationship("GastoOperativo", back_populates="tarea", cascade="all, delete-orphan")

class Insumo(Base):
    __tablename__ = "insumos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=True)
    unidad = Column(String, nullable=True)
    stock_actual = Column(Float, nullable=True)
    costo_promedio = Column(Float, nullable=True)
    
    tareas = relationship("Tarea", back_populates="insumo")
    compras = relationship("Compra", back_populates="insumo", cascade="all, delete-orphan")

class Compra(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Float, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    costo_total = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False)
    proveedor = Column(String, nullable=True)
    nota = Column(Text, nullable=True)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    
    insumo = relationship("Insumo", back_populates="compras")

class Cosecha(Base):
    __tablename__ = "cosechas"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String, nullable=True)
    notas = Column(Text, nullable=True)
    cultivo_id = Column(Integer, ForeignKey("cultivos.id"), nullable=False)
    
    cultivo = relationship("Cultivo", back_populates="cosechas")

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    
    gastos_operativos = relationship("GastoOperativo", back_populates="categoria")

class Alcance(Base):
    __tablename__ = "alcances"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    
    tareas = relationship("Tarea", back_populates="alcance")
    gastos_operativos = relationship("GastoOperativo", back_populates="alcance")

class GastoOperativo(Base):
    __tablename__ = "gastos_operativos"
    id = Column(Integer, primary_key=True, index=True)
    concepto = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(Date, nullable=True)
    fecha_limite = Column(Date, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    alcance_id = Column(Integer, ForeignKey("alcances.id"), nullable=False)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    cultivo_id = Column(Integer, ForeignKey("cultivos.id"), nullable=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=True)
    
    categoria = relationship("Categoria", back_populates="gastos_operativos")
    alcance = relationship("Alcance", back_populates="gastos_operativos")
    finca = relationship("Finca", back_populates="gastos_operativos")
    lote = relationship("Lote", back_populates="gastos_operativos")
    cultivo = relationship("Cultivo", back_populates="gastos_operativos")
    tarea = relationship("Tarea", back_populates="gastos_operativos")

# ==========================================
# NUEVA TABLA DE AUTENTICACIÓN (CUENTAS)
# ==========================================
class Cuenta(Base):
    __tablename__ = "cuentas"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, nullable=True, default="admin") 
    fincas_asociadas = relationship("FincaCuenta", back_populates="cuenta", cascade="all, delete-orphan")