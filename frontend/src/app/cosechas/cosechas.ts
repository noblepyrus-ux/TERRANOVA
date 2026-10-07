import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CosechasService, Cosecha } from '../services/cosechas.service';
import { CultivosService, Cultivo } from '../services/cultivos.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-cosechas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cosechas.html',
  styleUrls: ['./cosechas.css']
})
export class CosechasComponent implements OnInit {
  cosechas: Cosecha[] = [];
  cultivos: Cultivo[] = [];
  errorMessage = '';
  showForm = false;
  editingCosecha: Cosecha | null = null;
  
  // Datos del formulario
  fecha = '';
  cantidad: number | undefined = undefined;
  unidad = '';
  notas = '';
  cultivo_id: number | undefined = undefined;

  // Opciones de unidad
  unidades = ['kg', 'g', 'toneladas', 'quintales', 'sacos', 'litros', 'unidades'];

  constructor(
    private cosechasService: CosechasService,
    private cultivosService: CultivosService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadCosechas();
    this.loadCultivos();
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

  loadCultivos() {
    this.cultivosService.getCultivos().subscribe({
      next: (cultivos) => { this.cultivos = cultivos; this.cdr.detectChanges(); },
      error: () => {}
    });
  }

  loadCosechas() {
    this.cosechasService.getCosechas().subscribe({
      next: (cosechas) => {
        this.cosechas = cosechas;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar las cosechas';
          this.cdr.detectChanges();
        }
      }
    });
  }

  formatearFecha(fecha: string | undefined): string {
    if (!fecha) return 'N/A';
    const partes = fecha.split('-');
    if (partes.length === 3) {
      return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }
    return fecha;
  }

  openForm(cosecha?: Cosecha) {
    if (cosecha) {
      this.editingCosecha = cosecha;
      this.fecha = cosecha.fecha || '';
      this.cantidad = cosecha.cantidad;
      this.unidad = cosecha.unidad || '';
      this.notas = cosecha.notas || '';
      this.cultivo_id = cosecha.cultivo_id;
    } else {
      this.editingCosecha = null;
      this.fecha = new Date().toISOString().split('T')[0];
      this.cantidad = undefined;
      this.unidad = '';
      this.notas = '';
      this.cultivo_id = undefined;
    }
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingCosecha = null;
    this.cdr.detectChanges();
  }

  saveCosecha() {
    const cosechaData: Partial<Cosecha> = {
      fecha: this.fecha || undefined,
      cantidad: this.cantidad,
      unidad: this.unidad || undefined,
      notas: this.notas || undefined,
      cultivo_id: this.cultivo_id
    };

    const request = this.editingCosecha
      ? this.cosechasService.updateCosecha(this.editingCosecha.id, cosechaData)
      : this.cosechasService.createCosecha(cosechaData);

    request.subscribe({
      next: () => {
        this.loadCosechas();
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al guardar la cosecha';
        this.cdr.detectChanges();
      }
    });
  }

  deleteCosecha(id: number) {
    if (confirm('¿Estás seguro de eliminar esta cosecha?')) {
      this.cosechasService.deleteCosecha(id).subscribe({
        next: () => this.loadCosechas(),
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar la cosecha';
          this.cdr.detectChanges();
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}