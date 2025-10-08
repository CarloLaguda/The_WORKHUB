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
  loading!: boolean //VARIABILE PER LE CHIAMTAE
  obs_projects!: Observable<Project[]> //OBSERVABLE PER PROGETTI
  project_all: Project[] = [] // TUTTI I PROGETTI

  obs_login!: Observable<Login> // OBSERVABLE PER LA LOGIN

  obs_user!: Observable<User[]> // OBSERVALE PER USER (TUTTI)
  users!: User[] //VETTORE USERS

  current_user_obs!: Observable<User> // OBSERVALE PER USER REGISTRATO
  current_user_Object!: User //CURRENT USER
  
   errore: string = ""
  
  url: string = "https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/" // LINK AL SERVER (DA CAMBIARE OGNI VOLTA)
  
 
  constructor(public http: HttpClient, public router: Router){}//CONSTRUCTOR

  login(username: string, password: string) { //LOGIN CON DATI REGISTRATI
    this.loading = true;
    this.errore = '';
    const body = { 
      "username":username, 
      "password": password };

    this.obs_login = this.http.post<Login>('https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/api/login', body);

    this.obs_login.subscribe(this.handleLoginResponse);
  }

  handleLoginResponse = (res: any) => {
    this.loading = false;
    if (res && res.user_id) {//SE CI RESTITUISCE L'ID DELLO USER ABBIAMO FATTO LA LOGIN !!!
      console.log("aaaaaaaaaa")
      localStorage.setItem('token', res.token);
      console.log('Login effettuato con successo ✅');
      this.getUser_Main(res.user_id) // PRENDO I DATI SOLO DELLO USER REGISTRATO
      this.router.navigate(['/home']); // VADO ALLA HOME
      //
    } else {
      this.errore = 'Credenziali non valide';
    }
  };

  getUser_Main(id: number){ //PRENDO USER REGISTRATO
    this.loading = true;
    this.errore = '';
    this.current_user_obs = this.http.get<User>('https://ideal-space-xylophone-q7664x7rjp72xp-5000.app.github.dev/api/users?user_id='+ id);
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

  getAllProject()// PRENDO TUTTI I PROGETTI
  {
    this.loading = true
    this.obs_projects = this.http.get<Project[]>(this.url)
    this.obs_projects.subscribe(this.getData_Project)
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
    this.getAllProject()
  }
}
