import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Tarea {
  id: number;
  nombre: string;
  descripcion?: string;
  fecha?: string;
  estado?: string;
  tipo?: string;
  alcance_id: number;
  insumo_id?: number;
  cantidad_usada?: number;
  lote_id?: number;
  cultivo_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class TareasService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  getTareas(): Observable<Tarea[]> {
    return this.http.get<Tarea[]>(`${this.apiUrl}/tareas`);
  }

  getTarea(id: number): Observable<Tarea> {
    return this.http.get<Tarea>(`${this.apiUrl}/tareas/${id}`);
  }

  createTarea(tarea: Partial<Tarea>): Observable<Tarea> {
    return this.http.post<Tarea>(`${this.apiUrl}/tareas`, tarea);
  }

  updateTarea(id: number, tarea: Partial<Tarea>): Observable<Tarea> {
    return this.http.put<Tarea>(`${this.apiUrl}/tareas/${id}`, tarea);
  }

  deleteTarea(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/tareas/${id}`);
  }
}