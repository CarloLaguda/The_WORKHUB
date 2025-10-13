import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private apiUrl = 'https://orange-fortnight-v66xxgwwv97wc6qpx-5000.app.github.dev/api/projects_details'; // URL della tua API

  constructor(private http: HttpClient) {}

  getAllProjects(): Observable<Project[]> {
    return this.http.get<Project[]>(this.apiUrl);
  }

  getFilteredProjects(skill?: string, availability?: string): Observable<Project[]> {
    let params = new HttpParams();

    if (skill) {
      params = params.set('skills', skill);
    }
    if (availability) {
      params = params.set('availability', availability);
    }

    return this.http.get<Project[]>(this.apiUrl, { params });
  }
}

