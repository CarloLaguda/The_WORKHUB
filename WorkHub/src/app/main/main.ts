import { Component, OnInit } from '@angular/core';
import { Project } from '../models/project.model';
import { App } from '../app';
import { appConfig } from '../app.config';
import { ProjectsComponent } from '../projects-component/projects-component';

@Component({
  selector: 'app-main',
  imports: [ProjectsComponent],
  templateUrl: './main.html',
  styleUrl: './main.css'
})

export class Main implements OnInit{
  progetti!: Project[]

  constructor(private app: App){}

  ngOnInit(): void {
    this.progetti = this.app.project_all
  }
}
