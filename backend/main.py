from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import models
from fastapi.security import OAuth2PasswordRequestForm
import schemas
from database import Base, engine, get_db
from auth import (
    get_password_hash, 
    create_access_token, 
    authenticate_user, 
    get_current_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    require_admin
)
from datetime import date
from sqlalchemy import func

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
        data={"sub": cuenta.usuario, "rol": cuenta.rol}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint adicional para Swagger UI (OAuth2)
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Buscar usuario (form_data.username es lo que envía Swagger)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.usuario, "rol": user.rol}, expires_delta=access_token_expires
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
def delete_alcance(alcance_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_alcance = db.query(models.Alcance).filter(models.Alcance.id == alcance_id).first()
    if not db_alcance:
        raise HTTPException(status_code=404, detail="Alcance no encontrado")
    db.delete(db_alcance)
    db.commit()


# ==================== FINCAS (PROTEGIDO) ====================

@app.get("/fincas", response_model=list[schemas.FincaResponse])
def list_fincas(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Obtener las fincas asociadas al usuario a través de la tabla intermedia
    fincas_cuentas = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.cuenta_id == current_user.id
    ).all()
    
    finca_ids = [fc.finca_id for fc in fincas_cuentas]
    
    if not finca_ids:
        return []
    
    fincas = db.query(models.Finca).filter(models.Finca.id.in_(finca_ids)).all()
    
    # Construir respuesta con propietarios
    resultado = []
    for finca in fincas:
        propietarios = db.query(models.FincaCuenta).filter(
            models.FincaCuenta.finca_id == finca.id
        ).all()
        
        finca_dict = {
            "id": finca.id,
            "nombre": finca.nombre,
            "ubicacion": finca.ubicacion,
            "area_total": finca.area_total,
            "propietarios": [
                {"cuenta_id": p.cuenta_id, "rol_en_finca": p.rol_en_finca}
                for p in propietarios
            ]
        }
        resultado.append(finca_dict)
    
    return resultado


@app.get("/fincas/{finca_id}", response_model=schemas.FincaResponse)
def get_finca(finca_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el usuario tiene acceso a esta finca
    finca_cuenta = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == finca_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not finca_cuenta:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    
    finca = db.query(models.Finca).filter(models.Finca.id == finca_id).first()
    
    # Obtener propietarios
    propietarios = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == finca.id
    ).all()
    
    return {
        "id": finca.id,
        "nombre": finca.nombre,
        "ubicacion": finca.ubicacion,
        "area_total": finca.area_total,
        "propietarios": [
            {"cuenta_id": p.cuenta_id, "rol_en_finca": p.rol_en_finca}
            for p in propietarios
        ]
    }


@app.post("/fincas", response_model=schemas.FincaResponse, status_code=201)
def create_finca(finca: schemas.FincaCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Crear la finca (sin cuenta_id)
    db_finca = models.Finca(
        nombre=finca.nombre,
        ubicacion=finca.ubicacion,
        area_total=finca.area_total
    )
    db.add(db_finca)
    db.commit()
    db.refresh(db_finca)
    
    # Asociar propietarios
    propietarios_ids = finca.propietarios_ids or []
    
    # Si no se especifican propietarios, el usuario que crea es el propietario
    if not propietarios_ids:
        propietarios_ids = [current_user.id]
    
    # Si el usuario que crea no está en la lista, agregarlo también
    if current_user.id not in propietarios_ids:
        propietarios_ids.append(current_user.id)
    
    # Crear registros en la tabla intermedia
    for cuenta_id in propietarios_ids:
        # Verificar que la cuenta existe
        cuenta = db.query(models.Cuenta).filter(models.Cuenta.id == cuenta_id).first()
        if not cuenta:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {cuenta_id} no encontrado")
        
        finca_cuenta = models.FincaCuenta(
            finca_id=db_finca.id,
            cuenta_id=cuenta_id,
            rol_en_finca="propietario"
        )
        db.add(finca_cuenta)
    
    db.commit()
    db.refresh(db_finca)
    
    # Obtener propietarios para la respuesta
    propietarios = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == db_finca.id
    ).all()
    
    return {
        "id": db_finca.id,
        "nombre": db_finca.nombre,
        "ubicacion": db_finca.ubicacion,
        "area_total": db_finca.area_total,
        "propietarios": [
            {"cuenta_id": p.cuenta_id, "rol_en_finca": p.rol_en_finca}
            for p in propietarios
        ]
    }


@app.put("/fincas/{finca_id}", response_model=schemas.FincaResponse)
def update_finca(finca_id: int, finca: schemas.FincaUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el usuario tiene acceso a esta finca
    finca_cuenta = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == finca_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not finca_cuenta:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    
    db_finca = db.query(models.Finca).filter(models.Finca.id == finca_id).first()
    
    # Actualizar campos
    data = finca.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_finca, key, value)
    
    db.commit()
    db.refresh(db_finca)
    
    # Obtener propietarios para la respuesta
    propietarios = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == db_finca.id
    ).all()
    
    return {
        "id": db_finca.id,
        "nombre": db_finca.nombre,
        "ubicacion": db_finca.ubicacion,
        "area_total": db_finca.area_total,
        "propietarios": [
            {"cuenta_id": p.cuenta_id, "rol_en_finca": p.rol_en_finca}
            for p in propietarios
        ]
    }


