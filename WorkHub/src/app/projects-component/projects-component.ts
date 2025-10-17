import { Component, Input } from '@angular/core';
import { Project } from '../models/project.model';
import { Observable } from 'rxjs';
import { ProjectService } from '../service/project.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { RouterLink } from '@angular/router';
@Component({
  selector: 'app-projects-component',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './projects-component.html',
  styleUrl: './projects-component.css'
})
export class ProjectsComponent {
  projects!: Observable<Project[]>; // il simbolo $ indica che è un Observable
  user: User | null = null
  popupType: 'success' | 'error' = 'success';
  popupVisible: boolean = false;
  popupMessage: string = '';
  constructor(private projectService: ProjectService, private userService: UserService) {}

  skillsList: string[] = [
    "HTML","CSS","JavaScript","SQL","Python","Project Management",
    "Imbiancaggio","Idraulica","Marketing","Excel","Node.js",
    "React","Photoshop","UX Design","DevOps","SQL Server",
    "Docker","Content Writing","Carpentry","Testing"
  ];

  filterProjectSkill?: string;
  filterProjectAvailability?: string;

  // Toggle dettagli progetto
  expandedProjectId: number | null = null;

  toggleProjectDetails(id: number) {
    if (this.expandedProjectId === id) {
      this.expandedProjectId = null;
    } else {
      this.expandedProjectId = id;
    }
  }

  // Filtri progetto
  applyProjectFilters() {
    // Se vuoi filtrare lato server, fai qui la chiamata con parametri
    this.projects = this.projectService.getFilteredProjects(this.filterProjectSkill, this.filterProjectAvailability);
    console.log('Filtri applicati', this.filterProjectSkill, this.filterProjectAvailability);
  }

  clearProjectFilters() {
    this.filterProjectSkill = '';
    this.filterProjectAvailability = '';
    this.projects = this.projectService.getAllProjects();
  }

  add_userProject(project_id: number): void {
    if (this.user && this.user.user_id !== undefined) {
      this.projectService.joinUserToProject(project_id, this.user.user_id, 0).subscribe({
        next: (response) => {
          console.log("✅ Unione al progetto riuscita!", response);
          // Mostra popup di successo con il messaggio del backend
          this.showPopup('success', response.message || 'Ti sei unito con successo al progetto!');
        },
        error: (error) => {
          console.error("❌ Errore durante l'unione al progetto:", error);
          // Mostra popup di errore con il messaggio dal backend
          const errorMessage = error.error?.message || 'Si è verificato un errore sconosciuto.';
          this.showPopup('error', errorMessage);
        }
      });
    }
  }

showPopup(type: 'success' | 'error', message: string): void {
  this.popupType = type;
  this.popupMessage = message;
  this.popupVisible = true;

  // Chiudi automaticamente dopo 3 secondi
  setTimeout(() => {
    this.popupVisible = false;
  }, 3000);
}

  closePopup() {
    this.popupVisible = false;
  }

  ngOnInit(): void {
    this.projects = this.projectService.getAllProjects();
    this.userService.getCurrentUserObservable().subscribe({
      next: (u) => {
        this.user = u;
      }
    });
    console.log(this.projects)
  }
    
}
