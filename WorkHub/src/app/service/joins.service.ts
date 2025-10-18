import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProjectJoinService{
  private apiUrl = 'https://glowing-goggles-5ggww455qjx7c7p9w-5000.app.github.dev/api'; // Base URL

  constructor(private http: HttpClient) {}

  addSkillToProject(projectId: number, skillName: string): Observable<any> {
    const body = { project_id: projectId, skill_name: skillName };
    return this.http.post(`${this.apiUrl}/join_projects_skill`, body);
  }

  addEnvToProject(projectId: number, envName: string): Observable<any> {
    const body = { project_id: projectId, env_name: envName };
    return this.http.post(`${this.apiUrl}/join_projects_env`, body);
  }
}
