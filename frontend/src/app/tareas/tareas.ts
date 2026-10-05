import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TareasService, Tarea } from '../services/tareas.service';
import { FincasService, Finca } from '../services/fincas.service';
import { LotesService, Lote } from '../services/lotes.service';
import { CultivosService, Cultivo } from '../services/cultivos.service';
import { InsumosService, Insumo } from '../services/insumos.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-tareas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './tareas.html',
  styleUrls: ['./tareas.css']
})
export class TareasComponent implements OnInit {
  tareas: Tarea[] = [];
  errorMessage = '';
  showForm = false;
  editingTarea: Tarea | null = null;
  hoy = new Date().toISOString().split('T')[0];
  manana = new Date(Date.now() + 86400000).toISOString().split('T')[0];
  
  // Listas para los selects
  fincas: Finca[] = [];
  lotes: Lote[] = [];
  cultivos: Cultivo[] = [];
  insumos: Insumo[] = [];

  // Datos del formulario
  nombre = '';
  descripcion = '';
  fecha = '';
  fecha_limite = '';
  estado = '';
  tipo = '';
  alcance_id: number | undefined = undefined;
  
  // IDs específicos seleccionados
  selected_finca_id: number | undefined = undefined;
  selected_lote_id: number | undefined = undefined;
  selected_cultivo_id: number | undefined = undefined;
  
  // Insumo seleccionado (ahora es un objeto completo)
  selected_insumo: Insumo | null = null;
  cantidad_usada: number | undefined = undefined;

  // Opciones
  estados = ['Pendiente', 'En progreso', 'Completada', 'Cancelada', 'Vencida'];
  tipos = [
    "Preparación de terreno", "Análisis de suelos", "Encalado",
    "Siembra directa", "Transplante", "Resiembra",
    "Riego", "Fertilización", "Fumigación", "Deshierbe", "Poda", "Tutorado", "Raleo",
    "Cosecha", "Transporte interno", "Clasificación y Empaque",
    "Mantenimiento de maquinaria", "Reparación de infraestructura", "Limpieza general",
    "Gestión de personal", "Trámites y Legal", "Otro"
  ];
  alcances = [
    { id: 1, tipo: 'Finca' },
    { id: 2, tipo: 'Lote' },
    { id: 3, tipo: 'Cultivo' }
  ];

  constructor(
    private tareasService: TareasService,
    private fincasService: FincasService,
    private lotesService: LotesService,
    private cultivosService: CultivosService,
    private insumosService: InsumosService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadTareas();
    this.loadSelects();
  }

  irAFincas() { this.router.navigate(['/fincas']); }
  irALotes() { this.router.navigate(['/lotes']); }
  irACultivos() { this.router.navigate(['/cultivos']); }
  irATareas() { this.router.navigate(['/tareas']); }
  irAInsumos() { this.router.navigate(['/insumos']); }
  irACompras() { this.router.navigate(['/compras']); }
  irAGastosOperativos() { this.router.navigate(['/gastos-operativos']); }

  loadSelects() {
    this.fincasService.getFincas().subscribe(f => { this.fincas = f; this.cdr.detectChanges(); });
    this.lotesService.getLotes().subscribe(l => { this.lotes = l; this.cdr.detectChanges(); });
    this.cultivosService.getCultivos().subscribe(c => { this.cultivos = c; this.cdr.detectChanges(); });
    this.insumosService.getInsumos().subscribe(i => { this.insumos = i; this.cdr.detectChanges(); });
  }

