import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class RegisterComponent {
  usuario = '';
  password = '';
  message = '';
  isError = false;
  isSuccess = false;

  constructor(
    private authService: AuthService, 
    private router: Router,
    private cdr: ChangeDetectorRef // 👈 NUEVO: Para forzar la detección de cambios
  ) {}

  onRegister() {
    this.message = '';
    this.isError = false;
    this.isSuccess = false;

    this.authService.register({ usuario: this.usuario, password: this.password }).subscribe({
      next: (response: any) => {
        console.log('✅ DATOS RECIBIDOS DEL BACKEND:', response);
        
        this.message = response.message ? response.message : '¡Cuenta creada exitosamente!';
        this.isSuccess = true;
        this.isError = false;
        
        this.cdr.detectChanges();

        // Redirigir después de 3 segundos (tiempo suficiente para ver la animación)
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      },
      error: (err) => {
        console.error('❌ ERROR:', err);
        this.message = err.error?.detail || 'Error al crear la cuenta';
        this.isError = true;
        this.isSuccess = false;
        
        this.cdr.detectChanges();
      }
    });
  }
}