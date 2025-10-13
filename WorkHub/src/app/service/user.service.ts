import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'https://fictional-space-halibut-7vvggrww9qw42rj94-5000.app.github.dev/api/users'; // URL della tua API

  constructor(private http: HttpClient) {}

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  getFilteredUsers(age?: number, skills?: string, country?: string): Observable<User[]> {
    let params = new HttpParams();

    if (age) params = params.set('age', age);
    if (skills) params = params.set('skills', skills);
    if (country) params = params.set('country', country);

    return this.http.get<User[]>(this.apiUrl, { params });
  }
}