import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Login } from '../models/login.model';

export interface LoginResponse {
  message: string;
  user_id?: number;
}

@Injectable({ //Service per la login
  providedIn: 'root'
})
export class LoginService { //Service per fare la login 
  private apiUrl = 'https://ominous-fortnight-q77ww96jrgxq26x69-5000.app.github.dev/api/login';

  constructor(private http: HttpClient) {}

  login(data: Login): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(this.apiUrl, data);
  }
}
