import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { App } from '../app';

@Component({
  selector: 'app-login',
  imports: [RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
    responde: any

    constructor(private chiamata: App) {}
    //Metodo locale per fare la chiamata http nell'app component
    login_start(username :HTMLInputElement, password: HTMLInputElement){
      console.log("Ciao")
      this.chiamata.login(username.value, password.value)
    }
}
