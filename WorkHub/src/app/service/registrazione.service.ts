import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Register } from '../models/register.model';

@Injectable({
  providedIn: 'root'
})
export class RegistrationService {

  private baseUrl: string = "https://turbo-computing-machine-wrrww9xxr7jwc5wpp-5000.app.github.dev/api";

  constructor(private http: HttpClient) { }

  /**
   * Registra un nuovo utente
   * @param data Oggetto con i dati della registrazione
   */
  register(data: Register): Observable<Register> {
    return this.http.post<Register>(`${this.baseUrl}/register`, data);

  }
}
