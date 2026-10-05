from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, Literal


# ==================== TOKENS (AUTENTICACIÓN) ====================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    usuario: Optional[str] = None


# ==================== CUENTAS (AUTENTICACIÓN) ====================
class CuentaBase(BaseModel):
    usuario: str
    rol: Optional[str] = "admin"

class CuentaCreate(CuentaBase):
    password: str

class CuentaResponse(CuentaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== ALCANCES ====================
class AlcanceBase(BaseModel):
    tipo: str

class AlcanceCreate(AlcanceBase):
    pass

class AlcanceResponse(AlcanceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== FINCAS ====================
class FincaBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None
    area_total: Optional[float] = None
    cuenta_id: Optional[int] = None

class FincaCreate(FincaBase):
    pass

class FincaUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    area_total: Optional[float] = None
    cuenta_id: Optional[int] = None

class FincaResponse(FincaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== LOTES ====================
class LoteBase(BaseModel):
    nombre: str
    area: Optional[float] = None
    tipo_suelo: Optional[str] = None
    altitud: Optional[float] = None
    clima: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    finca_id: int

class LoteCreate(LoteBase):
    pass

class LoteUpdate(BaseModel):
    nombre: Optional[str] = None
    area: Optional[float] = None
    tipo_suelo: Optional[str] = None
    altitud: Optional[float] = None
    clima: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    finca_id: Optional[int] = None

class LoteResponse(LoteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== CULTIVOS ====================
class CultivoBase(BaseModel):
    nombre: str
    variedad: Optional[str] = None
    estado: Optional[str] = None
    fecha_siembra: Optional[date] = None
    lote_id: int

class CultivoCreate(CultivoBase):
    pass

class CultivoUpdate(BaseModel):
    nombre: Optional[str] = None
    variedad: Optional[str] = None
    estado: Optional[str] = None
    fecha_siembra: Optional[date] = None
    lote_id: Optional[int] = None

class CultivoResponse(CultivoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== INSUMOS ====================

class InsumoBase(BaseModel):
    nombre: str
    tipo: Optional[str] = None
    unidad: Optional[str] = None
    stock_actual: Optional[float] = 0.0
    costo_promedio: Optional[float] = 0.0

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    unidad: Optional[str] = None
    stock_actual: Optional[float] = None
    costo_promedio: Optional[float] = None

class InsumoResponse(InsumoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
# ==================== COMPRAS ====================

class CompraBase(BaseModel):
    cantidad: float
    costo_unitario: float
    costo_total: Optional[float] = None
    fecha: Optional[date] = None
    proveedor: Optional[str] = None
    nota: Optional[str] = None
    insumo_id: int

class CompraCreate(CompraBase):
    # Campos opcionales para crear insumo nuevo en la misma operación
    nuevo_insumo_nombre: Optional[str] = None
    nuevo_insumo_tipo: Optional[str] = None
    nuevo_insumo_unidad: Optional[str] = None

class CompraUpdate(BaseModel):
    cantidad: Optional[float] = None
    costo_unitario: Optional[float] = None
    costo_total: Optional[float] = None
    fecha: Optional[date] = None
    proveedor: Optional[str] = None
    nota: Optional[str] = None
    insumo_id: Optional[int] = None

class CompraResponse(CompraBase):
    id: int
    nombre_insumo: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# ==================== COSECHAS ====================
class CosechaBase(BaseModel):
    fecha: date
    cantidad: float
    unidad: Optional[str] = None
    notas: Optional[str] = None
    cultivo_id: int

class CosechaCreate(CosechaBase):
    pass

class CosechaUpdate(BaseModel):
    fecha: Optional[date] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    notas: Optional[str] = None
    cultivo_id: Optional[int] = None

class CosechaResponse(CosechaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== CATEGORIAS ====================
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== TAREAS ====================
TipoTarea = Literal[
    "Preparación de terreno", "Análisis de suelos", "Encalado",
    "Siembra directa", "Transplante", "Resiembra",
    "Riego", "Fertilización", "Fumigación", "Deshierbe", "Poda", "Tutorado", "Raleo",
    "Cosecha", "Transporte interno", "Clasificación y Empaque",
    "Mantenimiento de maquinaria", "Reparación de infraestructura", "Limpieza general",
    "Gestión de personal", "Trámites y Legal",
    "Otro"
]

class TareaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha: Optional[date] = None
    estado: Optional[str] = None
    tipo: Optional[TipoTarea] = None
    alcance_id: int
    insumo_id: Optional[int] = None
    cantidad_usada: Optional[float] = None
    lote_id: Optional[int] = None
    cultivo_id: Optional[int] = None

class TareaCreate(TareaBase):
    pass

class TareaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha: Optional[date] = None
    estado: Optional[str] = None
    tipo: Optional[TipoTarea] = None
    alcance_id: Optional[int] = None
    insumo_id: Optional[int] = None
    cantidad_usada: Optional[float] = None
    lote_id: Optional[int] = None
    cultivo_id: Optional[int] = None

class TareaResponse(TareaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==================== GASTOS OPERATIVOS ====================
class GastoOperativoBase(BaseModel):
    concepto: str
    monto: float
    fecha: Optional[date] = None
    categoria_id: int
    alcance_id: int
    finca_id: Optional[int] = None
    lote_id: Optional[int] = None
    cultivo_id: Optional[int] = None
    tarea_id: Optional[int] = None

class GastoOperativoCreate(GastoOperativoBase):
    pass

class GastoOperativoUpdate(BaseModel):
    concepto: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[date] = None
    categoria_id: Optional[int] = None
    alcance_id: Optional[int] = None
    finca_id: Optional[int] = None
    lote_id: Optional[int] = None
    cultivo_id: Optional[int] = None
    tarea_id: Optional[int] = None

class GastoOperativoResponse(GastoOperativoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)