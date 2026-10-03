import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { LotesService, Lote, Cultivo } from '../../services/lotes.service';
import { CultivosService } from '../../services/cultivos.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-lote-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lote-detalle.html',
  styleUrls: ['./lote-detalle.css']
})
export class LoteDetalleComponent implements OnInit {
  lote: Lote | null = null;
  cultivos: Cultivo[] = [];
  errorMessage = '';
  showForm = false;
  
  nombre = '';
  variedad = '';
  estado = '';
  fecha_siembra = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private lotesService: LotesService,
    private cultivosService: CultivosService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const loteId = Number(this.route.snapshot.paramMap.get('id'));
    if (loteId) {
      this.loadLote(loteId);
      this.loadCultivos(loteId);
    }
  }

  loadLote(id: number) {
    this.lotesService.getLote(id).subscribe({
      next: (lote) => {
        this.lote = lote;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error al cargar el lote';
        this.cdr.detectChanges();
      }
    });
  }

  loadCultivos(loteId: number) {
    this.lotesService.getCultivosByLote(loteId).subscribe({
      next: (cultivos) => {
        this.cultivos = cultivos;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error al cargar los cultivos';
        this.cdr.detectChanges();
      }
    });
  }

  openForm() {
    this.showForm = true;
    this.nombre = '';
    this.variedad = '';
    this.estado = '';
    this.fecha_siembra = '';
    this.cdr.detectChanges();
  }

  closeForm() {
    this.showForm = false;
    this.cdr.detectChanges();
  }

  saveCultivo() {
    if (!this.lote) return;

    const cultivoData = {
      nombre: this.nombre,
      variedad: this.variedad || undefined,
      estado: this.estado || undefined,
      fecha_siembra: this.fecha_siembra || undefined,
      lote_id: this.lote.id
    };

    this.cultivosService.createCultivo(cultivoData).subscribe({
      next: () => {
        this.loadCultivos(this.lote!.id);
        this.closeForm();
      },
      error: (err: any) => {
        this.errorMessage = err.error?.detail || 'Error al crear el cultivo';
        this.cdr.detectChanges();
      }
    });
  }

  deleteCultivo(id: number) {
    if (confirm('¿Estás seguro de eliminar este cultivo?')) {
      this.cultivosService.deleteCultivo(id).subscribe({
        next: () => {
          if (this.lote) this.loadCultivos(this.lote.id);
        },
        error: (err: any) => {
          this.errorMessage = err.error?.detail || 'Error al eliminar el cultivo';
          this.cdr.detectChanges();
        }
      });
    }
  }

  goBack() {
    this.router.navigate(['/lotes']);
  }

  logout() {
    this.authService.logout();
  }
}