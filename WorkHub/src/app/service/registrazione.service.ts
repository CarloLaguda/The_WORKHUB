import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Register } from '../models/register.model';

@Injectable({
  providedIn: 'root'
})
export class RegistrationService {

  private baseUrl: string = "https://didactic-adventure-4j66vrj45vr2q6v5-5000.app.github.dev//api";

  constructor(private http: HttpClient) { }

  /**
   * Registra un nuovo utente
   * @param data Oggetto con i dati della registrazione
   */
  register(data: Register): Observable<Register> {
    console.log(data)
    return this.http.post<Register>(`${this.baseUrl}/register`, data);

  }
}
