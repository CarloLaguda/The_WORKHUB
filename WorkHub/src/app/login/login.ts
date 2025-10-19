import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { LoginService } from '../service/login.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { UserService } from '../service/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
  imports: [CommonModule, RouterLink],
})
export class Login implements OnInit, OnDestroy {

  showPassword: boolean = false;//Toggle password
  //POPUP variable
  popupVisible: boolean = false;
  popupMessage: string = '';
  popupType: 'success' | 'error' = 'success';
  //SERVICE PER FARE LE CHIAMATE HTTP
  constructor(private loginService: LoginService, private userService: UserService) {}

  togglePassword() {
    this.showPassword = !this.showPassword;
  }
  //StartLogin
  login_start(username: HTMLInputElement, password: HTMLInputElement) {
    if (!username.value || !password.value) {
      this.showPopup('⚠️ Insert credential to login', 'error');
      return;
    }

    const data = {
      username: username.value,
      password: password.value
    }

    this.loginService.login(data).subscribe({
      next: (res) => {
        if (res.message === 'Login successful') {
          this.showPopup('✅ Login Succesfully done', 'success');
          
          // reset campi solo in caso di successo
          username.value = '';
          password.value = '';

          // salvi user_id (opzionale)
          if (res.user_id) {
            this.userService.getCurrentUser(res.user_id)
            localStorage.setItem('user_id', res.user_id.toString()); //Salvo user nel local storage
          }

        } else {
          this.showPopup('❌ Invalid credential', 'error');
        }
      },
      error: (err) => {
        const msg = err.error?.message || 'Error during the login';
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
