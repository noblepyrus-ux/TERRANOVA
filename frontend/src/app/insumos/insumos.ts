import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { InsumosService, Insumo } from '../services/insumos.service';
import { AuthService } from '../services/auth.service';
import { FormatoPesosPipe } from '../pipes/formato-pesos.pipe';

@Component({
  selector: 'app-insumos',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './insumos.html',
  styleUrls: ['./insumos.css']
})
export class InsumosComponent implements OnInit {
  insumos: Insumo[] = [];
  errorMessage = '';
  showForm = false;
  editingInsumo: Insumo | null = null;
  
  nombre = '';
  tipo = '';
  unidad = '';
  stock_actual: number | undefined = undefined;
  
  // Variables para manejar el costo con formato
  costo_input = '';       // Lo que ve el usuario en el input
  costo_real: number | undefined = undefined; // El valor numérico real que se guarda

  tipos = ['Fertilizante', 'Pesticida', 'Semilla', 'Herramienta', 'Otro'];
  unidades = ['kg', 'g', 'L', 'mL', 'unidades', 'sacos', 'litros'];

  constructor(
    private insumosService: InsumosService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
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

  loadInsumos() {
    this.insumosService.getInsumos().subscribe({
      next: (insumos: Insumo[]) => {
        this.insumos = insumos;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar los insumos';
          this.cdr.detectChanges();
        }
      }
    });
  }

  // Formatea el valor real a formato pesos
  updateCostoInput() {
    if (this.costo_real !== undefined && this.costo_real !== null) {
      this.costo_input = new Intl.NumberFormat('es-CO', {
        style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 2
      }).format(this.costo_real);
    } else {
      this.costo_input = '';
    }
  }

  openForm(insumo?: Insumo) {
    if (insumo) {
      this.editingInsumo = insumo;
      this.nombre = insumo.nombre;
      this.tipo = insumo.tipo || '';
      this.unidad = insumo.unidad || '';
      this.stock_actual = insumo.stock_actual;
      this.costo_real = insumo.costo_promedio;
      this.updateCostoInput(); // 👈 Formatear al abrir
    } else {
      this.editingInsumo = null;
      this.nombre = '';
      this.tipo = '';
      this.unidad = '';
      this.stock_actual = 0;
      this.costo_real = undefined;
      this.costo_input = '';
    }
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingInsumo = null;
    this.cdr.detectChanges();
  }

  // Cuando el usuario hace clic en el input, mostramos el número puro para editar fácil
  onCostoFocus() {
    this.costo_input = this.costo_real?.toString() || '';
  }

  // Cuando el usuario sale del input, limpiamos y formateamos
  onCostoBlur() {
    const limpio = this.costo_input.replace(/\./g, '').replace(',', '.');
    this.costo_real = limpio && !isNaN(parseFloat(limpio)) ? parseFloat(limpio) : undefined;
    this.updateCostoInput();
  }

  saveInsumo() {
    const insumoData: Partial<Insumo> = {
      nombre: this.nombre,
      tipo: this.tipo || undefined,
      unidad: this.unidad || undefined,
      stock_actual: this.stock_actual,
      costo_promedio: this.costo_real // 👈 Guardamos el valor numérico real
    };

    const request = this.editingInsumo
      ? this.insumosService.updateInsumo(this.editingInsumo.id, insumoData)
      : this.insumosService.createInsumo(insumoData);

    request.subscribe({
      next: () => {
        this.loadInsumos();
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al guardar el insumo';
        this.cdr.detectChanges();
      }
    });
  }

  deleteInsumo(id: number) {
    if (confirm('¿Estás seguro de eliminar este insumo?')) {
      this.insumosService.deleteInsumo(id).subscribe({
        next: () => this.loadInsumos(),
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar el insumo';
          this.cdr.detectChanges();
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}