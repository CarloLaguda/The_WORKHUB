import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Project } from '../models/project.model';
import { ProjectService } from '../service/project.service';
import { ProjectJoinService } from '../service/joins.service';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './create-project.html',
  styleUrl: './create-project.css'
})
export class CreateProject {
  // 👤 Da sostituire con l'utente loggato (puoi recuperarlo dal tuo UserService)
  user: User | null = null;

  // ✅ Variabili per form
  projectSkill: string = '';
  selectedSkills: string[] = [];
  selectedEnvs: string[] = [];

  skillsList: string[] = [
    "HTML","CSS","JavaScript","SQL","Python","Project Management",
    "Imbiancaggio","Idraulica","Marketing","Excel","Node.js",
    "React","Photoshop","UX Design","DevOps","SQL Server",
    "Docker","Content Writing","Carpentry","Testing"
  ];

  envList: string[] = [
    'Web Development','Database','Marketing','Edilizia','Design','IT Operations','Content','QA','HR','Security'
  ];

  // ✅ Popup
  popupVisible = false;
  popupType: 'success' | 'error' = 'success';
  popupMessage = '';

  constructor(private projectService: ProjectService, private projectJoins:ProjectJoinService, private userService: UserService ) {}

  // 🔹 Gestione selezioni multiple
  toggleSkill(skill: string) {
    this.selectedSkills = this.selectedSkills.includes(skill)
      ? this.selectedSkills.filter(s => s !== skill)
      : [...this.selectedSkills, skill];
  }

  toggleEnv(env: string) {
    this.selectedEnvs = this.selectedEnvs.includes(env)
      ? this.selectedEnvs.filter(e => e !== env)
      : [...this.selectedEnvs, env];
  }

  // 🔹 Crea progetto
  createProject(title: string, description: string, maxPersone: number) {
  // Controllo per i campi obbligatori
  if (!title || !description || !maxPersone) {
    this.showPopup('Compila tutti i campi obbligatori!', 'error');
    return;
  }

  // Controllo se l'utente è autenticato
  if (!this.user || this.user.user_id === undefined) {
    this.showPopup('Utente non autenticato, impossibile creare il progetto.', 'error');
    return;
  }

  // Controllo se le skill sono selezionate
  if (!this.selectedSkills || this.selectedSkills.length === 0) {
    this.showPopup('Seleziona almeno una skill per il progetto.', 'error');
    return;
  }

  // Controllo se gli ambiti (env) sono selezionati
  if (!this.selectedEnvs || this.selectedEnvs.length === 0) {
    this.showPopup('Seleziona almeno un ambito per il progetto.', 'error');
    return;
  }

  // Chiama il service per creare il progetto
  this.projectService.createProject(
    title,
    description,
    'open', // 👈 sempre open di default
    maxPersone,
    this.user.user_id
  ).subscribe({
    next: (project: Project) => {
      console.log('✅ Progetto creato:', project);

      // Aggiungi le skill al progetto
      this.selectedSkills.forEach(skill => {
        this.projectJoins.addSkillToProject(project.project_id, skill).subscribe();
      });

      // Aggiungi gli ambiti al progetto
      this.selectedEnvs.forEach(env => {
        this.projectJoins.addEnvToProject(project.project_id, env).subscribe();
      });

      // Mostra il popup di successo
      this.showPopup('✅ Progetto creato con successo!', 'success');
    },
    error: (err) => {
      console.error('❌ Errore durante la creazione del progetto:', err);
      this.showPopup('❌ Errore durante la creazione del progetto', 'error');
    }
  });
}


  // 🔹 Gestione popup
  showPopup(message: string, type: 'success' | 'error') {
    this.popupMessage = message;
    this.popupType = type;
    this.popupVisible = true;
  }

  closePopup() {
    this.popupVisible = false;
  }

  ngOnInit(): void {
    this.userService.getCurrentUserObservable().subscribe({
      next: (u) => {
        this.user = u;
      }
    });
  }
}
