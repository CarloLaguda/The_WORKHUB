import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { RegistrationService } from '../service/registrazione.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-registrazione',
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css'],
  imports: [CommonModule, RouterLink]
})
export class Registrazione implements OnInit, OnDestroy 
{

  showPassword: boolean = false; //Variabili per toggke password e per la data
  showPassword1: boolean = false;
  passwordError: boolean = false;
  dataNascita: string = ""
  button1: boolean = false //Accettazione termini
  button2: boolean = false

  constructor(private rService: RegistrationService) {}

  togglebutton1(){this.button1 = !this.button1}
  togglebutton2(){this.button2 = !this.button2}
  togglePassword() { this.showPassword = !this.showPassword; }
  togglePassword1() { this.showPassword1 = !this.showPassword1; }

  //Variabili e metodi per POPUP
  popupType: 'success' | 'error' | null = null;
  errorMessage: string = '';
  openPopup(type: 'success' | 'error', message?: string) 
  {

    this.popupType = type;
    if (type === 'error' && message) {
      this.errorMessage = message;
    }
  }
  closePopup() 
  {
    this.popupType = null;
    this.errorMessage = '';
  }
 
  //Metodo della registrazione
  register_start(
  username: HTMLInputElement,
  email: HTMLInputElement,
  password: HTMLInputElement,
  conf_pass: HTMLInputElement,
  nome: HTMLInputElement,
  cognome: HTMLInputElement,
  dataNascitaInput: HTMLInputElement,
  gender: HTMLSelectElement
  ) 
  {
    if (!username.value || !email.value || !password.value || !conf_pass.value || !nome.value || !cognome.value || !dataNascitaInput.value || !gender.value)
    {
      this.openPopup('error', '⚠️ You must insert all the field.');
      return;
    }

    if (!email.value.includes('@')) 
    {
      this.openPopup('error', '⚠️ You must insert a valide email');
      return;
    }

    if (password.value !== conf_pass.value) 
    {
      this.passwordError = true;
      this.openPopup('error', 'Passwords dont matches.');
      return;
    } else 
    {
      this.passwordError = false;
    }

    if(!this.button1 || !this.button2){this.openPopup('error', '⚠️ You must accept the terms'); return}

    const dataNascita = new Date(dataNascitaInput.value);
    const oggi = new Date();
    let etaVera = oggi.getFullYear() - dataNascita.getFullYear();
    const calcMese = oggi.getMonth() - dataNascita.getMonth();
    const calcGiorno = oggi.getDate() - dataNascita.getDate();
    if (calcMese < 0 || (calcMese === 0 && calcGiorno < 0)) etaVera--;

    const genderVero = gender.value.toLowerCase() === "male" ? "M" : "F";

    const regData = {
      username: username.value,
      email: email.value,
      password: password.value,
      first_name: nome.value,
      last_name: cognome.value,
      eta: etaVera,
      gender: genderVero
    };

    this.rService.register(regData).subscribe({
      next: res => 
      {
        console.log("✅ Registrazione completata", res);
        this.openPopup('success');

        // ✅ Reset campi SOLO in caso di successo
        username.value = '';
        email.value = '';
        password.value = '';
        conf_pass.value = '';
        nome.value = '';
        cognome.value = '';
        dataNascitaInput.value = '';
        gender.value = '';
      },
      error: err => 
      {
        console.error("❌ Registration error", err);
        const msg = err?.error?.message || 'Unaxpected error during registration.';
        this.openPopup('error', msg);
      }
    });
  }

  ngOnInit(): void 
  {
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void 
  {
    document.body.style.overflow = 'auto';
  }
}
