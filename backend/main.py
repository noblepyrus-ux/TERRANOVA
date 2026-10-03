from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import models
import schemas
from database import Base, engine, get_db
from auth import (
    get_password_hash, 
    create_access_token, 
    authenticate_user, 
    get_current_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Crear las tablas en la base de datos al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Terranova API - Sistema Agrícola")

# Configuración de CORS para permitir peticiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, cambia "*" por la URL de tu frontend (ej: "http://localhost:4200")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTENTICACIÓN ====================

@app.post("/auth/register", status_code=201)  
def register_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db)):
    db_cuenta = db.query(models.Cuenta).filter(models.Cuenta.usuario == cuenta.usuario).first()
    if db_cuenta:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")
    
    hashed_password = get_password_hash(cuenta.password)
    db_new_cuenta = models.Cuenta(
        usuario=cuenta.usuario, 
        hashed_password=hashed_password, 
        rol=cuenta.rol
    )
    db.add(db_new_cuenta)
    db.commit()
    db.refresh(db_new_cuenta)
    
    return {
        "message": "¡Cuenta creada exitosamente! Ya puedes iniciar sesión.",
        "usuario": db_new_cuenta.usuario,
        "rol": db_new_cuenta.rol
    }

@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(cuenta_data: schemas.CuentaCreate, db: Session = Depends(get_db)):
    cuenta = authenticate_user(db, cuenta_data.usuario, cuenta_data.password)
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": cuenta.usuario}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== ALCANCES ====================

@app.get("/alcances", response_model=list[schemas.AlcanceResponse])
def list_alcances(db: Session = Depends(get_db)):
    return db.query(models.Alcance).all()

@app.post("/alcances", response_model=schemas.AlcanceResponse, status_code=201)
def create_alcance(alcance: schemas.AlcanceCreate, db: Session = Depends(get_db)):
    db_alcance = models.Alcance(**alcance.model_dump())
    db.add(db_alcance)
    db.commit()
    db.refresh(db_alcance)
    return db_alcance

@app.delete("/alcances/{alcance_id}", status_code=204)
def delete_alcance(alcance_id: int, db: Session = Depends(get_db)):
    db_alcance = db.query(models.Alcance).filter(models.Alcance.id == alcance_id).first()
    if not db_alcance:
        raise HTTPException(status_code=404, detail="Alcance no encontrado")
    db.delete(db_alcance)
    db.commit()


# ==================== FINCAS (PROTEGIDO) ====================

