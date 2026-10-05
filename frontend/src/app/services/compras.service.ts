import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Compra {
  id: number;
  cantidad: number;
  costo_unitario: number;
  costo_total: number;
  fecha?: string;
  proveedor?: string;
  nota?: string;
  insumo_id: number;
  nombre_insumo?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ComprasService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getCompras(): Observable<Compra[]> {
    return this.http.get<Compra[]>(`${this.apiUrl}/compras`);
  }

  getCompra(id: number): Observable<Compra> {
    return this.http.get<Compra>(`${this.apiUrl}/compras/${id}`);
  }

  createCompra(compra: any): Observable<Compra> {
    return this.http.post<Compra>(`${this.apiUrl}/compras`, compra);
  }

  updateCompra(id: number, compra: Partial<Compra>): Observable<Compra> {
    return this.http.put<Compra>(`${this.apiUrl}/compras/${id}`, compra);
  }

  deleteCompra(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/compras/${id}`);
  }
}