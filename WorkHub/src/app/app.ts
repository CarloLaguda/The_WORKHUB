import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Project } from './models/project.model';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { Login } from './models/login.model';
import { User } from './models/user.model';
import { Register } from './models/register.model';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  loading!: boolean //VARIABILE PER LE CHIAMTAE
  obs_projects!: Observable<Project[]> //OBSERVABLE PER PROGETTI
  project_all: Project[] = [] // TUTTI I PROGETTI

  obs_login!: Observable<Login> // OBSERVABLE PER LA LOGIN

  obs_register!: Observable<Register>

  obs_user!: Observable<User[]> // OBSERVALE PER USER (TUTTI)
  users!: User[] //VETTORE USERS

  current_user_obs!: Observable<User> // OBSERVALE PER USER REGISTRATO
  current_user_Object!: User //CURRENT USER
  
   errore: string = ""
  
  url: string = "https://opulent-spork-wrrww9x6p7493557w-5000.app.github.dev/" // LINK AL SERVER (DA CAMBIARE OGNI VOLTA)
  
 
  constructor(public http: HttpClient, public router: Router){}//CONSTRUCTOR

  login(username: string, password: string) { //LOGIN CON DATI REGISTRATI
    this.loading = true;
    this.errore = '';
    const body = { 
      "username":username, 
      "password": password };

    this.obs_login = this.http.post<Login>(`${this.url}api/login`, body);

    this.obs_login.subscribe(this.handleLoginResponse);
  }

  handleLoginResponse = (res: any) => {
    this.loading = false;
    if (res && res.user_id) {//SE CI RESTITUISCE L'ID DELLO USER ABBIAMO FATTO LA LOGIN !!!
      localStorage.setItem('token', res.token);
      console.log('Login effettuato con successo ✅');
      this.getUser_Main(res.user_id) // PRENDO I DATI SOLO DELLO USER REGISTRATO
      this.router.navigate(['/home']); // VADO ALLA HOME
      //
    } else {
      this.errore = 'Credenziali non valide';
    }
  };

  register(username: string, email: string, password: string, nome: string, cognome: string, eta: number, gender: string){
    let reg_data = {
      "username": username,
      "email": email,
      "password": password,
      "first_name": nome,
      "last_name": cognome,
      "eta": eta,
      "gender": gender,
    }

    console.log(reg_data)

    this.obs_register = this.http.post<Register>(`${this.url}api/register`, reg_data)
    this.obs_register.subscribe(this.handleRegisterResponse)
  }

  handleRegisterResponse = (response: any) => {
    console.log(response)
  }

  getUser_Main(id: number){ //PRENDO USER REGISTRATO
    this.loading = true;
    this.errore = '';
    this.current_user_obs = this.http.get<User>(`${this.url}api/users?user_id=`+ id);
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

  /*
  getAllProject()// PRENDO TUTTI I PROGETTI
  {
    if (this.project_all.length>0){
        this.project_all = []
    }
    this.loading = true
    this.obs_projects = this.http.get<Project[]>(this.url+"api/projects_details")
    this.obs_projects.subscribe(this.getData_Project)
    console.log(this.project_all + " buonasera")
    return this.project_all
  }

  getData_Project = (d: Project[]) =>
  {
    console.log(d + " ciao")
    this.project_all = d
    if (this.project_all.length === 0){
      this.errore = "Nessun progetto trovato :/"
    }
    else{
      console.log(this.project_all + " arrivderci")
      this.loading = false
    }
  }

  getAllUsers(){
    this.users = []
    this.loading = true
    this.obs_user = this.http.get<User[]>(this.url+"api/users")
    this.obs_user.subscribe(this.getData_Users)
  }
  getData_Users = (d: User[]) => {
    this.users= d
    if (this.users.length === 0){
      this.errore = "Nessun progetto trovato :/"
    }
    else{
      console.log(this.users)
      this.loading = false
    }
  }
  */
  ngOnInit(){
    //this.getAllUsers()
    //this.getAllProject()
  }
}
