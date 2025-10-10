import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { App } from '../app';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-registrazione',
  imports: [RouterLink, CommonModule, FormsModule],
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css']
})
export class Registrazione implements OnInit, OnDestroy {

  @ViewChild('registerBtn') registerBtn!: ElementRef<HTMLButtonElement>;

  dataNascita!: Date;
  showPassword: boolean = false;
  showPassword1: boolean = false;
  passwordError: boolean = false;

  constructor(private app: App) {}

  togglePassword() { this.showPassword = !this.showPassword; }
  togglePassword1() { this.showPassword1 = !this.showPassword1; }

  register_start(
    username: HTMLInputElement,
    email: HTMLInputElement,
    password: HTMLInputElement,
    conf_pass: HTMLInputElement,
    nome: HTMLInputElement,
    cognome: HTMLInputElement,
    dataNascitaInput: HTMLInputElement,
    gender: HTMLSelectElement
  ) {
    if (!username.value || !email.value || !password.value || !conf_pass.value ||
        !nome.value || !cognome.value || !dataNascitaInput.value || !gender.value) {
      console.log("Devi compilare tutti i campi");
      return;
    }

    if (password.value !== conf_pass.value) {
      this.passwordError = true;
      console.log("Le password non sono uguali");
      return;
    } else {
      this.passwordError = false;
    }

    this.dataNascita = new Date(dataNascitaInput.value);
    const oggi = new Date();
    let etaVera = oggi.getFullYear() - this.dataNascita.getFullYear();
    const calcMese = oggi.getMonth() - this.dataNascita.getMonth();
    const calcGiorno = oggi.getDate() - this.dataNascita.getDate();
    if (calcMese < 0 || (calcMese === 0 && calcGiorno < 0)) etaVera--;

    let genderVero = gender.value.toLowerCase() === "maschio" ? "M" : "F";

    this.app.register(
      username.value, email.value, password.value,
      nome.value, cognome.value, etaVera, genderVero
    );
  }

  onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.registerBtn.nativeElement.click();
    }
  }

  ngOnInit(): void {
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void {
    document.body.style.overflow = 'auto';
  }
}
