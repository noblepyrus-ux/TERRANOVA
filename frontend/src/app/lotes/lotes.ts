import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LotesService, Lote } from '../services/lotes.service';
import { FincasService, Finca } from '../services/fincas.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-lotes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lotes.html',
  styleUrls: ['./lotes.css']
})
export class LotesComponent implements OnInit {
  lotes: Lote[] = [];
  fincas: Finca[] = [];
  errorMessage = '';
  showForm = false;
  editingLote: Lote | null = null;
  
  nombre = '';
  area: number | undefined = undefined;
  tipo_suelo = '';
  altitud: number | undefined = undefined;
  clima = '';
  estado = '';
  notas = '';
  finca_id: number | undefined = undefined;

  constructor(
    private lotesService: LotesService,
    private fincasService: FincasService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadFincas();
    this.loadLotes();
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

  loadFincas() {
    this.fincasService.getFincas().subscribe({
      next: (fincas: Finca[]) => {
        this.fincas = fincas;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.errorMessage = 'Error al cargar las fincas';
        this.cdr.detectChanges();
      }
    });
  }

  loadLotes() {
    this.lotesService.getLotes().subscribe({
      next: (lotes: Lote[]) => {
        this.lotes = lotes;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        if (err.status === 401) {
          this.authService.logout();
        } else {
          this.errorMessage = 'Error al cargar los lotes';
          this.cdr.detectChanges();
        }
      }
    });
  }

  openForm(lote?: Lote) {
    if (lote) {
      this.editingLote = lote;
      this.nombre = lote.nombre;
      this.area = lote.area;
      this.tipo_suelo = lote.tipo_suelo || '';
      this.altitud = lote.altitud;
      this.clima = lote.clima || '';
      this.estado = lote.estado || '';
      this.notas = lote.notas || '';
      this.finca_id = lote.finca_id;
    } else {
      this.editingLote = null;
      this.nombre = '';
      this.area = undefined;
      this.tipo_suelo = '';
      this.altitud = undefined;
      this.clima = '';
      this.estado = '';
      this.notas = '';
      this.finca_id = this.fincas.length > 0 ? this.fincas[0].id : undefined;
    }
    
    this.showForm = true;
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.editingLote = null;
    this.nombre = '';
    this.area = undefined;
    this.tipo_suelo = '';
    this.altitud = undefined;
    this.clima = '';
    this.estado = '';
    this.notas = '';
    this.finca_id = undefined;
    this.cdr.detectChanges();
  }

  saveLote() {
    const loteData: Partial<Lote> = {
      nombre: this.nombre,
      area: this.area,
      tipo_suelo: this.tipo_suelo || undefined,
      altitud: this.altitud,
      clima: this.clima || undefined,
      estado: this.estado || undefined,
      notas: this.notas || undefined,
      finca_id: this.finca_id
    };

    if (this.editingLote) {
      this.lotesService.updateLote(this.editingLote.id, loteData).subscribe({
        next: () => {
          this.loadLotes();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al actualizar el lote';
          this.cdr.detectChanges();
        }
      });
    } else {
      this.lotesService.createLote(loteData).subscribe({
        next: () => {
          this.loadLotes();
          this.closeForm();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al crear el lote';
          this.cdr.detectChanges();
        }
      });
    }
  }

  deleteLote(id: number) {
    if (confirm('¿Estás seguro de eliminar este lote?')) {
      this.lotesService.deleteLote(id).subscribe({
        next: () => {
          this.loadLotes();
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar el lote';
          this.cdr.detectChanges();
        }
      });
    }
  }

  getNombreFinca(fincaId: number): string {
    const finca = this.fincas.find(f => f.id === fincaId);
    return finca ? finca.nombre : 'N/A';
  }

  verDetalle(id: number) {
    this.router.navigate(['/lotes', id]);
  }

  logout() {
    this.authService.logout();
  }
}