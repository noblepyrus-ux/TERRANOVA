import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
export class CultivosService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getCultivos(): Observable<Cultivo[]> {
    return this.http.get<Cultivo[]>(`${this.apiUrl}/cultivos`);
  }

  getCultivo(id: number): Observable<Cultivo> {
    return this.http.get<Cultivo>(`${this.apiUrl}/cultivos/${id}`);
  }

  createCultivo(cultivo: Partial<Cultivo>): Observable<Cultivo> {
    return this.http.post<Cultivo>(`${this.apiUrl}/cultivos`, cultivo);
  }

  updateCultivo(id: number, cultivo: Partial<Cultivo>): Observable<Cultivo> {
    return this.http.put<Cultivo>(`${this.apiUrl}/cultivos/${id}`, cultivo);
  }

  deleteCultivo(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/cultivos/${id}`);
  }
}