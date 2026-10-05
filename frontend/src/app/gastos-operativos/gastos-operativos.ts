import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { GastosOperativosService, GastoOperativo } from '../services/gastos-operativos.service';
import { TareasService, Tarea } from '../services/tareas.service';
import { FincasService, Finca } from '../services/fincas.service';
import { LotesService, Lote } from '../services/lotes.service';
import { CultivosService, Cultivo } from '../services/cultivos.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-gastos-operativos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gastos-operativos.html',
  styleUrls: ['./gastos-operativos.css']
})
export class GastosOperativosComponent implements OnInit {
  gastos: GastoOperativo[] = [];
  tareas: Tarea[] = [];
  fincas: Finca[] = [];
  lotes: Lote[] = [];
  cultivos: Cultivo[] = [];
  errorMessage = '';
  showForm = false;
  editingGasto: GastoOperativo | null = null;
  hoy = new Date().toISOString().split('T')[0];
  manana = new Date(Date.now() + 86400000).toISOString().split('T')[0]; 
  
  // Datos del formulario
  concepto = '';
  monto: number | undefined = undefined;
  fecha = '';
  fecha_limite = '';
  categoria_id: number | undefined = undefined;
  alcance_id: number | undefined = undefined;
  
  // IDs específicos seleccionados
  selected_finca_id: number | undefined = undefined;
  selected_lote_id: number | undefined = undefined;
  selected_cultivo_id: number | undefined = undefined;
  
  tarea_id: number | undefined = undefined;

  // Opciones
  categorias = [
    { id: 6, nombre: 'Mano de obra' },
    { id: 7, nombre: 'Transporte' },
    { id: 8, nombre: 'Maquinaria' },
    { id: 9, nombre: 'Servicios públicos' },
    { id: 10, nombre: 'Mantenimiento' },
    { id: 11, nombre: 'Administración' },
    { id: 5, nombre: 'Otros' }
  ];
  
  alcances = [
    { id: 1, tipo: 'Finca' },
    { id: 2, tipo: 'Lote' },
    { id: 3, tipo: 'Cultivo' },
    { id: 4, tipo: 'General' }
  ];

  constructor(
    private gastosService: GastosOperativosService,
    private tareasService: TareasService,
    private fincasService: FincasService,
    private lotesService: LotesService,
    private cultivosService: CultivosService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadGastos();
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
  irACosechas() { this.router.navigate(['/cosechas']); }

  loadSelects() {
    this.fincasService.getFincas().subscribe(f => { this.fincas = f; this.cdr.detectChanges(); });
    this.lotesService.getLotes().subscribe(l => { this.lotes = l; this.cdr.detectChanges(); });
    this.cultivosService.getCultivos().subscribe(c => { this.cultivos = c; this.cdr.detectChanges(); });
  }

  loadTareas() {
    this.tareasService.getTareas().subscribe({
      next: (tareas) => { this.tareas = tareas; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  loadGastos() {
    this.gastosService.getGastosOperativos().subscribe({
      next: (gastos) => {
        this.gastos = gastos;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar los gastos operativos';
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

  formatearPesos(valor: number | undefined): string {
    if (valor === undefined || valor === null) return '$ 0';
    const partes = valor.toFixed(2).split('.');
    const entero = partes[0];
    const decimal = partes[1];
    const enteroFormateado = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `$ ${enteroFormateado},${decimal}`;
  }

  formatearFecha(fecha: string | undefined): string {
    if (!fecha) return 'N/A';
    const partes = fecha.split('-');
    if (partes.length === 3) {
      return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }
    return fecha;
  }

  getNombreAlcance(gasto: GastoOperativo): string {
    const alcance = this.alcances.find(a => a.id === gasto.alcance_id);
    const tipoAlcance = alcance ? alcance.tipo : 'N/A';
    
    let especifico = '';
    
    if (gasto.alcance_id === 1) {
      // Es finca
      if (gasto.finca_id) {
        const finca = this.fincas.find(f => f.id === gasto.finca_id);
        especifico = finca ? ` (${finca.nombre})` : ' (Finca específica)';
      } else {
        especifico = ' (Todas las fincas)';
      }
    } else if (gasto.alcance_id === 2) {
      // Es lote
      if (gasto.lote_id) {
        const lote = this.lotes.find(l => l.id === gasto.lote_id);
        especifico = lote ? ` (${lote.nombre})` : ' (Lote específico)';
      } else {
        especifico = ' (Todos los lotes)';
      }
    } else if (gasto.alcance_id === 3) {
      // Es cultivo
      if (gasto.cultivo_id) {
        const cultivo = this.cultivos.find(c => c.id === gasto.cultivo_id);
        especifico = cultivo ? ` (${cultivo.nombre})` : ' (Cultivo específico)';
      } else {
        especifico = ' (Todos los cultivos)';
      }
    } else if (gasto.alcance_id === 4) {
      especifico = ' (General)';
    }
    
    return tipoAlcance + especifico;
  }

  openForm(gasto?: GastoOperativo) {
    if (gasto) {
      this.editingGasto = gasto;
      this.concepto = gasto.concepto;
      this.monto = gasto.monto;
      this.fecha = gasto.fecha || '';
      this.categoria_id = gasto.categoria_id;
      this.alcance_id = gasto.alcance_id;
      this.selected_finca_id = gasto.finca_id;
      this.selected_lote_id = gasto.lote_id;
      this.selected_cultivo_id = gasto.cultivo_id;
      this.tarea_id = gasto.tarea_id;
    } else {
      this.editingGasto = null;
      this.concepto = '';
      this.monto = undefined;
      this.fecha = new Date().toISOString().split('T')[0];
      this.fecha = this.hoy;  // 👈 Automática
      this.fecha_limite = '';
      this.categoria_id = undefined;
      this.alcance_id = undefined;
      this.selected_finca_id = undefined;
      this.selected_lote_id = undefined;
      this.selected_cultivo_id = undefined;
      this.tarea_id = undefined;
    }
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingGasto = null;
    this.cdr.detectChanges();
  }

  saveGasto() {

    if (this.fecha_limite && this.fecha_limite <= this.hoy) {
      this.errorMessage = 'La fecha límite debe ser al menos un día después de hoy';
      this.cdr.detectChanges();
      return;
    }

    const gastoData: Partial<GastoOperativo> = {
      concepto: this.concepto,
      monto: this.monto,
      fecha: this.fecha || this.hoy,
      fecha_limite: this.fecha_limite || undefined,  
      categoria_id: this.categoria_id,
      alcance_id: this.alcance_id,
      finca_id: this.alcance_id === 1 ? this.selected_finca_id : undefined,
      lote_id: this.alcance_id === 2 ? this.selected_lote_id : undefined,
      cultivo_id: this.alcance_id === 3 ? this.selected_cultivo_id : undefined,
      tarea_id: this.tarea_id
    };

    const request = this.editingGasto
      ? this.gastosService.updateGastoOperativo(this.editingGasto.id, gastoData)
      : this.gastosService.createGastoOperativo(gastoData);

    request.subscribe({
      next: () => {
        this.loadGastos();
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al guardar el gasto operativo';
        this.cdr.detectChanges();
      }
    });
  }

  deleteGasto(id: number) {
    if (confirm('¿Estás seguro de eliminar este gasto operativo?')) {
      this.gastosService.deleteGastoOperativo(id).subscribe({
        next: () => this.loadGastos(),
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar el gasto operativo';
          this.cdr.detectChanges();
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}