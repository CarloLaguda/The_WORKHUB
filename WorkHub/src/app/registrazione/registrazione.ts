import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Register } from '../models/register.model';
import { RegistrationService } from '../service/registrazione.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-registrazione',
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css'],
  imports: [CommonModule, RouterLink]
})
export class Registrazione implements OnInit, OnDestroy {

  @ViewChild('registerBtn') registerBtn!: ElementRef<HTMLButtonElement>;

  showPassword: boolean = false;
  showPassword1: boolean = false;
  passwordError: boolean = false;
  dataNascita: string = ""
  constructor(private rService: RegistrationService) {}

  togglePassword() { this.showPassword = !this.showPassword; }
  togglePassword1() { this.showPassword1 = !this.showPassword1; }

  popupType: 'success' | 'error' | null = null;
  errorMessage: string = '';

  openPopup(type: 'success' | 'error', message?: string) {
    this.popupType = type;
    if (type === 'error' && message) {
      this.errorMessage = message;
    }
  }

  closePopup() {
    this.popupType = null;
    this.errorMessage = '';
  }
 
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
    if (!username.value || !email.value || !password.value || !conf_pass.value ||
        !nome.value || !cognome.value || !dataNascitaInput.value || !gender.value) {
      this.openPopup('error', '⚠️ Devi compilare tutti i campi.');
      return;
    }

    if (!email.value.includes('@')) {
      this.openPopup('error', '⚠️ Devi inserire una email valida.');
    return;
    }

    if (password.value !== conf_pass.value) {
      this.passwordError = true;
      this.openPopup('error', 'Le password non coincidono.');
      return;
    } else {
      this.passwordError = false;
    }

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
      next: res => {
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
      error: err => {
        console.error("❌ Errore registrazione", err);
        const msg = err?.error?.message || 'Si è verificato un errore inatteso.';
        this.openPopup('error', msg);
      }
    });
}

  ngOnInit(): void {
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void {
    document.body.style.overflow = 'auto';
  }
}
