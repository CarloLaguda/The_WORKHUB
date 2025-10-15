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
  Skill: string = ""
  skills: string[] = [
    "HTML","CSS","JavaScript","SQL","Python","Project Management",
    "Imbiancaggio","Idraulica","Marketing","Excel","Node.js",
    "React","Photoshop","UX Design","DevOps","SQL Server",
    "Docker","Content Writing","Carpentry","Testing"
  ]

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
  addUserSkill(sn: string) {
  if (!this.user?.user_id) {
    console.error("User ID non disponibile");
    return;
  }

  const data: any = {
    user_id: this.user.user_id,
    skill_names: this.Skill
  };

  this.userService.addUserSkills(data).subscribe({
    next: (res) => {
      console.log(res.message);
      this.userService.getCurrentUser(this.user!.user_id);
    },
    error: (err) => {
      console.error('Errore aggiornamento skill:', err);
    }
  });
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

      // Ricarica l'utente aggiornato dal server e aggiorna BehaviorSubject e variabile locale
      this.userService.getCurrentUser(this.user!.user_id);

      // Non serve aggiornare manualmente this.user qui perché
      // ngOnInit già sottoscrive currentUser e aggiornerà la variabile automaticamente
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
