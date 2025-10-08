import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { Component } from '@angular/core';
import { Prova } from './prova/prova';
import { HttpClient } from '@angular/common/http';
import { Project } from './models/project.model';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { Login } from './models/login.model';
import { User } from './models/user.model';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, Prova],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  loading!: boolean
  obs!: Observable<Project[]>
  obs_login!: Observable<Login>
  obs_user!: Observable<User[]>
  users!: User[]
  current_user_obs!: Observable<User>
  current_user_Object!: User
  url: string = "https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/"
  project_all: Project[] = []
 
  constructor(public http: HttpClient, public router: Router){}

  errore: string = ""
 

  login(username: string, password: string) {
    this.loading = true;
    this.errore = '';
    // creo il corpo della richiesta
    const body = { 
      "username":username, 
      "password": password };

    // salvo l'osservabile come fai tu con getAllProject
    this.obs_login = this.http.post<Login>('https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/api/login', body);

    // sottoscrizione con callback separata
    this.obs_login.subscribe(this.handleLoginResponse);
  }

  handleLoginResponse = (res: any) => {
    this.loading = false;
    // supponiamo che il backend risponda con { success: true, token: "..."}
    if (res && res.user_id) {
      console.log("aaaaaaaaaa")
      localStorage.setItem('token', res.token);
      console.log('Login effettuato con successo ✅');
      // redirect alla home
      // ATTENZIONE: serve il Router nel costruttore
      this.getUser_Main(res.user_id)
      this.router.navigate(['/home']);
      //
    } else {
      this.errore = 'Credenziali non valide';
    }
  };

  getUser_Main(id: number){
    this.loading = true;
    this.errore = '';
    // salvo l'osservabile come fai tu con getAllProject
    this.current_user_obs = this.http.get<User>('https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/api/users?user_id='+ id);

    // sottoscrizione con callback separata
    this.current_user_obs.subscribe(this.getUser_Main_data);
  }

  getUser_Main_data = (d: User) =>
  {
    this.current_user_Object = d
    if (this.current_user_Object.user_id === 0){
      this.errore = "Nessun pilota trovato :/"
    }
    else{
      console.log(this.current_user_Object)
      this.loading = false
    }
  }

  
  getAllProject()
  {
    this.loading = true
    this.obs = this.http.get<Project[]>(this.url)
    this.obs.subscribe(this.getData_Project)
  }

  getData_Project = (d: Project[]) =>
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

  ngOnInit(){
    //this.getAllProject()
  }
}
