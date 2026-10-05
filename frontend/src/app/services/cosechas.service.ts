import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Cosecha {
  id: number;
  fecha?: string;
  cantidad: number;
  unidad?: string;
  notas?: string;
  cultivo_id: number;
  nombre_cultivo?: string;
  nombre_lote?: string;
  nombre_finca?: string;
}

@Injectable({
  providedIn: 'root'
})
export class CosechasService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getCosechas(): Observable<Cosecha[]> {
    return this.http.get<Cosecha[]>(`${this.apiUrl}/cosechas`);
  }

  getCosecha(id: number): Observable<Cosecha> {
    return this.http.get<Cosecha>(`${this.apiUrl}/cosechas/${id}`);
  }

  createCosecha(cosecha: Partial<Cosecha>): Observable<Cosecha> {
    return this.http.post<Cosecha>(`${this.apiUrl}/cosechas`, cosecha);
  }

  updateCosecha(id: number, cosecha: Partial<Cosecha>): Observable<Cosecha> {
    return this.http.put<Cosecha>(`${this.apiUrl}/cosechas/${id}`, cosecha);
  }

  deleteCosecha(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/cosechas/${id}`);
  }
}