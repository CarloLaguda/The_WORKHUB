import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Register } from '../models/register.model';

@Injectable({
  providedIn: 'root'
})
export class RegistrationService {//SERVICE PER LA LOGIN

  private baseUrl: string = "https://friendly-parakeet-977ppqww9v4jh7wrp-5000.app.github.dev/api/register";

  constructor(private http: HttpClient) { }

  /**
   * Registra un nuovo utente
   * @param data Oggetto con i dati della registrazione
   */
  register(data: Register): Observable<Register> {
    return this.http.post<Register>(this.baseUrl, data);

  }
}
