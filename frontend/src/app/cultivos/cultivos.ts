import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CultivosService, Cultivo } from '../services/cultivos.service';
import { LotesService, Lote } from '../services/lotes.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-cultivos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cultivos.html',
  styleUrls: ['./cultivos.css']
})
export class CultivosComponent implements OnInit {
  cultivos: Cultivo[] = [];
  lotes: Lote[] = [];
  errorMessage = '';
  showForm = false;
  editingCultivo: Cultivo | null = null;
  
  // Datos del formulario
  nombre = '';
  variedad = '';
  estado = '';
  fecha_siembra = '';
  lote_id: number | undefined = undefined;

  constructor(
    private cultivosService: CultivosService,
    private lotesService: LotesService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadLotes();
    this.loadCultivos();
  }

  // ✅ MÉTODOS DE NAVEGACIÓN
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
  irACompras() { this.router.navigate(['/compras']); }
  irAGastosOperativos() { this.router.navigate(['/gastos-operativos']); }
  irACosechas() { this.router.navigate(['/cosechas']); }

  loadLotes() {
    this.lotesService.getLotes().subscribe({
      next: (lotes: Lote[]) => {
        this.lotes = lotes;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.errorMessage = 'Error al cargar los lotes';
        this.cdr.detectChanges();
      }
    });
  }

  loadCultivos() {
    this.cultivosService.getCultivos().subscribe({
      next: (cultivos: Cultivo[]) => {
        this.cultivos = cultivos;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) {
          this.authService.logout();
        } else {
          this.errorMessage = 'Error al cargar los cultivos';
          this.cdr.detectChanges();
        }
      }
    });
  }

  openForm(cultivo?: Cultivo) {
    if (cultivo) {
      this.editingCultivo = cultivo;
      this.nombre = cultivo.nombre;
      this.variedad = cultivo.variedad || '';
      this.estado = cultivo.estado || '';
      this.fecha_siembra = cultivo.fecha_siembra || '';
      this.lote_id = cultivo.lote_id;
    } else {
      this.editingCultivo = null;
      this.nombre = '';
      this.variedad = '';
      this.estado = '';
      this.fecha_siembra = '';
      this.lote_id = this.lotes.length > 0 ? this.lotes[0].id : undefined;
    }
    
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingCultivo = null;
    this.nombre = '';
    this.variedad = '';
    this.estado = '';
    this.fecha_siembra = '';
    this.lote_id = undefined;
    this.cdr.detectChanges();
  }

  saveCultivo() {
    const cultivoData: Partial<Cultivo> = {
      nombre: this.nombre,
      variedad: this.variedad || undefined,
      estado: this.estado || undefined,
      fecha_siembra: this.fecha_siembra || undefined,
      lote_id: this.lote_id
    };

    if (this.editingCultivo) {
      this.cultivosService.updateCultivo(this.editingCultivo.id, cultivoData).subscribe({
        next: () => {
          this.loadCultivos();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al actualizar el cultivo';
          this.cdr.detectChanges();
        }
      });
    } else {
      this.cultivosService.createCultivo(cultivoData).subscribe({
        next: () => {
          this.loadCultivos();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al crear el cultivo';
          this.cdr.detectChanges();
        }
      });
    }
  }

  deleteCultivo(id: number) {
    if (confirm('¿Estás seguro de eliminar este cultivo?')) {
      this.cultivosService.deleteCultivo(id).subscribe({
        next: () => {
          this.loadCultivos();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar el cultivo';
          this.cdr.detectChanges();
        }
      });
    }
  }

  getNombreLote(loteId: number): string {
    const lote = this.lotes.find(l => l.id === loteId);
    return lote ? lote.nombre : 'N/A';
  }

  logout() {
    this.authService.logout();
  }
}