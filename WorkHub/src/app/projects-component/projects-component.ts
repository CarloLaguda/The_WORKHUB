import { Component, Input } from '@angular/core';
import { Project } from '../models/project.model';
import { Observable } from 'rxjs';
import { ProjectService } from '../service/project.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-projects-component',
  imports: [CommonModule, FormsModule],
  templateUrl: './projects-component.html',
  styleUrl: './projects-component.css'
})
export class ProjectsComponent {
  projects!: Observable<Project[]>; // il simbolo $ indica che è un Observable

  constructor(private projectService: ProjectService) {}

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

  ngOnInit(): void {
    this.projects = this.projectService.getAllProjects();
    console.log(this.projects)
  }
    
}
