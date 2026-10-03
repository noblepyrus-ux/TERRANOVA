import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface Finca {
  id: number;
  nombre: string;
  ubicacion: string | null;
  area_total: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class Api {
  private http = inject(HttpClient);
  private baseUrl = 'http://127.0.0.1:8000';

  getFincas(): Observable<Finca[]> {
    return this.http.get<Finca[]>(`${this.baseUrl}/fincas`);
  }

  crearFinca(finca: any): Observable<Finca> {
    return this.http.post<Finca>(`${this.baseUrl}/fincas`, finca);
  }

  eliminarFinca(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/fincas/${id}`);
  }
}