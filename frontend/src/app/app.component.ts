import { Component } from '@angular/core';
import { RouterModule } from '@angular/router'; // <-- ✅ This is needed for <router-outlet>
import { CommonModule } from '@angular/common';

import { SidebarComponent } from './components/sidebar/sidebar.component';
import { OrderFormComponent } from './components/order-form/order-form.component';

@Component({
  selector: 'app-root',
  standalone: true,
  
  imports: [
    CommonModule,
    RouterModule,
    SidebarComponent,
    
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent {
  showOrderForm = false;

  openOrderForm() {
    this.showOrderForm = true;
  }

  closeOrderForm() {
    this.showOrderForm = false;
  }
}
