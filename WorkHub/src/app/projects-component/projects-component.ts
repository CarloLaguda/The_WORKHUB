import { Component, Input } from '@angular/core';
import { Project } from '../models/project.model';
import { Observable } from 'rxjs';
import { ProjectService } from '../service/project.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-projects-component',
  imports: [CommonModule],
  templateUrl: './projects-component.html',
  styleUrl: './projects-component.css'
})
export class ProjectsComponent {
  projects!: Observable<Project[]>; // il simbolo $ indica che è un Observable

  constructor(private projectService: ProjectService) {}

  ngOnInit(): void {
    this.projects = this.projectService.getAllProjects();
    console.log(this.projects)
  }
  
}
