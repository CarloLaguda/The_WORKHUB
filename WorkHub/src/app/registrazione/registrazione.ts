import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormArray, FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { App } from '../app';

@Component({
  selector: 'app-registrazione',
  imports: [RouterLink],
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css']
})
export class Registrazione {

  dataNascita!: Date

  constructor(private app: App){}

  register_start(username: HTMLInputElement, email: HTMLInputElement, password: HTMLInputElement, conf_pass: HTMLInputElement, nome: HTMLInputElement, cognome: HTMLInputElement, eta: HTMLInputElement, gender: HTMLSelectElement){
    if(password.value == conf_pass.value){
      let oggi = new Date()
      this.dataNascita = new Date(eta.value)

      let etaVera = oggi.getFullYear() - this.dataNascita.getFullYear()
      let calcMese = oggi.getMonth() - this.dataNascita.getMonth()
      let calcGiorno = oggi.getDay() - this.dataNascita.getDay()

      if(calcMese < 0 || (calcMese == 0 && calcGiorno < 0)){
        etaVera -= 1
      }

      let genderVero: string = ""
      if(gender.value == "maschio"){
        genderVero = "M"
      }else if(gender.value == "femmina"){
        genderVero = "F"
      }

      this.app.register(username.value, email.value, password.value, nome.value, cognome.value, etaVera, genderVero)

    }else{
      console.log("Le password non sono uguali")
    }
  }

 ngOnInit(): void {
    // Blocca lo scroll
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void {
    // Ripristina lo scroll quando esci dal componente
    document.body.style.overflow = 'auto';
  }
}
