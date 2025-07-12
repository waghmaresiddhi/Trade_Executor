import { Routes } from '@angular/router';
import { OrdersComponent } from './components/orders/orders.component';

export const routes: Routes = [
  { path: '', redirectTo: 'orders', pathMatch: 'full' },
  { path: 'orders', component: OrdersComponent },
];
