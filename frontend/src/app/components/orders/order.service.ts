import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class OrderService {
  constructor(private http: HttpClient) {}

  // ✅ Get all orders
  getOrders() {
    return this.http.get<any>('http://localhost:8000/api/orders/');
  }

  // ✅ Place new order
  placeOrder(order: any) {
    return this.http.post<any>('http://localhost:8000/api/place-order/', order);
  }
}
