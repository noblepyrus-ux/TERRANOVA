import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ComprasService, Compra } from '../services/compras.service';
import { InsumosService, Insumo } from '../services/insumos.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-compras',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './compras.html',
  styleUrls: ['./compras.css']
})
export class ComprasComponent implements OnInit {
  compras: Compra[] = [];
  insumos: Insumo[] = [];
  errorMessage = '';
  showForm = false;
  editingCompra: Compra | null = null;
  
  // Datos del formulario
  cantidad: number | undefined = undefined;
  costo_unitario: number | undefined = undefined;
  costo_total: number | undefined = undefined;
  fecha = '';
  proveedor = '';
  nota = '';
  insumo_id: number | undefined = undefined;
  
  // Para crear insumo nuevo
  es_nuevo_insumo = false;
  nuevo_insumo_nombre = '';
  nuevo_insumo_tipo = '';
  nuevo_insumo_unidad = '';

  // Opciones
  tipos_insumo = ['Fertilizante', 'Pesticida', 'Semilla', 'Herramienta', 'Otro'];
  unidades = ['kg', 'g', 'L', 'mL', 'unidades', 'sacos', 'litros'];

  constructor(
    private comprasService: ComprasService,
    private insumosService: InsumosService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadCompras();
    this.loadInsumos();
  }

  irAFincas() { this.router.navigate(['/fincas']); }
  irALotes() { this.router.navigate(['/lotes']); }
  irACultivos() { this.router.navigate(['/cultivos']); }
  irATareas() { this.router.navigate(['/tareas']); }
  irAInsumos() { this.router.navigate(['/insumos']); }
  irACompras() { this.router.navigate(['/compras']); }
  irAGastosOperativos() { this.router.navigate(['/gastos-operativos']); }
  irACosechas() { this.router.navigate(['/cosechas']); }
  irADashboard() { this.router.navigate(['/dashboard']); }

  loadInsumos() {
    this.insumosService.getInsumos().subscribe({
      next: (insumos) => { this.insumos = insumos; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  loadCompras() {
    this.comprasService.getCompras().subscribe({
      next: (compras) => {
        this.compras = compras;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar las compras';
          this.cdr.detectChanges();
        }
      }
    });
  }

  onInsumoChange(value: any) {
    if (value === -1 || value === '-1') {
      this.es_nuevo_insumo = true;
      this.insumo_id = -1;
    } else {
      this.es_nuevo_insumo = false;
      this.insumo_id = value ? Number(value) : undefined;
    }
    this.cdr.detectChanges();
  }

  calcularCostoTotal() {
    if (this.cantidad && this.costo_unitario) {
      this.costo_total = this.cantidad * this.costo_unitario;
    } else {
      this.costo_total = undefined;
    }
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

  openForm(compra?: Compra) {
    if (compra) {
      this.editingCompra = compra;
      this.cantidad = compra.cantidad;
      this.costo_unitario = compra.costo_unitario;
      this.costo_total = compra.costo_total;
      this.fecha = compra.fecha || '';
      this.proveedor = compra.proveedor || '';
      this.nota = compra.nota || '';
      this.insumo_id = compra.insumo_id;
      this.es_nuevo_insumo = false;
    } else {
      this.editingCompra = null;
      this.cantidad = undefined;
      this.costo_unitario = undefined;
      this.costo_total = undefined;
      this.fecha = new Date().toISOString().split('T')[0];
      this.proveedor = '';
      this.nota = '';
      this.insumo_id = undefined;
      this.es_nuevo_insumo = false;
      this.nuevo_insumo_nombre = '';
      this.nuevo_insumo_tipo = '';
      this.nuevo_insumo_unidad = '';
    }
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingCompra = null;
    this.cdr.detectChanges();
  }

  saveCompra() {
    const compraData: any = {
      cantidad: this.cantidad,
      costo_unitario: this.costo_unitario,
      costo_total: this.costo_total,
      fecha: this.fecha || undefined,
      proveedor: this.proveedor || undefined,
      nota: this.nota || undefined,
      insumo_id: this.insumo_id
    };

    if (this.es_nuevo_insumo) {
      compraData.nuevo_insumo_nombre = this.nuevo_insumo_nombre;
      compraData.nuevo_insumo_tipo = this.nuevo_insumo_tipo || undefined;
      compraData.nuevo_insumo_unidad = this.nuevo_insumo_unidad || undefined;
    }

    const request = this.editingCompra
      ? this.comprasService.updateCompra(this.editingCompra.id, compraData)
      : this.comprasService.createCompra(compraData);

    request.subscribe({
      next: () => {
        this.loadCompras();
        this.loadInsumos();
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al guardar la compra';
        this.cdr.detectChanges();
      }
    });
  }

  deleteCompra(id: number) {
    if (confirm('¿Estás seguro de eliminar esta compra?')) {
      this.comprasService.deleteCompra(id).subscribe({
        next: () => this.loadCompras(),
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar la compra';
          this.cdr.detectChanges();
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}