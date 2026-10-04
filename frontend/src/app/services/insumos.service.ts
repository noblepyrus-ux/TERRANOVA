import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Insumo {
  id: number;
  nombre: string;
  tipo?: string;
  unidad?: string;
  stock_actual?: number;
  costo_promedio?: number;
}

@Injectable({
  providedIn: 'root'
})
export class InsumosService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getInsumos(): Observable<Insumo[]> {
    return this.http.get<Insumo[]>(`${this.apiUrl}/insumos`);
  }

  getInsumo(id: number): Observable<Insumo> {
    return this.http.get<Insumo>(`${this.apiUrl}/insumos/${id}`);
  }

  createInsumo(insumo: Partial<Insumo>): Observable<Insumo> {
    return this.http.post<Insumo>(`${this.apiUrl}/insumos`, insumo);
  }

  updateInsumo(id: number, insumo: Partial<Insumo>): Observable<Insumo> {
    return this.http.put<Insumo>(`${this.apiUrl}/insumos/${id}`, insumo);
  }

  deleteInsumo(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/insumos/${id}`);
  }
}