import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {
  usuario = '';
  password = '';
  errorMessage = '';

  constructor(
    private authService: AuthService, 
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  // 👈 1. CAMBIADO DE onLogin A onSubmit PARA QUE COINCIDA CON EL HTML
  onSubmit() {
    this.errorMessage = '';
    console.log('🔐 Intentando login con usuario:', this.usuario);

    this.authService.login({ usuario: this.usuario, password: this.password }).subscribe({
      next: (response) => {
        console.log('✅ Login exitoso, respuesta completa:', response);
        
        // Verificar que el token se guardó
        const tokenGuardado = localStorage.getItem('token');
        console.log('🔍 Token en localStorage después del login:', tokenGuardado);
        
        if (tokenGuardado) {
          console.log('🚀 Redirigiendo a /dashboard...');
          
          // 👈 2. CAMBIADO DE /fincas A /dashboard
          this.router.navigate(['/dashboard']).then(
            (navego) => console.log('🎯 Navegación exitosa:', navego),
            (err) => console.error('❌ Error en navegación:', err)
          );
        } else {
          console.error('❌ El token NO se guardó');
          this.errorMessage = 'Error: No se pudo guardar el token de sesión';
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('❌ Error en login:', err);
        this.errorMessage = err.error?.detail || 'Error al iniciar sesión';
        this.cdr.detectChanges();
      }
    });
  }
}