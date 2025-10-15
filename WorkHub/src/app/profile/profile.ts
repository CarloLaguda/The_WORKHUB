import { Component, OnInit } from '@angular/core';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { Router } from '@angular/router';
import { ThisReceiver } from '@angular/compiler';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit{

  utente!: User
  selectedStatus: string = '';

  user: User | null = null;
  tUser: Boolean = false
  tMail: Boolean = false
  tStatus: Boolean = false
  tCountry: Boolean = false
  tAnnixp: Boolean = false
  tPass: boolean = false
  showPassword: boolean = false
  constructor(private userService: UserService, private router: Router) {}

  
  toggleUsername(){this.tUser = !this.tUser}
  toggleMail(){this.tMail = !this.tMail}
  toggleCountry(){this.tCountry = !this.tCountry}
  toggleStatus(){this.tStatus = !this.tStatus}
  toggleAnniexp(){this.tAnnixp = !this.tAnnixp}
  togglePass(){this.tPass = !this.tPass}
  togglePasswordText(){this.showPassword = !this.showPassword}
  startLogout()
  {
    this.userService.logout()
    this.router.navigate(['/signIn']);

  }

  updateUser(campo: keyof User, valore: string) {
    if (!this.user) return; // sicurezza

    const payload: Partial<User> & { user_id: number } = {
      user_id: this.user.user_id,
      [campo]: valore
    };

    this.userService.updateUser(payload).subscribe({
      next: (res) => {
        console.log(res.message);
        // Aggiorna subito il BehaviorSubject
        const updatedUser = { ...this.user!, [campo]: valore };
        this.userService.currentUser.next(updatedUser);
        this.user = updatedUser; // aggiorna anche la variabile locale
      },
      error: (err) => {
        console.error('Errore aggiornamento:', err);
      }
    });
  }

  ngOnInit(): void {
    // ✅ Sottoscriviti al BehaviorSubject per ricevere i dati aggiornati
    this.userService.getCurrentUserObservable().subscribe({
      next: (u) => {
        this.user = u;
        console.log('👤 Profilo caricato:', u);
      }
    });
  }

}
