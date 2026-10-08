import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

// ✅ INTERFAZ ACTUALIZADA: Se eliminó cuenta_id y se agregó propietarios
export interface Finca {
  id: number;
  nombre: string;
  ubicacion: string | null;
  area_total: number | null;
  propietarios?: {
    cuenta_id: number;
    rol_en_finca: string;
  }[];
}

@Injectable({
  providedIn: 'root'
})
export class FincasService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  // Método auxiliar para obtener el token
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  getFincas(): Observable<Finca[]> {
    return this.http.get<Finca[]>(`${this.apiUrl}/fincas`, { headers: this.getHeaders() });
  }

  getFinca(id: number): Observable<Finca> {
    return this.http.get<Finca>(`${this.apiUrl}/fincas/${id}`, { headers: this.getHeaders() });
  }

  createFinca(finca: Partial<Finca>): Observable<Finca> {
    return this.http.post<Finca>(`${this.apiUrl}/fincas`, finca, { headers: this.getHeaders() });
  }

  updateFinca(id: number, finca: Partial<Finca>): Observable<Finca> {
    return this.http.put<Finca>(`${this.apiUrl}/fincas/${id}`, finca, { headers: this.getHeaders() });
  }

  deleteFinca(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/fincas/${id}`, { headers: this.getHeaders() });
  }
}