@app.get("/fincas", response_model=list[schemas.FincaResponse])
def list_fincas(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Solo devuelve las fincas que pertenecen al usuario logueado
    return db.query(models.Finca).filter(models.Finca.cuenta_id == current_user.id).all()

@app.get("/fincas/{finca_id}", response_model=schemas.FincaResponse)
def get_finca(finca_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    finca = db.query(models.Finca).filter(
        models.Finca.id == finca_id,
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    return finca

@app.post("/fincas", response_model=schemas.FincaResponse, status_code=201)
def create_finca(finca: schemas.FincaCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Asigna automáticamente la finca al usuario logueado
    db_finca = models.Finca(**finca.model_dump(exclude={"cuenta_id"}), cuenta_id=current_user.id)
    db.add(db_finca)
    db.commit()
    db.refresh(db_finca)
    return db_finca

@app.put("/fincas/{finca_id}", response_model=schemas.FincaResponse)
def update_finca(finca_id: int, finca: schemas.FincaUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_finca = db.query(models.Finca).filter(
        models.Finca.id == finca_id,
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not db_finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    for key, value in finca.model_dump(exclude_unset=True).items():
        setattr(db_finca, key, value)
    db.commit()
    db.refresh(db_finca)
    return db_finca

@app.delete("/fincas/{finca_id}", status_code=204)
def delete_finca(finca_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_finca = db.query(models.Finca).filter(
        models.Finca.id == finca_id,
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not db_finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    db.delete(db_finca)
    db.commit()


# ==================== LOTES ====================

# ==================== LOTES (Con seguridad multi-usuario) ====================

@app.get("/lotes", response_model=list[schemas.LoteResponse])
def list_lotes(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Obtener los IDs de las fincas del usuario actual
    fincas_ids = [finca.id for finca in db.query(models.Finca.id).filter(models.Finca.cuenta_id == current_user.id).all()]
    if not fincas_ids:
        return []
    # Solo devolver lotes de las fincas del usuario
    return db.query(models.Lote).filter(models.Lote.finca_id.in_(fincas_ids)).all()

@app.get("/lotes/{lote_id}", response_model=schemas.LoteResponse)
def get_lote(lote_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece a una finca del usuario
    lote = db.query(models.Lote).join(models.Finca).filter(
        models.Lote.id == lote_id, 
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    return lote

@app.post("/lotes", response_model=schemas.LoteResponse, status_code=201)
def create_lote(lote: schemas.LoteCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que la finca existe y le pertenece al usuario
    finca = db.query(models.Finca).filter(
        models.Finca.id == lote.finca_id, 
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not finca:
        raise HTTPException(status_code=403, detail="No tienes permiso para agregar lotes a esta finca")
    
    db_lote = models.Lote(**lote.model_dump())
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    return db_lote

@app.put("/lotes/{lote_id}", response_model=schemas.LoteResponse)
def update_lote(lote_id: int, lote: schemas.LoteUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece al usuario
    db_lote = db.query(models.Lote).join(models.Finca).filter(
        models.Lote.id == lote_id, 
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    data = lote.model_dump(exclude_unset=True)
    if "finca_id" in data:
        finca = db.query(models.Finca).filter(
            models.Finca.id == data["finca_id"],
            models.Finca.cuenta_id == current_user.id
        ).first()
        if not finca:
            raise HTTPException(status_code=403, detail="No tienes permiso para mover el lote a esa finca")
    
    for key, value in data.items():
        setattr(db_lote, key, value)
    db.commit()
    db.refresh(db_lote)
    return db_lote

@app.delete("/lotes/{lote_id}", status_code=204)
def delete_lote(lote_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece al usuario
    db_lote = db.query(models.Lote).join(models.Finca).filter(
        models.Lote.id == lote_id, 
        models.Finca.cuenta_id == current_user.id
    ).first()
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    db.delete(db_lote)
    db.commit()
    return None

# ==================== CULTIVOS POR LOTE (Para la vista de detalle) ====================

@app.get("/lotes/{lote_id}/cultivos", response_model=list[schemas.CultivoResponse])
def get_cultivos_by_lote(lote_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece al usuario
    lote = db.query(models.Lote).join(models.Finca).filter(
        models.Lote.id == lote_id, 
        models.Finca.cuenta_id == current_user.id
    ).first()
    
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    # Obtener todos los cultivos de este lote
    cultivos = db.query(models.Cultivo).filter(models.Cultivo.lote_id == lote_id).all()
    return cultivos

@app.delete("/lotes/{lote_id}", status_code=204)
def delete_lote(lote_id: int, db: Session = Depends(get_db)):
    db_lote = db.query(models.Lote).filter(models.Lote.id == lote_id).first()
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    db.delete(db_lote)
    db.commit()


# ==================== CULTIVOS ====================

@app.get("/cultivos", response_model=list[schemas.CultivoResponse])
def list_cultivos(db: Session = Depends(get_db)):
    return db.query(models.Cultivo).all()

@app.get("/cultivos/{cultivo_id}", response_model=schemas.CultivoResponse)
def get_cultivo(cultivo_id: int, db: Session = Depends(get_db)):
    cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cultivo_id).first()
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    return cultivo

@app.post("/cultivos", response_model=schemas.CultivoResponse, status_code=201)
def create_cultivo(cultivo: schemas.CultivoCreate, db: Session = Depends(get_db)):
    lote = db.query(models.Lote).filter(models.Lote.id == cultivo.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    db_cultivo = models.Cultivo(**cultivo.model_dump())
    db.add(db_cultivo)
    db.commit()
    db.refresh(db_cultivo)
    return db_cultivo

@app.put("/cultivos/{cultivo_id}", response_model=schemas.CultivoResponse)
def update_cultivo(cultivo_id: int, cultivo: schemas.CultivoUpdate, db: Session = Depends(get_db)):
    db_cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cultivo_id).first()
    if not db_cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    data = cultivo.model_dump(exclude_unset=True)
    if "lote_id" in data:
        lote = db.query(models.Lote).filter(models.Lote.id == data["lote_id"]).first()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote no encontrado")
    for key, value in data.items():
        setattr(db_cultivo, key, value)
    db.commit()
    db.refresh(db_cultivo)
    return db_cultivo

@app.delete("/cultivos/{cultivo_id}", status_code=204)
def delete_cultivo(cultivo_id: int, db: Session = Depends(get_db)):
    db_cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cultivo_id).first()
    if not db_cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    db.delete(db_cultivo)
    db.commit()


# ==================== INSUMOS ====================

@app.get("/insumos", response_model=list[schemas.InsumoResponse])
def list_insumos(db: Session = Depends(get_db)):
    return db.query(models.Insumo).all()

@app.get("/insumos/{insumo_id}", response_model=schemas.InsumoResponse)
def get_insumo(insumo_id: int, db: Session = Depends(get_db)):
    insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return insumo

@app.post("/insumos", response_model=schemas.InsumoResponse, status_code=201)
def create_insumo(insumo: schemas.InsumoCreate, db: Session = Depends(get_db)):
    db_insumo = models.Insumo(**insumo.model_dump())
    db.add(db_insumo)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

@app.put("/insumos/{insumo_id}", response_model=schemas.InsumoResponse)
def update_insumo(insumo_id: int, insumo: schemas.InsumoUpdate, db: Session = Depends(get_db)):
    db_insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not db_insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    for key, value in insumo.model_dump(exclude_unset=True).items():
        setattr(db_insumo, key, value)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

@app.delete("/insumos/{insumo_id}", status_code=204)
def delete_insumo(insumo_id: int, db: Session = Depends(get_db)):
    db_insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not db_insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    db.delete(db_insumo)
    db.commit()


# ==================== COMPRAS ====================

@app.get("/compras", response_model=list[schemas.CompraResponse])
def list_compras(db: Session = Depends(get_db)):
    return db.query(models.Compra).all()

@app.get("/compras/{compra_id}", response_model=schemas.CompraResponse)
def get_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

@app.post("/compras", response_model=schemas.CompraResponse, status_code=201)
def create_compra(compra: schemas.CompraCreate, db: Session = Depends(get_db)):
    insumo = db.query(models.Insumo).filter(models.Insumo.id == compra.insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    db_compra = models.Compra(**compra.model_dump())
    db.add(db_compra)
    
    # Actualizar stock y costo promedio del insumo
    stock_actual = insumo.stock_actual or 0
    costo_actual = insumo.costo_promedio or 0
    nuevo_promedio = ((stock_actual * costo_actual) + (compra.cantidad * compra.costo_unitario)) / (stock_actual + compra.cantidad)
    
    insumo.stock_actual = stock_actual + compra.cantidad
    insumo.costo_promedio = nuevo_promedio
    
    db.commit()
    db.refresh(db_compra)
    return db_compra

@app.put("/compras/{compra_id}", response_model=schemas.CompraResponse)
def update_compra(compra_id: int, compra: schemas.CompraUpdate, db: Session = Depends(get_db)):
    db_compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    for key, value in compra.model_dump(exclude_unset=True).items():
        setattr(db_compra, key, value)
    db.commit()
    db.refresh(db_compra)
    return db_compra

@app.delete("/compras/{compra_id}", status_code=204)
def delete_compra(compra_id: int, db: Session = Depends(get_db)):
    db_compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    db.delete(db_compra)
    db.commit()


# ==================== COSECHAS ====================

@app.get("/cosechas", response_model=list[schemas.CosechaResponse])
def list_cosechas(db: Session = Depends(get_db)):
    return db.query(models.Cosecha).all()

@app.get("/cosechas/{cosecha_id}", response_model=schemas.CosechaResponse)
def get_cosecha(cosecha_id: int, db: Session = Depends(get_db)):
    cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    return cosecha

@app.post("/cosechas", response_model=schemas.CosechaResponse, status_code=201)
def create_cosecha(cosecha: schemas.CosechaCreate, db: Session = Depends(get_db)):
    cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cosecha.cultivo_id).first()
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    db_cosecha = models.Cosecha(**cosecha.model_dump())
    db.add(db_cosecha)
    db.commit()
    db.refresh(db_cosecha)
    return db_cosecha

@app.put("/cosechas/{cosecha_id}", response_model=schemas.CosechaResponse)
def update_cosecha(cosecha_id: int, cosecha: schemas.CosechaUpdate, db: Session = Depends(get_db)):
    db_cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not db_cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    for key, value in cosecha.model_dump(exclude_unset=True).items():
        setattr(db_cosecha, key, value)
    db.commit()
    db.refresh(db_cosecha)
    return db_cosecha

@app.delete("/cosechas/{cosecha_id}", status_code=204)
def delete_cosecha(cosecha_id: int, db: Session = Depends(get_db)):
    db_cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not db_cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    db.delete(db_cosecha)
    db.commit()


# ==================== CATEGORIAS ====================

@app.get("/categorias", response_model=list[schemas.CategoriaResponse])
def list_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()

@app.get("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.post("/categorias", response_model=schemas.CategoriaResponse, status_code=201)
def create_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.put("/categorias/{categoria_id}", response_model=schemas.CategoriaResponse)
def update_categoria(categoria_id: int, categoria: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, value in categoria.model_dump(exclude_unset=True).items():
        setattr(db_categoria, key, value)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.delete("/categorias/{categoria_id}", status_code=204)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(db_categoria)
    db.commit()


# ==================== TAREAS ====================

@app.get("/tareas", response_model=list[schemas.TareaResponse])
def list_tareas(db: Session = Depends(get_db)):
    return db.query(models.Tarea).all()

@app.get("/tareas/{tarea_id}", response_model=schemas.TareaResponse)
def get_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@app.post("/tareas", response_model=schemas.TareaResponse, status_code=201)
def create_tarea(tarea: schemas.TareaCreate, db: Session = Depends(get_db)):
    alcance = db.query(models.Alcance).filter(models.Alcance.id == tarea.alcance_id).first()
    if not alcance:
        raise HTTPException(status_code=404, detail="Alcance no encontrado")
    
    db_tarea = models.Tarea(**tarea.model_dump())
    db.add(db_tarea)
    
    # Si hay insumo, actualizar stock
    if tarea.insumo_id and tarea.cantidad_usada:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == tarea.insumo_id).first()
        if insumo:
            insumo.stock_actual = (insumo.stock_actual or 0) - tarea.cantidad_usada
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.put("/tareas/{tarea_id}", response_model=schemas.TareaResponse)
def update_tarea(tarea_id: int, tarea: schemas.TareaUpdate, db: Session = Depends(get_db)):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    for key, value in tarea.model_dump(exclude_unset=True).items():
        setattr(db_tarea, key, value)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.delete("/tareas/{tarea_id}", status_code=204)
def delete_tarea(tarea_id: int, db: Session = Depends(get_db)):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(db_tarea)
    db.commit()


# ==================== GASTOS OPERATIVOS ====================

@app.get("/gastos-operativos", response_model=list[schemas.GastoOperativoResponse])
def list_gastos_operativos(db: Session = Depends(get_db)):
    return db.query(models.GastoOperativo).all()

@app.get("/gastos-operativos/{gasto_id}", response_model=schemas.GastoOperativoResponse)
def get_gasto_operativo(gasto_id: int, db: Session = Depends(get_db)):
    gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    return gasto

@app.put("/gastos-operativos/{gasto_id}", response_model=schemas.GastoOperativoResponse)
def update_gasto_operativo(gasto_id: int, gasto: schemas.GastoOperativoUpdate, db: Session = Depends(get_db)):
    db_gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not db_gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    for key, value in gasto.model_dump(exclude_unset=True).items():
        setattr(db_gasto, key, value)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto

@app.delete("/gastos-operativos/{gasto_id}", status_code=204)
def delete_gasto_operativo(gasto_id: int, db: Session = Depends(get_db)):
    db_gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not db_gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    db.delete(db_gasto)
    db.commit()