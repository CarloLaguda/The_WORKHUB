import { Component, OnInit } from '@angular/core';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { Router, RouterLink } from '@angular/router';
import { ThisReceiver } from '@angular/compiler';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProjectService } from '../service/project.service';
import { Project } from '../models/project.model';
@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  utente!: User;
  progetti: Project[] = [];
  selectedStatus: string = '';

  user: User | null = null;
  tUser: Boolean = false;
  tMail: Boolean = false;
  tStatus: Boolean = false;
  tCountry: Boolean = false;
  tAnnixp: Boolean = false;
  tPass: boolean = false;
  showPassword: boolean = false;
  Skill: string = "";
  skills: string[] = [
    "HTML", "CSS", "JavaScript", "SQL", "Python", "Project Management",
    "Imbiancaggio", "Idraulica", "Marketing", "Excel", "Node.js",
    "React", "Photoshop", "UX Design", "DevOps", "SQL Server",
    "Docker", "Content Writing", "Carpentry", "Testing"
  ];

  popupVisible: boolean = false;
  popupMessage: string = '';
  popupType: 'success' | 'error' = 'success';

  constructor(private userService: UserService, private router: Router, private projectService: ProjectService) {}

  toggleUsername() { this.tUser = !this.tUser; }
  toggleMail() { this.tMail = !this.tMail; }
  toggleCountry() { this.tCountry = !this.tCountry; }
  toggleStatus() { this.tStatus = !this.tStatus; }
  toggleAnniexp() { this.tAnnixp = !this.tAnnixp; }
  togglePass() { this.tPass = !this.tPass; }
  togglePasswordText() { this.showPassword = !this.showPassword; }

  startLogout() {
    this.userService.logout();
    this.showPopup('success', 'Logout effettuato con successo');
    this.router.navigate(['/signIn']);
  }

  addUserSkill(sn: string) {
    if (!this.user?.user_id) {
      console.error("User ID non disponibile");
      this.showPopup('error', 'Impossibile aggiungere la skill: ID utente mancante');
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
        this.showPopup('success', 'Skill aggiunta con successo');
      },
      error: (err) => {
        console.error('Errore aggiornamento skill:', err);
        this.showPopup('error', 'Errore nell\'aggiunta della skill');
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
        this.userService.getCurrentUser(this.user!.user_id);
        this.showPopup('success', 'Informazioni aggiornate con successo');
      },
      error: (err) => {
        console.error('Errore aggiornamento:', err);
        this.showPopup('error', 'Errore nell\'aggiornamento delle informazioni');
      }
    });
  }

  showPopup(type: 'success' | 'error', message: string) {
    this.popupType = type;
    this.popupMessage = message;
    this.popupVisible = true;
    setTimeout(() => {
      this.popupVisible = false;
    }, 3000); // Nascondi popup dopo 3 secondi
  }

  closePopup() {
    this.popupVisible = false;
  }

  ngOnInit(): void {
    // Sottoscrizione per ricevere i dati aggiornati dell'utente
    this.userService.getCurrentUserObservable().subscribe({
      next: (u) => {
        this.user = u;
        if (u && u.user_id) {
          this.projectService.getUserProjects(u.user_id).subscribe({
            next: (projects) => {
              this.progetti = projects;
              console.log('Progetti trovati:', projects);
            },
            error: (err) => console.error('Errore nel caricamento progetti:', err)
          });
        }
      }
    });
  }
}
