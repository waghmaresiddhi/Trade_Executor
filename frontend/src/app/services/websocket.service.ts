import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private ltpSocket$: WebSocketSubject<any>;
  private orderSocket$: WebSocketSubject<any>;

  private ltpSubjects: { [symbol: string]: BehaviorSubject<any> } = {};
  private orderSubject = new BehaviorSubject<any>(null);

  constructor() {
    // ✅ LTP WebSocket (ws://localhost:8000/ws/ltp/)
    this.ltpSocket$ = webSocket('ws://localhost:8000/ws/ltp/');

    this.ltpSocket$.subscribe(
      (msg) => {
        console.log('📩 Received LTP message from backend:', msg); // ✅ Log incoming messages

        const symbol = msg?.symbol;
        if (!symbol) {
          console.warn('⚠️ Received LTP message with missing symbol:', msg);
          return;
        }

        if (symbol && msg?.ltp !== undefined) {
          if (!this.ltpSubjects[symbol]) {
            this.ltpSubjects[symbol] = new BehaviorSubject<any>(null);
          }
          this.ltpSubjects[symbol].next(msg);
        }
      },
      (err) => {
        console.error('❌ LTP WebSocket Error:', err);
        Object.values(this.ltpSubjects).forEach(subject => subject.next(null));
      },
      () => {
        console.warn('⚠️ LTP WebSocket Closed');
      }
    );

    // ✅ Order Update WebSocket (ws://localhost:8000/ws/order-updates/)
    this.orderSocket$ = webSocket('ws://localhost:8000/ws/order-updates/');

    this.orderSocket$.subscribe(
      (msg) => {
        console.log('📩 Order WebSocket Received:', msg);
        this.orderSubject.next(msg);
      },
      (err) => {
        console.error('❌ Order WebSocket Error:', err);
      },
      () => {
        console.warn('⚠️ Order WebSocket Closed');
      }
    );
  }

  // 👉 For LTP
  getLTPStream(symbol: string): Observable<any> {
    if (!this.ltpSubjects[symbol]) {
      this.ltpSubjects[symbol] = new BehaviorSubject<any>(null);
    }
    return this.ltpSubjects[symbol].asObservable();
  }

  requestLTP(symbol: string) {
    if (this.ltpSocket$) {
      console.log('📤 Subscribing to LTP for:', symbol);
      this.ltpSocket$.next({ type: 'subscribe', symbol });
    }
  }

  unsubscribeLTP(symbol: string) {
    if (this.ltpSocket$) {
      console.log('📤 Unsubscribing from LTP for:', symbol);
      this.ltpSocket$.next({ type: 'unsubscribe', symbol });
    }
  }

  // 👉 For Order Updates
  getOrderUpdates(): Observable<any> {
    return this.orderSubject.asObservable();
  }

  sendOrderMessage(message: any) {
    if (this.orderSocket$) {
      this.orderSocket$.next(message);
    }
  }
}
