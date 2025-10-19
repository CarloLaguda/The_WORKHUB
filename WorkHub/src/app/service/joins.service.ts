import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProjectJoinService{
  private apiUrl = 'https://bookish-journey-pjjxxg6jpgjvf7vjp-5000.app.github.dev/'; // Base URL

  constructor(private http: HttpClient) {}

  addSkillToProject(projectId: number, skillName: string): Observable<any> { //Aggiungi le skill al progetto
    const body = { project_id: projectId, skill_name: skillName };
    return this.http.post(`${this.apiUrl}/join_projects_skill`, body);
  }

  addEnvToProject(projectId: number, envName: string): Observable<any> {//Aggiungi Gli ambiti al progetto
    const body = { project_id: projectId, env_name: envName };
    return this.http.post(`${this.apiUrl}/join_projects_env`, body);
  }
}
