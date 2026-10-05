import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FincasService, Finca } from '../services/fincas.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-fincas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './fincas.html',
  styleUrls: ['./fincas.css']
})
export class FincasComponent implements OnInit {
  fincas: Finca[] = [];
  errorMessage = '';
  showForm = false;
  editingFinca: Finca | null = null;
  
  nombre = '';
  ubicacion = '';
  area_total: number | null = null;

  constructor(
    private fincasService: FincasService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadFincas();
  }

  // ✅ MÉTODOS DE NAVEGACIÓN (agregar estos 3)
  irAFincas() {
    this.router.navigate(['/fincas']);
  }

  irALotes() {
    this.router.navigate(['/lotes']);
  }

  irACultivos() {
    this.router.navigate(['/cultivos']);
  }

  irATareas() {
    this.router.navigate(['/tareas']);
  }

  irAInsumos() { this.router.navigate(['/insumos']); }
  irAGastosOperativos() { this.router.navigate(['/gastos-operativos']); }
  irACompras() { this.router.navigate(['/compras']); }

  loadFincas() {
    this.fincasService.getFincas().subscribe({
      next: (fincas: Finca[]) => {
        this.fincas = fincas;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) {
          this.authService.logout();
        } else {
          this.errorMessage = 'Error al cargar las fincas';
          this.cdr.detectChanges();
        }
      }
    });
  }

  openForm(finca?: Finca) {
    if (finca) {
      this.editingFinca = finca;
      this.nombre = finca.nombre;
      this.ubicacion = finca.ubicacion || '';
      this.area_total = finca.area_total;
    } else {
      this.editingFinca = null;
      this.nombre = '';
      this.ubicacion = '';
      this.area_total = null;
    }
    
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingFinca = null;
    this.nombre = '';
    this.ubicacion = '';
    this.area_total = null;
    this.cdr.detectChanges();
  }

  saveFinca() {
    const fincaData = {
      nombre: this.nombre,
      ubicacion: this.ubicacion,
      area_total: this.area_total
    };

    if (this.editingFinca) {
      this.fincasService.updateFinca(this.editingFinca.id, fincaData).subscribe({
        next: () => {
          this.loadFincas();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = 'Error al actualizar la finca';
          this.cdr.detectChanges();
        }
      });
    } else {
      this.fincasService.createFinca(fincaData).subscribe({
        next: () => {
          this.loadFincas();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = 'Error al crear la finca';
          this.cdr.detectChanges();
        }
      });
    }
  }

  deleteFinca(id: number) {
    if (confirm('¿Estás seguro de eliminar esta finca?')) {
      this.fincasService.deleteFinca(id).subscribe({
        next: () => {
          this.loadFincas();
        },
        error: (err: any) => {
          this.errorMessage = 'Error al eliminar la finca';
          this.cdr.detectChanges();
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}