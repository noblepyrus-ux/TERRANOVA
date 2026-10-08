import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http'; // ✅ AGREGADO
import { DashboardService, DashboardData } from '../services/dashboard.service';
import { AuthService } from '../services/auth.service';
import { Chart, registerables } from 'chart.js';
import { FincasService, Finca } from '../services/fincas.service';
import { FormsModule } from '@angular/forms';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
})
export class DashboardComponent implements OnInit, AfterViewInit {
  dashboard: DashboardData | null = null;
  errorMessage = '';
  
  @ViewChild('gastosChart') gastosChartRef!: ElementRef;
  @ViewChild('cosechasChart') cosechasChartRef!: ElementRef;
  
  private gastosChart: Chart | null = null;
  private cosechasChart: Chart | null = null;

  // ✅ VARIABLES PARA EL MODAL DE COLABORADORES
  mostrarFormColaborador = false;
  nuevoUsuario = '';
  nuevaPassword = '';
  fincasSeleccionadas: number[] = [];
  mensajeColaborador = '';
  exitoColaborador = false;
  idsFincasInput = '';
  fincas: Finca[] = [];

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private http: HttpClient,
    private fincasService: FincasService  
  ) {}

  ngOnInit() {
    this.loadDashboard();
    this.cargarFincas();
  }

  ngAfterViewInit() {
    // Los gráficos se crean después de que el HTML esté renderizado
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
  cargarFincas() {
    this.fincasService.getFincas().subscribe({
      next: (fincas) => {
        this.fincas = fincas;
      },
      error: (err) => {
        console.error('Error al cargar fincas', err);
      }
    });
  }
  
  loadDashboard() {
    this.dashboardService.getDashboard().subscribe({
      next: (data) => {
        this.dashboard = data;
        this.cdr.detectChanges();
        setTimeout(() => this.crearGraficos(), 100);
      },
      error: (err: any) => {
        if (err.status === 401) this.authService.logout();
        else {
          this.errorMessage = 'Error al cargar el dashboard';
          this.cdr.detectChanges();
        }
      }
    });
  }

  crearGraficos() {
    if (!this.dashboard) return;

    if (this.gastosChart) this.gastosChart.destroy();
    if (this.cosechasChart) this.cosechasChart.destroy();

    const coloresGastos = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA'];
    
    if (this.gastosChartRef?.nativeElement && this.dashboard.gastos_por_categoria.length > 0) {
      const ctx = this.gastosChartRef.nativeElement.getContext('2d');
      this.gastosChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.dashboard.gastos_por_categoria.map(g => g.categoria),
          datasets: [{
            data: this.dashboard.gastos_por_categoria.map(g => g.total),
            backgroundColor: coloresGastos,
            borderWidth: 3,
            borderColor: '#ffffff',
            hoverOffset: 15,
            hoverBorderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: { padding: 20, usePointStyle: true, pointStyle: 'circle', font: { size: 13, family: "'Segoe UI', sans-serif" }, color: '#555' }
            },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              cornerRadius: 8,
              callbacks: {
                label: function(context: any) {
                  const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                  const porcentaje = ((context.parsed / total) * 100).toFixed(1);
                  const valor = context.parsed.toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 });
                  return ` ${context.label}: ${valor} (${porcentaje}%)`;
                }
              }
            }
          },
          animation: { animateRotate: true, animateScale: true, duration: 1200, easing: 'easeOutQuart' }
        }
      });
    }

    if (this.cosechasChartRef?.nativeElement && this.dashboard.cosechas_por_cultivo.length > 0) {
      const ctx = this.cosechasChartRef.nativeElement.getContext('2d');
      const coloresCosechas = ['#4CAF50', '#2196F3', '#FFC107', '#FF9800', '#9C27B0', '#E91E63', '#00BCD4', '#8BC34A'];
      const backgroundColors = this.dashboard.cosechas_por_cultivo.map((_, index) => coloresCosechas[index % coloresCosechas.length]);
      
      this.cosechasChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.dashboard.cosechas_por_cultivo.map(c => c.cultivo),
          datasets: [{
            label: 'Cantidad cosechada',
            data: this.dashboard.cosechas_por_cultivo.map(c => c.total),
            backgroundColor: backgroundColors,
            borderRadius: 8,
            borderSkipped: false,
            barPercentage: 0.6,
            categoryPercentage: 0.7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(0,0,0,0.8)',
              padding: 12,
              cornerRadius: 8,
              callbacks: {
                label: function(context: any) {
                  const valor = context.parsed.y ?? 0;
                  return ` ${valor.toLocaleString('es-CO')} unidades`;
                }
              }
            }
          },
          scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 12 }, color: '#888', padding: 10 } },
            x: { grid: { display: false }, ticks: { font: { size: 13, weight: 'bold' }, color: '#555', padding: 10 } }
          },
          animation: { duration: 1000, easing: 'easeOutBounce' }
        }
      });
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
    if (partes.length === 3) return `${partes[2]}/${partes[1]}/${partes[0]}`;
    return fecha;
  }

  logout() {
    this.authService.logout();
  }

  // ==========================================
  // ✅ MÉTODOS PARA GESTIÓN DE COLABORADORES
  // ==========================================
  toggleFinca(fincaId: number, event: any) {
    if (event.target.checked) {
      this.fincasSeleccionadas.push(fincaId);
    } else {
      const index = this.fincasSeleccionadas.indexOf(fincaId);
      if (index > -1) this.fincasSeleccionadas.splice(index, 1);
    }
  }

  crearColaborador() {
    if (!this.nuevoUsuario || !this.nuevaPassword) {
      this.mensajeColaborador = 'Usuario y contraseña son obligatorios';
      this.exitoColaborador = false;
      return;
    }

    // Convertir el string "1, 2" en un array de números [1, 2]
    const fincaIdsArray = this.idsFincasInput.split(',')
      .map(id => parseInt(id.trim()))
      .filter(id => !isNaN(id));

    if (fincaIdsArray.length === 0) {
      this.mensajeColaborador = 'Debe ingresar al menos un ID de finca válido';
      this.exitoColaborador = false;
      return;
    }

    const data = {
      usuario: this.nuevoUsuario,
      password: this.nuevaPassword,
      finca_ids: fincaIdsArray
    };

    const token = localStorage.getItem('token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    this.http.post('http://127.0.0.1:8000/admin/crear-colaborador', data, { headers }).subscribe({
      next: (response: any) => {
        this.mensajeColaborador = response.message || 'Colaborador creado exitosamente';
        this.exitoColaborador = true;
        this.nuevoUsuario = '';
        this.nuevaPassword = '';
        this.idsFincasInput = '';
        setTimeout(() => this.cerrarFormColaborador(), 2500);
      },
      error: (err) => {
        this.mensajeColaborador = err.error?.detail || 'Error al crear colaborador';
        this.exitoColaborador = false;
      }
    });
  }

  cerrarFormColaborador() {
    this.mostrarFormColaborador = false;
    this.mensajeColaborador = '';
    this.nuevoUsuario = '';
    this.nuevaPassword = '';
    this.fincasSeleccionadas = [];
  }
}