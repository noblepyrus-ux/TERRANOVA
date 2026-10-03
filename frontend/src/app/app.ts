import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App implements OnInit {
  title = 'Terranova';

  constructor(private router: Router) {}

  ngOnInit() {
    console.log('🚀 App inicializada');
    console.log('📍 Ruta actual:', this.router.url);
  }
}