  loadTareas() {
    this.tareasService.getTareas().subscribe({
      next: (tareas: Tarea[]) => {
        this.tareas = tareas;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar las tareas';
          this.cdr.detectChanges();
        }
      }
    });
  }

  onAlcanceChange() {
    this.selected_finca_id = undefined;
    this.selected_lote_id = undefined;
    this.selected_cultivo_id = undefined;
  }

  onAlcanceSelected(value: string) { 
    this.alcance_id = value ? Number(value) : undefined;
    this.onAlcanceChange();
  }

  onInsumoChange(insumoId: number | undefined) {
    if (insumoId) {
      this.selected_insumo = this.insumos.find(i => i.id === insumoId) ?? null;
    } else {
      this.selected_insumo = null;
    }
    this.cdr.detectChanges();
  }

  // Calcula el costo total de la tarea con el insumo seleccionado
  getCostoTotal(): number {
    if (this.selected_insumo && this.cantidad_usada) {
      const costo = this.selected_insumo.costo_promedio ?? 0;
      return costo * this.cantidad_usada;
    }
    return 0;
  }

  formatearPesos(valor: number | undefined): string {
    if (valor === undefined || valor === null) return '$ 0';
    const partes = valor.toFixed(2).split('.');
    const entero = partes[0];
    const decimal = partes[1];
    const enteroFormateado = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `$ ${enteroFormateado},${decimal}`;
  }

  openForm(tarea?: Tarea) {
    if (tarea) {
      this.editingTarea = tarea;
      this.nombre = tarea.nombre;
      this.descripcion = tarea.descripcion || '';
      this.fecha = tarea.fecha || '';
      this.fecha_limite = tarea.fecha_limite || '';
      this.estado = tarea.estado || '';
      this.tipo = tarea.tipo || '';
      this.alcance_id = tarea.alcance_id;
      this.selected_finca_id = undefined;
      this.selected_lote_id = tarea.lote_id;
      this.selected_cultivo_id = tarea.cultivo_id;
      this.cantidad_usada = tarea.cantidad_usada;
      
      // Buscar el insumo por ID
      if (tarea.insumo_id) {
        this.selected_insumo = this.insumos.find(i => i.id === tarea.insumo_id) || null;
      } else {
        this.selected_insumo = null;
      }
    } else {
      this.editingTarea = null;
      this.nombre = '';
      this.descripcion = '';
      this.fecha = this.hoy; 
      this.fecha = '';
      this.fecha_limite = '';
      this.estado = '';
      this.tipo = '';
      this.alcance_id = undefined;
      this.selected_finca_id = undefined;
      this.selected_lote_id = undefined;
      this.selected_cultivo_id = undefined;
      this.selected_insumo = null;
      this.cantidad_usada = undefined;
    }
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingTarea = null;
    this.cdr.detectChanges();
  }

  saveTarea() {

    // Validación: fecha límite debe ser al menos mañana
  if (this.fecha_limite && this.fecha_limite <= this.hoy) {
    this.errorMessage = 'La fecha límite debe ser al menos un día después de hoy';
    this.cdr.detectChanges();
    return;
  }

    const tareaData: Partial<Tarea> = {
      nombre: this.nombre,
      descripcion: this.descripcion || undefined,
      fecha: this.fecha || undefined,
      fecha_limite: this.fecha_limite || undefined,
      estado: this.estado || undefined,
      tipo: this.tipo || undefined,
      alcance_id: this.alcance_id,
      lote_id: this.alcance_id === 2 ? this.selected_lote_id : undefined,
      cultivo_id: this.alcance_id === 3 ? this.selected_cultivo_id : undefined,
      insumo_id: this.selected_insumo?.id,
      cantidad_usada: this.cantidad_usada
    };

    const request = this.editingTarea
      ? this.tareasService.updateTarea(this.editingTarea.id, tareaData)
      : this.tareasService.createTarea(tareaData);

    request.subscribe({
      next: () => {
        this.loadTareas();
        this.loadSelects(); // Recargar insumos porque el stock cambió
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al guardar la tarea';
        this.cdr.detectChanges();
      }
    });
  }

  deleteTarea(id: number) {
    if (confirm('¿Estás seguro de eliminar esta tarea?')) {
      this.tareasService.deleteTarea(id).subscribe({
        next: () => {
          this.loadTareas();
          this.loadSelects(); // Recargar insumos
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar la tarea';
          this.cdr.detectChanges();
        }
      });
    }
  }

  getNombreAlcance(tarea: Tarea): string {
    const alcance = this.alcances.find(a => a.id === tarea.alcance_id);
    const tipoAlcance = alcance ? alcance.tipo : 'N/A';
    
    let especifico = '';
    if (tarea.alcance_id === 1) {
      especifico = tarea.lote_id ? ` (Finca específica)` : ' (Todas las fincas)';
    } else if (tarea.alcance_id === 2) {
      especifico = tarea.lote_id ? ` (Lote específico)` : ' (Todos los lotes)';
    } else if (tarea.alcance_id === 3) {
      especifico = tarea.cultivo_id ? ` (Cultivo específico)` : ' (Todos los cultivos)';
    }
    
    return tipoAlcance + especifico;
  }

  logout() {
    this.authService.logout();
  }
}