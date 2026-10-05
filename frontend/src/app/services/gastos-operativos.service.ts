import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GastoOperativo {
  id: number;
  concepto: string;
  monto: number;
  fecha?: string;
  fecha_limite?: string; 
  categoria_id?: number;
  alcance_id?: number;
  finca_id?: number;
  lote_id?: number;
  cultivo_id?: number;
  tarea_id?: number;
  nombre_categoria?: string;
  nombre_tarea?: string;
}

@Injectable({
  providedIn: 'root'
})
export class GastosOperativosService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getGastosOperativos(): Observable<GastoOperativo[]> {
    return this.http.get<GastoOperativo[]>(`${this.apiUrl}/gastos-operativos`);
  }

  getGastoOperativo(id: number): Observable<GastoOperativo> {
    return this.http.get<GastoOperativo>(`${this.apiUrl}/gastos-operativos/${id}`);
  }

  createGastoOperativo(gasto: Partial<GastoOperativo>): Observable<GastoOperativo> {
    return this.http.post<GastoOperativo>(`${this.apiUrl}/gastos-operativos`, gasto);
  }

  updateGastoOperativo(id: number, gasto: Partial<GastoOperativo>): Observable<GastoOperativo> {
    return this.http.put<GastoOperativo>(`${this.apiUrl}/gastos-operativos/${id}`, gasto);
  }

  deleteGastoOperativo(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/gastos-operativos/${id}`);
  }
}