import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { RegisterComponent } from './components/register/register';
import { FincasComponent } from './fincas/fincas';
import { LotesComponent } from './lotes/lotes';
import { CultivosComponent } from './cultivos/cultivos';
import { LoteDetalleComponent } from './lotes/lote-detalle/lote-detalle';

export const routes: Routes = [
  { path: 'lotes/:id', component: LoteDetalleComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'fincas', component: FincasComponent },
  { path: 'lotes', component: LotesComponent },
  { path: 'cultivos', component: CultivosComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];