import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Finca {
  id: number;
  nombre: string;
  ubicacion: string | null;
  area_total: number | null;
  cuenta_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class FincasService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getFincas(): Observable<Finca[]> {
    return this.http.get<Finca[]>(`${this.apiUrl}/fincas`);
  }

  getFinca(id: number): Observable<Finca> {
    return this.http.get<Finca>(`${this.apiUrl}/fincas/${id}`);
  }

  createFinca(finca: Partial<Finca>): Observable<Finca> {
    return this.http.post<Finca>(`${this.apiUrl}/fincas`, finca);
  }

  updateFinca(id: number, finca: Partial<Finca>): Observable<Finca> {
    return this.http.put<Finca>(`${this.apiUrl}/fincas/${id}`, finca);
  }

  deleteFinca(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/fincas/${id}`);
  }
}