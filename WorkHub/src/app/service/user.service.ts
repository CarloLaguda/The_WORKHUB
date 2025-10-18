import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
providedIn: 'root'
})
export class UserService {
  private apiUrl = 'https://glowing-goggles-5ggww455qjx7c7p9w-5000.app.github.dev/';
  private currentUserSubject: BehaviorSubject<User | null>;

  constructor(private http: HttpClient) {
    // ✅ Al caricamento del service, controlla se c'è un utente salvato nel localStorage
    const savedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      savedUser ? JSON.parse(savedUser) : null
    );
  }

  // ✅ Observable pubblico per i componenti
  getCurrentUserObservable(): Observable<User | null> {
    return this.currentUserSubject.asObservable();
  }

  // ✅ Getter sincrono (utile per accesso immediato)
  getCurrentUserValue(): User | null {
   return this.currentUserSubject.value;
  }

  // ✅ Imposta o rimuove l’utente e aggiorna anche il localStorage
  setCurrentUser(user: User | null): void {
    this.currentUserSubject.next(user);
    if (user) {
      localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('currentUser');
    }
  }

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl + "api/users");
  }

  getCurrentUser(id_user: number): void {
    this.http.get<User>(`${this.apiUrl}api/users?user_id=${id_user}`).subscribe({
      next: (user) => {
        this.setCurrentUser(user); // ✅ salva anche nel localStorage
      },
      error: (err) => {
        console.error('Errore durante il recupero utente:', err);
        this.setCurrentUser(null);
      }
    });
  }

  getFilteredUsers(age?: number, skills?: string, country?: string): Observable<User[]> {
    let params = new HttpParams();
    if (age) params = params.set('age', age);
    if (skills) params = params.set('skills', skills);
    if (country) params = params.set('country', country);

  return this.http.get<User[]>(this.apiUrl + "api/users", { params });
  }

  updateUser(data: Partial<User> & { user_id: number }): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(this.apiUrl + "api/update_user", data);
  }

  addUserSkills(data: Partial<User> & { user_id: number }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(this.apiUrl + "api/add_user_skills_by_name", data);
  }

  // ✅ Logout che rimuove tutto
  logout(): void {
    this.setCurrentUser(null);
  }
}
