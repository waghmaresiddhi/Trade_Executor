import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OrderService } from './order.service';
import { CommonModule, NgIf, NgFor, DatePipe, NgClass } from '@angular/common';
import { OrderFormComponent } from '../order-form/order-form.component';
import { WebsocketService } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [
    CommonModule,
    NgIf,
    NgFor,
    NgClass,
    DatePipe,
    OrderFormComponent
  ],
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.less'],
  providers: [OrderService]
})
export class OrdersComponent implements OnInit, OnDestroy {
  showOrderForm = false;
  orders: any[] = [];
  ltpMap: { [symbol: string]: number | null } = {};
  errorMessage = '';
  successMessage = '';
  ltpSubs: { [symbol: string]: Subscription } = {};

  constructor(
    private http: HttpClient,
    private orderService: OrderService,
    private websocket: WebsocketService
  ) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  ngOnDestroy(): void {
    // ✅ Unsubscribe all active LTP streams
    Object.values(this.ltpSubs).forEach(sub => sub.unsubscribe());
  }

  openOrderForm() {
    this.showOrderForm = true;
    this.clearMessages();
  }

  closeOrderForm() {
    this.showOrderForm = false;
    this.clearMessages();
  }

  clearMessages() {
    this.errorMessage = '';
    this.successMessage = '';
  }

  handleOrderPlaced(order: any) {
    order.timestamp = new Date().toISOString();

    this.orderService.placeOrder(order).subscribe({
      next: (res: any) => {
        if (res.error) {
          this.errorMessage = res.error;
          setTimeout(() => this.errorMessage = '', 5000);
        } else {
          this.successMessage = '✅ Order placed successfully!';
          setTimeout(() => this.successMessage = '', 5000);
          this.loadOrders();
          this.showOrderForm = false;
        }
      },
      error: () => {
        this.errorMessage = '❌ Failed to place order.';
        setTimeout(() => this.errorMessage = '', 5000);
      }
    });
  }

  loadOrders() {
    this.orderService.getOrders().subscribe({
      next: (res) => {
        this.orders = res.orders ?? [];
        this.subscribeToSymbolsForLTP();
        this.listenToLTPUpdates();
      },
      error: (err) => {
        console.error('Error loading orders:', err);
      }
    });
  }

  // ✅ Updated for per-symbol subscriptions
  listenToLTPUpdates() {
    for (const order of this.orders) {
      const symbol = `${order.exchange}:${this.normalizeSymbol(order.symbol)}-EQ`;

      if (!this.ltpSubs[symbol]) {
        this.ltpSubs[symbol] = this.websocket.getLTPStream(symbol).subscribe((ltp) => {
          this.ltpMap[symbol] = ltp;
        });
      }
    }
  }

  // ✅ Sends symbol requests via WebSocket
  subscribeToSymbolsForLTP() {
    const uniqueSymbols = new Set<string>();
    for (const order of this.orders) {
      const cleanSymbol = this.normalizeSymbol(order.symbol);
      const fullSymbol = `${order.exchange}:${cleanSymbol}-EQ`;
      if (!uniqueSymbols.has(fullSymbol)) {
        uniqueSymbols.add(fullSymbol);
        this.websocket.requestLTP(fullSymbol);
      }
    }
  }

  getLTP(order: any): number | null {
    const cleanSymbol = this.normalizeSymbol(order.symbol);
    const fullSymbol = `${order.exchange}:${cleanSymbol}-EQ`;
    return this.ltpMap[fullSymbol] ?? null;
  }

  normalizeSymbol(symbol: string): string {
    return symbol
      .replace(/^NSE:|^BSE:/, '')
      .replace(/-EQ$/, '')
      .trim()
      .toUpperCase();
  }

  deleteLastFailedOrder() {
    this.http.delete('/api/delete-last-failed/').subscribe({
      next: (res: any) => {
        this.successMessage = res.message;
        setTimeout(() => this.successMessage = '', 5000);
        this.loadOrders();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Failed to delete last failed order.';
        setTimeout(() => this.errorMessage = '', 5000);
      }
    });
  }

  deleteOrder(orderId: number) {
    this.http.delete(`/api/delete-order/${orderId}/`).subscribe({
      next: (res: any) => {
        this.successMessage = res.message;
        setTimeout(() => this.successMessage = '', 5000);
        this.loadOrders();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Failed to delete order.';
        setTimeout(() => this.errorMessage = '', 5000);
      }
    });
  }
}
