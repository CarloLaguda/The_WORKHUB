import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { LoginService } from '../service/login.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
  imports: [CommonModule],
})
export class Login implements OnInit, OnDestroy {

  @ViewChild('loginBtn') loginBtn!: ElementRef<HTMLButtonElement>;

  showPassword: boolean = false;
  popupVisible: boolean = false;
  popupMessage: string = '';
  popupType: 'success' | 'error' = 'success';

  constructor(private loginService: LoginService) {}

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  login_start(username: HTMLInputElement, password: HTMLInputElement) {
    if (!username.value || !password.value) {
      this.showPopup('⚠️ Inserisci username/email e password', 'error');
      return;
    }

    const data = {
      username: username.value,
      password: password.value
    }

    this.loginService.login(data).subscribe({
      next: (res) => {
        if (res.message === 'Login successful') {
          this.showPopup('✅ Login effettuato con successo!', 'success');
          
          // reset campi solo in caso di successo
          username.value = '';
          password.value = '';

          // salvi user_id (opzionale)
          if (res.user_id) {
            localStorage.setItem('user_id', res.user_id.toString());
          }

          // chiudi popup e puoi reindirizzare dopo 2s
          setTimeout(() => {
            this.popupVisible = false;
            // this.router.navigate(['/home']);
          }, 2000);

        } else {
          this.showPopup('❌ Credenziali non valide', 'error');
        }
      },
      error: (err) => {
        console.error('Errore login:', err);
        const msg = err.error?.message || 'Errore durante il login';
        this.showPopup(`❌ ${msg}`, 'error');
      }
    });
  }

  showPopup(message: string, type: 'success' | 'error') {
    this.popupMessage = message;
    this.popupType = type;
    this.popupVisible = true;
  }

  closePopup() {
    this.popupVisible = false;
  }

  ngOnInit() {
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy() {
    document.body.style.overflow = 'auto';
  }
}
