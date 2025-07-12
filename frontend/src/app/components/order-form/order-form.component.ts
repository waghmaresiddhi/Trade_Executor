import { Component, EventEmitter, Output, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WebsocketService } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-order-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './order-form.component.html',
  styleUrls: ['./order-form.component.less']
})
export class OrderFormComponent implements OnDestroy {
  order = {
    symbol: '',
    quantity: null,
    orderType: 'LIMIT',
    orderMode: 'BUY',
    price: null,
    triggerPrice: null,
    product: 'INTRADAY',
    exchange: 'NSE',
    validity: 'DAY'
  };

  ltp: number | null = null;
  private debounceTimer: any;
  private ltpSub: Subscription | null = null;
  private lastSubscribedSymbol: string | null = null;

  @Output() close = new EventEmitter<void>();
  @Output() orderPlaced = new EventEmitter<any>();

  constructor(private websocket: WebsocketService, private cdr: ChangeDetectorRef) {}

  onSymbolInput(value: string) {
    this.order.symbol = value.trim().toUpperCase();
    clearTimeout(this.debounceTimer);

    this.debounceTimer = setTimeout(() => {
      if (this.order.symbol.length >= 3 && this.order.exchange) {
        const fullSymbol = `${this.order.exchange}:${this.order.symbol}-EQ`;
        console.log('🟢 Subscribing to:', fullSymbol);

        // 🔴 Unsubscribe from previous symbol
        if (this.lastSubscribedSymbol && this.lastSubscribedSymbol !== fullSymbol) {
          this.websocket.unsubscribeLTP(this.lastSubscribedSymbol);
          console.log('🔴 Unsubscribed from:', this.lastSubscribedSymbol);
        }

        this.ltpSub?.unsubscribe();
        this.ltp = null;

        this.ltpSub = this.websocket.getLTPStream(fullSymbol).subscribe(msg => {
          if (msg !== null && typeof msg === 'object') {
            const ltpRaw = msg.ltp;
            const precision = msg.precision ?? 2;

            if (typeof ltpRaw === 'number') {
              this.ltp = ltpRaw / Math.pow(10, precision);
              console.log(`📈 Adjusted LTP for ${fullSymbol}: ₹${this.ltp}`);
              this.cdr.detectChanges();
            }
          }
        });

        this.websocket.requestLTP(fullSymbol);
        this.lastSubscribedSymbol = fullSymbol;

      } else {
        this.ltp = null;
        this.ltpSub?.unsubscribe();

        // 🔴 Unsubscribe if symbol was cleared
        if (this.lastSubscribedSymbol) {
          this.websocket.unsubscribeLTP(this.lastSubscribedSymbol);
          console.log('🔴 Unsubscribed (symbol cleared):', this.lastSubscribedSymbol);
          this.lastSubscribedSymbol = null;
        }
      }
    }, 400);
  }

  onClose() {
    this.close.emit();
  }

  placeOrder() {
    if (!this.order.symbol || !this.order.quantity) {
      alert('Symbol and Quantity are required.');
      return;
    }

    if (this.order.orderType === 'LIMIT' && !this.order.price) {
      alert('Please enter price for Limit order.');
      return;
    }

    if (this.order.orderType === 'SL' && (!this.order.price || !this.order.triggerPrice)) {
      alert('SL order requires both price and trigger price.');
      return;
    }

    this.orderPlaced.emit({ ...this.order });
  }

  ngOnDestroy(): void {
    this.ltpSub?.unsubscribe();
    if (this.lastSubscribedSymbol) {
      this.websocket.unsubscribeLTP(this.lastSubscribedSymbol);
      console.log('🧹 Unsubscribed onDestroy:', this.lastSubscribedSymbol);
    }
  }
}