@app.delete("/fincas/{finca_id}", status_code=204)
def delete_finca(finca_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    # Verificar que el usuario tiene acceso a esta finca
    finca_cuenta = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == finca_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not finca_cuenta:
        raise HTTPException(status_code=404, detail="Finca no encontrada o no tienes permiso")
    
    db_finca = db.query(models.Finca).filter(models.Finca.id == finca_id).first()
    db.delete(db_finca)
    db.commit()

# ==================== LOTES (Con seguridad multi-usuario) ====================

@app.get("/lotes", response_model=list[schemas.LoteResponse])
def list_lotes(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Obtener los IDs de las fincas del usuario actual a través de la tabla intermedia
    fincas_cuentas = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.cuenta_id == current_user.id
    ).all()
    
    fincas_ids = [fc.finca_id for fc in fincas_cuentas]
    
    if not fincas_ids:
        return []
    
    # Solo devolver lotes de las fincas del usuario
    return db.query(models.Lote).filter(models.Lote.finca_id.in_(fincas_ids)).all()


@app.get("/lotes/{lote_id}", response_model=schemas.LoteResponse)
def get_lote(lote_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece a una finca del usuario
    lote = db.query(models.Lote).join(models.Finca).join(models.FincaCuenta).filter(
        models.Lote.id == lote_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    return lote


@app.post("/lotes", response_model=schemas.LoteResponse, status_code=201)
def create_lote(lote: schemas.LoteCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que la finca existe y el usuario tiene acceso a ella
    finca_cuenta = db.query(models.FincaCuenta).filter(
        models.FincaCuenta.finca_id == lote.finca_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not finca_cuenta:
        raise HTTPException(status_code=403, detail="No tienes permiso para agregar lotes a esta finca")
    
    db_lote = models.Lote(**lote.model_dump())
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    return db_lote


@app.put("/lotes/{lote_id}", response_model=schemas.LoteResponse)
def update_lote(lote_id: int, lote: schemas.LoteUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el lote existe y pertenece al usuario
    db_lote = db.query(models.Lote).join(models.Finca).join(models.FincaCuenta).filter(
        models.Lote.id == lote_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    data = lote.model_dump(exclude_unset=True)
    
    if "finca_id" in data:
        # Verificar que el usuario tiene acceso a la nueva finca
        finca_cuenta = db.query(models.FincaCuenta).filter(
            models.FincaCuenta.finca_id == data["finca_id"],
            models.FincaCuenta.cuenta_id == current_user.id
        ).first()
        
        if not finca_cuenta:
            raise HTTPException(status_code=403, detail="No tienes permiso para mover el lote a esa finca")
    
    for key, value in data.items():
        setattr(db_lote, key, value)
    
    db.commit()
    db.refresh(db_lote)
    return db_lote


@app.delete("/lotes/{lote_id}", status_code=204)
def delete_lote(lote_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    # Verificar que el lote existe y pertenece al usuario
    db_lote = db.query(models.Lote).join(models.Finca).join(models.FincaCuenta).filter(
        models.Lote.id == lote_id,
        models.FincaCuenta.cuenta_id == current_user.id
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
    lote = db.query(models.Lote).join(models.Finca).join(models.FincaCuenta).filter(
        models.Lote.id == lote_id,
        models.FincaCuenta.cuenta_id == current_user.id
    ).first()
    
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado o sin permisos")
    
    # Obtener todos los cultivos de este lote
    cultivos = db.query(models.Cultivo).filter(models.Cultivo.lote_id == lote_id).all()
    return cultivos


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
def delete_cultivo(cultivo_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cultivo_id).first()
    if not db_cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    db.delete(db_cultivo)
    db.commit()


# ==================== INSUMOS ====================

@app.get("/insumos", response_model=list[schemas.InsumoResponse])
def list_insumos(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    return db.query(models.Insumo).all()

@app.get("/insumos/{insumo_id}", response_model=schemas.InsumoResponse)
def get_insumo(insumo_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return insumo

@app.post("/insumos", response_model=schemas.InsumoResponse, status_code=201)
def create_insumo(insumo: schemas.InsumoCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_insumo = models.Insumo(**insumo.model_dump())
    db.add(db_insumo)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

@app.put("/insumos/{insumo_id}", response_model=schemas.InsumoResponse)
def update_insumo(insumo_id: int, insumo: schemas.InsumoUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not db_insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    data = insumo.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_insumo, key, value)
    
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

@app.delete("/insumos/{insumo_id}", status_code=204)
def delete_insumo(insumo_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if not db_insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    db.delete(db_insumo)
    db.commit()
    return None

# ==================== COMPRAS (Con seguridad multi-usuario) ====================

@app.get("/compras", response_model=list[schemas.CompraResponse])
def list_compras(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    compras = db.query(models.Compra).all()
    resultado = []
    for compra in compras:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == compra.insumo_id).first()
        compra_dict = {
            "id": compra.id,
            "cantidad": compra.cantidad,
            "costo_unitario": compra.costo_unitario,
            "costo_total": compra.costo_total,
            "fecha": compra.fecha,
            "proveedor": compra.proveedor,
            "nota": compra.nota,
            "insumo_id": compra.insumo_id,
            "nombre_insumo": insumo.nombre if insumo else "N/A"
        }
        resultado.append(compra_dict)
    return resultado

@app.get("/compras/{compra_id}", response_model=schemas.CompraResponse)
def get_compra(compra_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    insumo = db.query(models.Insumo).filter(models.Insumo.id == compra.insumo_id).first()
    return {
        "id": compra.id,
        "cantidad": compra.cantidad,
        "costo_unitario": compra.costo_unitario,
        "costo_total": compra.costo_total,
        "fecha": compra.fecha,
        "proveedor": compra.proveedor,
        "nota": compra.nota,
        "insumo_id": compra.insumo_id,
        "nombre_insumo": insumo.nombre if insumo else "N/A"
    }

@app.post("/compras", response_model=schemas.CompraResponse, status_code=201)
def create_compra(compra: schemas.CompraCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    insumo_id = compra.insumo_id
    
    # Si es un insumo nuevo (ID = -1 o negativo), crearlo primero
    if insumo_id == -1 or insumo_id < 0:
        if not compra.nuevo_insumo_nombre:
            raise HTTPException(status_code=400, detail="Debe proporcionar el nombre del nuevo insumo")
        
        nuevo_insumo = models.Insumo(
            nombre=compra.nuevo_insumo_nombre,
            tipo=compra.nuevo_insumo_tipo or "Otro",
            unidad=compra.nuevo_insumo_unidad or "unidades",
            stock_actual=0,
            costo_promedio=compra.costo_unitario
        )
        db.add(nuevo_insumo)
        db.commit()
        db.refresh(nuevo_insumo)
        insumo_id = nuevo_insumo.id
    else:
        # Verificar que el insumo existe
        insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
        if not insumo:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    # Calcular costo total si no se proporciona
    costo_total = compra.costo_total if compra.costo_total is not None else (compra.cantidad * compra.costo_unitario)
    
    # Crear la compra
    db_compra = models.Compra(
        cantidad=compra.cantidad,
        costo_unitario=compra.costo_unitario,
        costo_total=costo_total,
        fecha=compra.fecha,
        proveedor=compra.proveedor,
        nota=compra.nota,
        insumo_id=insumo_id
    )
    db.add(db_compra)
    
    # Actualizar stock del insumo (sumar la cantidad comprada)
    insumo = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    if insumo:
        insumo.stock_actual = (insumo.stock_actual or 0) + compra.cantidad
        # Actualizar costo promedio ponderado
        stock_anterior = insumo.stock_actual - compra.cantidad
        if stock_anterior > 0:
            costo_anterior_total = insumo.costo_promedio * stock_anterior
            insumo.costo_promedio = (costo_anterior_total + costo_total) / insumo.stock_actual
        else:
            insumo.costo_promedio = compra.costo_unitario
    
    db.commit()
    db.refresh(db_compra)
    
    insumo_final = db.query(models.Insumo).filter(models.Insumo.id == insumo_id).first()
    return {
        "id": db_compra.id,
        "cantidad": db_compra.cantidad,
        "costo_unitario": db_compra.costo_unitario,
        "costo_total": db_compra.costo_total,
        "fecha": db_compra.fecha,
        "proveedor": db_compra.proveedor,
        "nota": db_compra.nota,
        "insumo_id": db_compra.insumo_id,
        "nombre_insumo": insumo_final.nombre if insumo_final else "N/A"
    }

@app.put("/compras/{compra_id}", response_model=schemas.CompraResponse)
def update_compra(compra_id: int, compra: schemas.CompraUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    data = compra.model_dump(exclude_unset=True)
    
    # Si cambia el insumo, verificar que existe
    if "insumo_id" in data:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == data["insumo_id"]).first()
        if not insumo:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    for key, value in data.items():
        setattr(db_compra, key, value)
    
    # Recalcular costo total si cambiaron cantidad o costo_unitario
    if "cantidad" in data or "costo_unitario" in data:
        db_compra.costo_total = db_compra.cantidad * db_compra.costo_unitario
    
    db.commit()
    db.refresh(db_compra)
    
    insumo = db.query(models.Insumo).filter(models.Insumo.id == db_compra.insumo_id).first()
    return {
        "id": db_compra.id,
        "cantidad": db_compra.cantidad,
        "costo_unitario": db_compra.costo_unitario,
        "costo_total": db_compra.costo_total,
        "fecha": db_compra.fecha,
        "proveedor": db_compra.proveedor,
        "nota": db_compra.nota,
        "insumo_id": db_compra.insumo_id,
        "nombre_insumo": insumo.nombre if insumo else "N/A"
    }

@app.delete("/compras/{compra_id}", status_code=204)
def delete_compra(compra_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    db.delete(db_compra)
    db.commit()
    return None

# ==================== COSECHAS ====================

@app.get("/cosechas", response_model=list[schemas.CosechaResponse])
def list_cosechas(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    cosechas = db.query(models.Cosecha).all()
    resultado = []
    for cosecha in cosechas:
        cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cosecha.cultivo_id).first() if cosecha.cultivo_id else None
        lote = None
        finca = None
        if cultivo:
            lote = db.query(models.Lote).filter(models.Lote.id == cultivo.lote_id).first() if cultivo.lote_id else None
            finca = db.query(models.Finca).filter(models.Finca.id == lote.finca_id).first() if lote and lote.finca_id else None
        
        resultado.append({
            "id": cosecha.id,
            "fecha": cosecha.fecha,
            "cantidad": cosecha.cantidad,
            "unidad": cosecha.unidad,
            "notas": cosecha.notas,
            "cultivo_id": cosecha.cultivo_id,
            "nombre_cultivo": cultivo.nombre if cultivo else "N/A",
            "nombre_lote": lote.nombre if lote else "N/A",
            "nombre_finca": finca.nombre if finca else "N/A"
        })
    return resultado

@app.get("/cosechas/{cosecha_id}", response_model=schemas.CosechaResponse)
def get_cosecha(cosecha_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    
    cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cosecha.cultivo_id).first() if cosecha.cultivo_id else None
    lote = None
    finca = None
    if cultivo:
        lote = db.query(models.Lote).filter(models.Lote.id == cultivo.lote_id).first() if cultivo.lote_id else None
        finca = db.query(models.Finca).filter(models.Finca.id == lote.finca_id).first() if lote and lote.finca_id else None
    
    return {
        "id": cosecha.id,
        "fecha": cosecha.fecha,
        "cantidad": cosecha.cantidad,
        "unidad": cosecha.unidad,
        "notas": cosecha.notas,
        "cultivo_id": cosecha.cultivo_id,
        "nombre_cultivo": cultivo.nombre if cultivo else "N/A",
        "nombre_lote": lote.nombre if lote else "N/A",
        "nombre_finca": finca.nombre if finca else "N/A"
    }

@app.post("/cosechas", response_model=schemas.CosechaResponse, status_code=201)
def create_cosecha(cosecha: schemas.CosechaCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # Verificar que el cultivo existe
    cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == cosecha.cultivo_id).first()
    if not cultivo:
        raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    
    db_cosecha = models.Cosecha(**cosecha.model_dump())
    db.add(db_cosecha)
    db.commit()
    db.refresh(db_cosecha)
    
    lote = db.query(models.Lote).filter(models.Lote.id == cultivo.lote_id).first() if cultivo.lote_id else None
    finca = db.query(models.Finca).filter(models.Finca.id == lote.finca_id).first() if lote and lote.finca_id else None
    
    return {
        "id": db_cosecha.id,
        "fecha": db_cosecha.fecha,
        "cantidad": db_cosecha.cantidad,
        "unidad": db_cosecha.unidad,
        "notas": db_cosecha.notas,
        "cultivo_id": db_cosecha.cultivo_id,
        "nombre_cultivo": cultivo.nombre,
        "nombre_lote": lote.nombre if lote else "N/A",
        "nombre_finca": finca.nombre if finca else "N/A"
    }

@app.put("/cosechas/{cosecha_id}", response_model=schemas.CosechaResponse)
def update_cosecha(cosecha_id: int, cosecha: schemas.CosechaUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not db_cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    
    data = cosecha.model_dump(exclude_unset=True)
    
    # Si cambia el cultivo, verificar que existe
    if "cultivo_id" in data:
        cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == data["cultivo_id"]).first()
        if not cultivo:
            raise HTTPException(status_code=404, detail="Cultivo no encontrado")
    
    for key, value in data.items():
        setattr(db_cosecha, key, value)
    
    db.commit()
    db.refresh(db_cosecha)
    
    cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == db_cosecha.cultivo_id).first() if db_cosecha.cultivo_id else None
    lote = None
    finca = None
    if cultivo:
        lote = db.query(models.Lote).filter(models.Lote.id == cultivo.lote_id).first() if cultivo.lote_id else None
        finca = db.query(models.Finca).filter(models.Finca.id == lote.finca_id).first() if lote and lote.finca_id else None
    
    return {
        "id": db_cosecha.id,
        "fecha": db_cosecha.fecha,
        "cantidad": db_cosecha.cantidad,
        "unidad": db_cosecha.unidad,
        "notas": db_cosecha.notas,
        "cultivo_id": db_cosecha.cultivo_id,
        "nombre_cultivo": cultivo.nombre if cultivo else "N/A",
        "nombre_lote": lote.nombre if lote else "N/A",
        "nombre_finca": finca.nombre if finca else "N/A"
    }

@app.delete("/cosechas/{cosecha_id}", status_code=204)
def delete_cosecha(cosecha_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_cosecha = db.query(models.Cosecha).filter(models.Cosecha.id == cosecha_id).first()
    if not db_cosecha:
        raise HTTPException(status_code=404, detail="Cosecha no encontrada")
    
    db.delete(db_cosecha)
    db.commit()
    return None

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
def delete_categoria(categoria_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(db_categoria)
    db.commit()


# ==================== TAREAS (Con seguridad multi-usuario) ====================

@app.get("/tareas", response_model=list[schemas.TareaResponse])
def list_tareas(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    tareas = db.query(models.Tarea).all()
    hoy = date.today()
    
    actualizado = False
    
    for tarea in tareas:
        # Si tiene fecha límite, ya pasó hoy, y no está cerrada (Completada/Cancelada/Vencida)
        if (tarea.fecha_limite and 
            tarea.fecha_limite < hoy and 
            tarea.estado not in ['Completada', 'Cancelada', 'Vencida']):
            
            tarea.estado = 'Vencida'
            actualizado = True
            
    # Si hubo cambios, los guardamos en la base de datos
    if actualizado:
        db.commit()
        
    return tareas

@app.get("/tareas/{tarea_id}", response_model=schemas.TareaResponse)
def get_tarea(tarea_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@app.post("/tareas", response_model=schemas.TareaResponse, status_code=201)
def create_tarea(tarea: schemas.TareaCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    
    # Validar que fecha_limite no sea anterior a fecha
    if tarea.fecha and tarea.fecha_limite:
        if tarea.fecha_limite < tarea.fecha:
            raise HTTPException(
                status_code=400, 
                detail="La fecha límite no puede ser anterior a la fecha de asignación"
            )
    
    # Validar que el alcance existe
    alcance = db.query(models.Alcance).filter(models.Alcance.id == tarea.alcance_id).first()
    if not alcance:
        raise HTTPException(status_code=404, detail="Alcance no encontrado")
    
    # Validar que el insumo existe si se proporciona
    if tarea.insumo_id:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == tarea.insumo_id).first()
        if not insumo:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    db_tarea = models.Tarea(**tarea.model_dump())
    db.add(db_tarea)
    
    # Si hay insumo, actualizar stock (mantenemos tu lógica original)
    if tarea.insumo_id and tarea.cantidad_usada:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == tarea.insumo_id).first()
        if insumo:
            insumo.stock_actual = (insumo.stock_actual or 0) - tarea.cantidad_usada
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.put("/tareas/{tarea_id}", response_model=schemas.TareaResponse)
def update_tarea(tarea_id: int, tarea: schemas.TareaUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    data = tarea.model_dump(exclude_unset=True)
    
    # Validar que fecha_limite no sea anterior a fecha
    if tarea.fecha and tarea.fecha_limite:
        if tarea.fecha_limite < tarea.fecha:
            raise HTTPException(
                status_code=400, 
                detail="La fecha límite no puede ser anterior a la fecha de asignación"
            )
    
    if "alcance_id" in data:
        alcance = db.query(models.Alcance).filter(models.Alcance.id == data["alcance_id"]).first()
        if not alcance:
            raise HTTPException(status_code=404, detail="Alcance no encontrado")
    
    if "insumo_id" in data and data["insumo_id"] is not None:
        insumo = db.query(models.Insumo).filter(models.Insumo.id == data["insumo_id"]).first()
        if not insumo:
            raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    for key, value in data.items():
        setattr(db_tarea, key, value)
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.delete("/tareas/{tarea_id}", status_code=204)
def delete_tarea(tarea_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(db_tarea)
    db.commit()
    return None

# ==================== GASTOS OPERATIVOS ====================

@app.get("/gastos-operativos", response_model=list[schemas.GastoOperativoResponse])
def list_gastos_operativos(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    gastos = db.query(models.GastoOperativo).all()
    resultado = []
    for gasto in gastos:
        categoria = db.query(models.Categoria).filter(models.Categoria.id == gasto.categoria_id).first() if gasto.categoria_id else None
        tarea = db.query(models.Tarea).filter(models.Tarea.id == gasto.tarea_id).first() if gasto.tarea_id else None
        resultado.append({
            "id": gasto.id,
            "concepto": gasto.concepto,
            "monto": gasto.monto,
            "fecha": gasto.fecha,
            "fecha_limite": gasto.fecha_limite,
            "categoria_id": gasto.categoria_id,
            "alcance_id": gasto.alcance_id,
            "finca_id": gasto.finca_id,
            "lote_id": gasto.lote_id,
            "cultivo_id": gasto.cultivo_id,
            "tarea_id": gasto.tarea_id,
            "nombre_categoria": categoria.nombre if categoria else None,
            "nombre_tarea": tarea.nombre if tarea else None
        })
    return resultado

@app.get("/gastos-operativos/{gasto_id}", response_model=schemas.GastoOperativoResponse)
def get_gasto_operativo(gasto_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    
    categoria = db.query(models.Categoria).filter(models.Categoria.id == gasto.categoria_id).first() if gasto.categoria_id else None
    tarea = db.query(models.Tarea).filter(models.Tarea.id == gasto.tarea_id).first() if gasto.tarea_id else None
    return {
        "id": gasto.id,
        "concepto": gasto.concepto,
        "monto": gasto.monto,
        "fecha": gasto.fecha,
        "fecha_limite": gasto.fecha_limite,
        "categoria_id": gasto.categoria_id,
        "alcance_id": gasto.alcance_id,
        "finca_id": gasto.finca_id,
        "lote_id": gasto.lote_id,
        "cultivo_id": gasto.cultivo_id,
        "tarea_id": gasto.tarea_id,
        "nombre_categoria": categoria.nombre if categoria else None,
        "nombre_tarea": tarea.nombre if tarea else None
    }

@app.post("/gastos-operativos", response_model=schemas.GastoOperativoResponse, status_code=201)
def create_gasto_operativo(gasto: schemas.GastoOperativoCreate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    
    #  VALIDACIÓN DE FECHAS (va al inicio, antes de cualquier lógica)
    if gasto.fecha and gasto.fecha_limite:
        if gasto.fecha_limite < gasto.fecha:
            raise HTTPException(
                status_code=400, 
                detail="La fecha límite no puede ser anterior a la fecha de asignación"
            )
    
    db_gasto = models.GastoOperativo(**gasto.model_dump())
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    
    categoria = db.query(models.Categoria).filter(models.Categoria.id == gasto.categoria_id).first() if gasto.categoria_id else None
    tarea = db.query(models.Tarea).filter(models.Tarea.id == gasto.tarea_id).first() if gasto.tarea_id else None
    
    return {
        "id": db_gasto.id,
        "concepto": db_gasto.concepto,
        "monto": db_gasto.monto,
        "fecha": db_gasto.fecha,
        "categoria_id": db_gasto.categoria_id,
        "alcance_id": db_gasto.alcance_id,
        "finca_id": db_gasto.finca_id,
        "lote_id": db_gasto.lote_id,
        "cultivo_id": db_gasto.cultivo_id,
        "tarea_id": db_gasto.tarea_id,
        "nombre_categoria": categoria.nombre if categoria else None,
        "nombre_tarea": tarea.nombre if tarea else None
    }

@app.put("/gastos-operativos/{gasto_id}", response_model=schemas.GastoOperativoResponse)
def update_gasto_operativo(gasto_id: int, gasto: schemas.GastoOperativoUpdate, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    db_gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not db_gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    
    data = gasto.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_gasto, key, value)
    
    db.commit()
    db.refresh(db_gasto)
    
    categoria = db.query(models.Categoria).filter(models.Categoria.id == db_gasto.categoria_id).first() if db_gasto.categoria_id else None
    tarea = db.query(models.Tarea).filter(models.Tarea.id == db_gasto.tarea_id).first() if db_gasto.tarea_id else None
    
    return {
        "id": db_gasto.id,
        "concepto": db_gasto.concepto,
        "monto": db_gasto.monto,
        "fecha": db_gasto.fecha,
        "categoria_id": db_gasto.categoria_id,
        "alcance_id": db_gasto.alcance_id,
        "finca_id": db_gasto.finca_id,
        "lote_id": db_gasto.lote_id,
        "cultivo_id": db_gasto.cultivo_id,
        "tarea_id": db_gasto.tarea_id,
        "nombre_categoria": categoria.nombre if categoria else None,
        "nombre_tarea": tarea.nombre if tarea else None
    }

@app.delete("/gastos-operativos/{gasto_id}", status_code=204)
def delete_gasto_operativo(gasto_id: int, db: Session = Depends(get_db), current_user: models.Cuenta = Depends(require_admin)):
    db_gasto = db.query(models.GastoOperativo).filter(models.GastoOperativo.id == gasto_id).first()
    if not db_gasto:
        raise HTTPException(status_code=404, detail="Gasto operativo no encontrado")
    
    db.delete(db_gasto)
    db.commit()
    return None

# ==================== DASHBOARD ====================

@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: models.Cuenta = Depends(get_current_user)):
    # 1️ Obtener SOLO las fincas del usuario actual
    fincas_usuario = db.query(models.FincaCuenta).filter(
    models.FincaCuenta.cuenta_id == current_user.id
    ).all()
    
    finca_ids = [fc.finca_id for fc in fincas_usuario]
    
    # 2️⃣ Conteos básicos (SOLO del usuario)
    total_fincas = len(fincas_usuario)  # ✅ Cuenta solo las fincas del usuario
    
    # Lotes: solo de las fincas del usuario
    total_lotes = 0
    if finca_ids:
        total_lotes = db.query(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).count()
    
    # Cultivos: solo de los lotes del usuario
    total_cultivos = 0
    if finca_ids:
        total_cultivos = db.query(models.Cultivo).join(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).count()
    
    # 3️⃣ Tareas (solo de cultivos/lotes del usuario)
    tareas_pendientes = 0
    tareas_vencidas = 0
    tareas_lista = []
    
    if finca_ids:
        # Obtener IDs de lotes del usuario
        lotes_ids = [lote.id for lote in db.query(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).all()]
        
        # Obtener IDs de cultivos del usuario
        cultivos_ids = [cultivo.id for cultivo in db.query(models.Cultivo).join(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).all()]
        
        # Tareas pendientes
        tareas_pendientes = db.query(models.Tarea).filter(
            models.Tarea.estado.in_(['Pendiente', 'En progreso']),
            (models.Tarea.lote_id.in_(lotes_ids) if lotes_ids else False) |
            (models.Tarea.cultivo_id.in_(cultivos_ids) if cultivos_ids else False)
        ).count()
        
        # Tareas vencidas
        tareas_vencidas = db.query(models.Tarea).filter(
            models.Tarea.estado == 'Vencida',
            (models.Tarea.lote_id.in_(lotes_ids) if lotes_ids else False) |
            (models.Tarea.cultivo_id.in_(cultivos_ids) if cultivos_ids else False)
        ).count()
        
        # Últimas tareas pendientes
        ultimas_tareas = db.query(models.Tarea).filter(
            models.Tarea.estado.in_(['Pendiente', 'En progreso']),
            (models.Tarea.lote_id.in_(lotes_ids) if lotes_ids else False) |
            (models.Tarea.cultivo_id.in_(cultivos_ids) if cultivos_ids else False)
        ).order_by(models.Tarea.fecha.desc()).limit(5).all()
        
        for t in ultimas_tareas:
            tareas_lista.append({
                "id": t.id,
                "nombre": t.nombre,
                "estado": t.estado,
                "fecha_limite": str(t.fecha_limite) if t.fecha_limite else None,
                "tipo": t.tipo
            })
    
    # 4️⃣ Insumos con stock bajo (globales, no filtrados por usuario)
    insumos_stock_bajo = db.query(models.Insumo).filter(
        models.Insumo.stock_actual < 10
    ).order_by(models.Insumo.stock_actual.asc()).limit(5).all()
    
    insumos_lista = []
    for i in insumos_stock_bajo:
        insumos_lista.append({
            "id": i.id,
            "nombre": i.nombre,
            "stock_actual": i.stock_actual,
            "unidad": i.unidad
        })
    
    # 5️ Últimas cosechas (SOLO del usuario)
    cosechas_lista = []
    if finca_ids:
        cultivos_ids_cosechas = [c.id for c in db.query(models.Cultivo).join(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).all()]
        
        if cultivos_ids_cosechas:
            ultimas_cosechas = db.query(models.Cosecha).filter(
                models.Cosecha.cultivo_id.in_(cultivos_ids_cosechas)
            ).order_by(models.Cosecha.fecha.desc()).limit(5).all()
            
            for c in ultimas_cosechas:
                cultivo = db.query(models.Cultivo).filter(models.Cultivo.id == c.cultivo_id).first()
                cosechas_lista.append({
                    "id": c.id,
                    "cultivo": cultivo.nombre if cultivo else "N/A",
                    "cantidad": c.cantidad,
                    "unidad": c.unidad,
                    "fecha": str(c.fecha) if c.fecha else None
                })
    
    # 6️ Gastos por categoría (SOLO del usuario)
    gastos_chart = []
    if finca_ids:
        gastos_por_categoria = db.query(
            models.Categoria.nombre,
            func.sum(models.GastoOperativo.monto).label('total')
        ).join(
            models.GastoOperativo, models.Categoria.id == models.GastoOperativo.categoria_id
        ).filter(
            models.GastoOperativo.finca_id.in_(finca_ids)
        ).group_by(
            models.Categoria.nombre
        ).all()
        
        gastos_chart = [{"categoria": g.nombre, "total": float(g.total)} for g in gastos_por_categoria]
    
    # 7️ Cosechas por cultivo (SOLO del usuario)
    cosechas_chart = []
    if finca_ids:
        cultivos_ids_chart = [c.id for c in db.query(models.Cultivo).join(models.Lote).filter(
            models.Lote.finca_id.in_(finca_ids)
        ).all()]
        
        if cultivos_ids_chart:
            cosechas_por_cultivo = db.query(
                models.Cultivo.nombre,
                func.sum(models.Cosecha.cantidad).label('total')
            ).join(
                models.Cosecha, models.Cultivo.id == models.Cosecha.cultivo_id
            ).filter(
                models.Cultivo.id.in_(cultivos_ids_chart)
            ).group_by(
                models.Cultivo.nombre
            ).all()
            
            cosechas_chart = [{"cultivo": c.nombre, "total": float(c.total)} for c in cosechas_por_cultivo]
    
    # 8️⃣ Total invertido (SOLO del usuario)
    total_compras = 0
    total_gastos = 0
    
    if finca_ids:
        # Compras de insumos (globales, no filtradas por finca)
        total_compras = db.query(func.sum(models.Compra.costo_total)).scalar() or 0
        
        # Gastos operativos de las fincas del usuario
        total_gastos = db.query(func.sum(models.GastoOperativo.monto)).filter(
            models.GastoOperativo.finca_id.in_(finca_ids)
        ).scalar() or 0
    
    total_invertido = float(total_compras) + float(total_gastos)
    
    # 9️ Retornar respuesta
    return {
        "kpis": {
            "total_fincas": total_fincas,
            "total_lotes": total_lotes,
            "total_cultivos": total_cultivos,
            "tareas_pendientes": tareas_pendientes,
            "tareas_vencidas": tareas_vencidas,
            "insumos_stock_bajo": len(insumos_stock_bajo),
            "total_invertido": total_invertido
        },
        "ultimas_tareas": tareas_lista,
        "insumos_stock_bajo": insumos_lista,
        "ultimas_cosechas": cosechas_lista,
        "gastos_por_categoria": gastos_chart,
        "cosechas_por_cultivo": cosechas_chart
    }
    # ==================== GESTIÓN DE COLABORADORES (SOLO ADMIN) ====================

@app.post("/admin/crear-colaborador", status_code=201)
def crear_colaborador(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.Cuenta = Depends(require_admin)
):
    """
    Solo administradores pueden crear colaboradores y asignarles fincas.
    data = {
        "usuario": "nombre_usuario",
        "password": "contraseña",
        "finca_ids": [1, 2, 3]  # IDs de fincas a asignar
    }
    """
    usuario = data.get("usuario")
    password = data.get("password")
    finca_ids = data.get("finca_ids", [])
    
    # Validar que se proporcionaron los datos necesarios
    if not usuario or not password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios")
    
    # Verificar que el usuario no existe
    db_cuenta = db.query(models.Cuenta).filter(models.Cuenta.usuario == usuario).first()
    if db_cuenta:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear el nuevo usuario con rol "colaborador"
    hashed_password = get_password_hash(password)
    nuevo_colaborador = models.Cuenta(
        usuario=usuario,
        hashed_password=hashed_password,
        rol="colaborador"
    )
    db.add(nuevo_colaborador)
    db.commit()
    db.refresh(nuevo_colaborador)
    
    # Asignar las fincas al nuevo colaborador
    fincas_asignadas = []
    for finca_id in finca_ids:
        # Verificar que la finca existe y pertenece al admin
        finca_cuenta = db.query(models.FincaCuenta).filter(
            models.FincaCuenta.finca_id == finca_id,
            models.FincaCuenta.cuenta_id == current_user.id,
            models.FincaCuenta.rol_en_finca == "propietario"
        ).first()
        
        if finca_cuenta:
            # Crear la relación en fincas_cuentas
            relacion = models.FincaCuenta(
                finca_id=finca_id,
                cuenta_id=nuevo_colaborador.id,
                rol_en_finca="colaborador"
            )
            db.add(relacion)
            fincas_asignadas.append(finca_id)
    
    db.commit()
    
    return {
        "message": f"Colaborador '{usuario}' creado exitosamente",
        "usuario_id": nuevo_colaborador.id,
        "fincas_asignadas": fincas_asignadas
    }


@app.get("/admin/colaboradores")
def listar_colaboradores(
    db: Session = Depends(get_db),
    current_user: models.Cuenta = Depends(require_admin)
):
    """Lista todos los colaboradores y sus fincas asignadas (solo admin)"""
    colaboradores = db.query(models.Cuenta).filter(
        models.Cuenta.rol == "colaborador"
    ).all()
    
    resultado = []
    for colab in colaboradores:
        # Obtener fincas asignadas a este colaborador
        fincas_cuentas = db.query(models.FincaCuenta).filter(
            models.FincaCuenta.cuenta_id == colab.id
        ).all()
        
        fincas_asignadas = []
        for fc in fincas_cuentas:
            finca = db.query(models.Finca).filter(models.Finca.id == fc.finca_id).first()
            if finca:
                fincas_asignadas.append({
                    "finca_id": finca.id,
                    "nombre": finca.nombre
                })
        
        resultado.append({
            "id": colab.id,
            "usuario": colab.usuario,
            "rol": colab.rol,
            "fincas_asignadas": fincas_asignadas
        })
    
    return resultado


@app.delete("/admin/colaboradores/{colaborador_id}", status_code=204)
def eliminar_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: models.Cuenta = Depends(require_admin)
):
    """Elimina un colaborador y sus relaciones con fincas (solo admin)"""
    colaborador = db.query(models.Cuenta).filter(
        models.Cuenta.id == colaborador_id,
        models.Cuenta.rol == "colaborador"
    ).first()
    
    if not colaborador:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado")
    
    # Eliminar relaciones con fincas
    db.query(models.FincaCuenta).filter(
        models.FincaCuenta.cuenta_id == colaborador_id
    ).delete()
    
    # Eliminar el usuario
    db.delete(colaborador)
    db.commit()
    
    return None
    