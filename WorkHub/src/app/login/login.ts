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
      if(username.value == "" || password.value == ""){
        console.log("username/email o password mancanti")
      }else{
        this.chiamata.login(username.value, password.value)
      }
    }
    ngOnInit() {
  document.body.style.overflow = 'hidden';
}

  ngOnDestroy() {
    document.body.style.overflow = 'auto';
  }
  showPassword: boolean = false;

  togglePassword() {
    this.showPassword = !this.showPassword;
  }
}
