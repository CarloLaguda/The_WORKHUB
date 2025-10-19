import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
providedIn: 'root'
})
export class UserService {//SERVICE per la gestione degli uUSER
  private apiUrl = 'https://fictional-journey-q77ww966qrvq34pwv-5000.app.github.dev/api';
  private currentUserSubject: BehaviorSubject<User | null>; //User Loggato

  constructor(private http: HttpClient) {
    //Al caricamento del service, controlla se c'è un utente salvato nel localStorage
    const savedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      savedUser ? JSON.parse(savedUser) : null
    );
  }

  //Ritorna un observable
  getCurrentUserObservable(): Observable<User | null> {
    return this.currentUserSubject.asObservable();
  }

  //Ritorna i valori
  getCurrentUserValue(): User | null {
   return this.currentUserSubject.value;
  }

  //Imposta o rimuove l’utente e aggiorna anche il localStorage
  setCurrentUser(user: User | null): void {
    this.currentUserSubject.next(user);
    if (user) {
      localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('currentUser');
    }
  }

  //GET Per tutti gli user
  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl + "/users");
  }

  //Get del currentuser
  getCurrentUser(id_user: number): void {
    this.http.get<User>(`${this.apiUrl}/users?user_id=${id_user}`).subscribe({
      next: (user) => {
        this.setCurrentUser(user); //Salva anche nel localStorage
      },
      error: (err) => {
        console.error('Errore durante il recupero utente:', err);
        this.setCurrentUser(null);
      }
    });
  }

  //Filtro per gli user
  getFilteredUsers(age?: number, skills?: string, country?: string): Observable<User[]> {
    let params = new HttpParams();
    if (age) params = params.set('age', age);
    if (skills) params = params.set('skills', skills);
    if (country) params = params.set('country', country);
    return this.http.get<User[]>(this.apiUrl + "/users", { params });
  }

  //Aggiorna dati user
  updateUser(data: Partial<User> & { user_id: number }): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(this.apiUrl + "/update_user", data);
  }
  //Aggiungi skill allo user
  addUserSkills(data: Partial<User> & { user_id: number }): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(this.apiUrl + "/add_user_skills_by_name", data);
  }

  //Logout che rimuove tutto
  logout(): void {
    this.setCurrentUser(null);
  }
}
