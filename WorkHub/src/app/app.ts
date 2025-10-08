import { RouterOutlet } from '@angular/router';
import { Component } from '@angular/core';
import { Prova } from './prova/prova';
import { HttpClient } from '@angular/common/http';
import { Project } from './models/project.model';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, Prova],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  loading!: boolean
  obs!: Observable<Project[]>
  url: string = "https://congenial-couscous-wrrww9xxr7vghg476-5000.app.github.dev/api/all_projects"
  project_all: Project[] = []
  constructor(public http: HttpClient){}

  errore: string = ""

  getAllRider()
  {
    this.loading = true
    this.obs = this.http.get<Project[]>(this.url)
    this.obs.subscribe(this.getData)
  }

  getData = (d: Project[]) =>
  {
    this.project_all = d
    if (this.project_all.length === 0){
      this.errore = "Nessun pilota trovato :/"
    }
    else{
      console.log(this.project_all)
      this.loading = false
    }
  }

  trackById(index: number, item: any): any {
    return item.project_id;  
  }

  ngOnInit(){
    this.getAllRider()
  }
}
