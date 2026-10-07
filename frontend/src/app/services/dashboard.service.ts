import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardData {
  kpis: {
    total_fincas: number;
    total_lotes: number;
    total_cultivos: number;
    tareas_pendientes: number;
    tareas_vencidas: number;
    insumos_stock_bajo: number;
    total_invertido: number;
  };
  ultimas_tareas: Array<{
    id: number;
    nombre: string;
    estado: string;
    fecha_limite?: string;
    tipo?: string;
  }>;
  insumos_stock_bajo: Array<{
    id: number;
    nombre: string;
    stock_actual: number;
    unidad: string;
  }>;
  ultimas_cosechas: Array<{
    id: number;
    cultivo: string;
    cantidad: number;
    unidad: string;
    fecha?: string;
  }>;
  gastos_por_categoria: Array<{
    categoria: string;
    total: number;
  }>;
  cosechas_por_cultivo: Array<{
    cultivo: string;
    total: number;
  }>;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getDashboard(): Observable<DashboardData> {
    return this.http.get<DashboardData>(`${this.apiUrl}/dashboard`);
  }
}