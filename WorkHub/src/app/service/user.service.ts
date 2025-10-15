import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'https://musical-lamp-x55jj9xxwg9j3vr4w-5000.app.github.dev/api/users'; // URL della tua API
  public currentUser = new BehaviorSubject<User | null>(null);
  constructor(private http: HttpClient) {}

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  getCurrentUser(id_user: number){
    return this.http.get<User>(`${this.apiUrl}?user_id=${id_user}`).subscribe({
      next: (user) => {
        this.currentUser.next(user); // ✅ aggiorna il BehaviorSubject
        console.log(this.currentUser)
      },
      error: (err) => {
        console.error('Errore durante il recupero utente:', err);
        this.currentUser.next(null); // opzionale, reset in caso di errore
      }
    });
  }
  // ✅ Metodo per ottenere l'utente come Observable
  getCurrentUserObservable(): Observable<User | null> {
    return this.currentUser.asObservable();
  }

  // ✅ Metodo per ottenere direttamente il valore (non reattivo)
  getCurrentUserValue(): User | null {
    return this.currentUser.value;
  }
  
  getFilteredUsers(age?: number, skills?: string, country?: string): Observable<User[]> {
    let params = new HttpParams();

    if (age) params = params.set('age', age);
    if (skills) params = params.set('skills', skills);
    if (country) params = params.set('country', country);

    return this.http.get<User[]>(this.apiUrl, { params });
  }

  logout(): void {
    this.currentUser.next(null); 
  }

  updateUser(data: Partial<User> & { user_id: number }){
    return this.http.put<{ message: string }>("https://musical-lamp-x55jj9xxwg9j3vr4w-5000.app.github.dev/api/update_user", data);
  }

}