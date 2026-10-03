import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Lote {
  id: number;
  nombre: string;
  area?: number;
  tipo_suelo?: string;
  altitud?: number;
  clima?: string;
  estado?: string;
  notas?: string;
  finca_id: number;
}

export interface Cultivo {
  id: number;
  nombre: string;
  variedad?: string;
  estado?: string;
  fecha_siembra?: string;
  lote_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class LotesService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getLotes(): Observable<Lote[]> {
    return this.http.get<Lote[]>(`${this.apiUrl}/lotes`);
  }

  getLote(id: number): Observable<Lote> {
    return this.http.get<Lote>(`${this.apiUrl}/lotes/${id}`);
  }

  getCultivosByLote(loteId: number): Observable<Cultivo[]> {
    return this.http.get<Cultivo[]>(`${this.apiUrl}/lotes/${loteId}/cultivos`);
  }

  createLote(lote: Partial<Lote>): Observable<Lote> {
    return this.http.post<Lote>(`${this.apiUrl}/lotes`, lote);
  }

  updateLote(id: number, lote: Partial<Lote>): Observable<Lote> {
    return this.http.put<Lote>(`${this.apiUrl}/lotes/${id}`, lote);
  }

  deleteLote(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/lotes/${id}`);
  }
}