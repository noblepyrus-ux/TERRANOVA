import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { LoginRequest, RegisterRequest, TokenResponse } from '../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient, private router: Router) {}

  register(data: RegisterRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, data);
  }

  login(data: LoginRequest): Observable<TokenResponse> {
    console.log(' Enviando login a:', `${this.apiUrl}/auth/login`);
    console.log(' Datos:', data);
    
    return this.http.post<TokenResponse>(`${this.apiUrl}/auth/login`, data).pipe(
      tap((response) => {
        console.log('📥 Respuesta del backend:', response);
        console.log('🔑 Token recibido:', response.access_token);
        
        if (response.access_token) {
          localStorage.setItem('token', response.access_token);
          const guardado = localStorage.getItem('token');
          console.log('💾 Token guardado en localStorage:', guardado);
          console.log('🔍 Longitud del token:', guardado?.length);
        } else {
          console.error('❌ La respuesta NO tiene access_token');
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}