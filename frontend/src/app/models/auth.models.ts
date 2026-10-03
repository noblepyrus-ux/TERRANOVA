// src/app/models/auth.model.ts

export interface Cuenta {
    id: number;
    usuario: string;
    rol: string;
  }
  
  export interface LoginRequest {
    usuario: string;
    password: string;
    rol?: string; // Opcional, el backend le pone 'admin' por defecto
  }
  
  export interface RegisterRequest extends LoginRequest {
    rol?: string;
  }
  
  export interface TokenResponse {
    access_token: string;
    token_type: string;
  }