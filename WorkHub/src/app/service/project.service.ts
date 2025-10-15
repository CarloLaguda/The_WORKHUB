import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project } from '../models/project.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private apiUrl = 'https://opulent-spork-wrrww9x6p7493557w-5000.app.github.dev/api/projects_details'; // URL della tua API

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

  createProject(
    title: string, 
    description: string, 
    availability: 'open' | 'full', 
    maxPersone: number, 
    creatorUserId: number
  ): Observable<Project> {
    const body = {
      title,
      description,
      availability,
      max_persone: maxPersone,
      creator_user_id: creatorUserId
    };

    return this.http.post<Project>(`${this.apiUrl}/create_projects`, body);
  }

  joinUserToProject(projectId: number, userId: number, isCreator: number): Observable<any> {
    const body = { project_id: projectId, user_id: userId, is_creator: isCreator };
    return this.http.post(`${this.apiUrl}/join_user_projects`, body);
  }
}

