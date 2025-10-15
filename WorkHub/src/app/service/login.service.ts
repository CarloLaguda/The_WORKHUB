import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Login } from '../models/login.model';

export interface LoginResponse {
  message: string;
  user_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class LoginService {
  private apiUrl = 'https://shiny-space-fiesta-7vvggrwwv9g939rg-5000.app.github.dev/api/login';

  constructor(private http: HttpClient) {}

  login(data: Login): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(this.apiUrl, data);
  }
}
