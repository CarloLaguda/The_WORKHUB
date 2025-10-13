import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Register } from '../models/register.model';
import { RegistrationService } from '../service/registrazione.service';

@Component({
  selector: 'app-registrazione',
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css']
})
export class Registrazione implements OnInit, OnDestroy {

  @ViewChild('registerBtn') registerBtn!: ElementRef<HTMLButtonElement>;

  showPassword: boolean = false;
  showPassword1: boolean = false;
  passwordError: boolean = false;

  constructor(private rService: RegistrationService) {}

  togglePassword() { this.showPassword = !this.showPassword; }
  togglePassword1() { this.showPassword1 = !this.showPassword1; }


  /*
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

    const dataNascita = new Date(dataNascitaInput.value);
    const oggi = new Date();
    let etaVera = oggi.getFullYear() - dataNascita.getFullYear();
    const calcMese = oggi.getMonth() - dataNascita.getMonth();
    const calcGiorno = oggi.getDate() - dataNascita.getDate();
    if (calcMese < 0 || (calcMese === 0 && calcGiorno < 0)) etaVera--;

    const genderVero = gender.value.toLowerCase() === "maschio" ? "M" : "F";

   const regData: Register = {
      username: username.value,
      email: email.value,
      password: password.value,
    //  first_name: nome.value,
      last_name: cognome.value,
      eta: etaVera,
      gender: genderVero
    };

    this.rService.register(regData).subscribe({
      next: res => console.log("Registrazione completata ✅", res),
      error: err => console.error("Errore registrazione ❌", err)
    });
  }
*/
  ngOnInit(): void {
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void {
    document.body.style.overflow = 'auto';
  }
}
