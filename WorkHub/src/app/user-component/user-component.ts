import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from "@angular/router";

@Component({
  selector: 'app-user-component',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './user-component.html',
  styleUrl: './user-component.css'
})
export class UserComponent implements OnInit 
{
  user: User | null = null; //Utente loggato

  Users!: Observable<User[]>; //Lista utenti
  expandedUserId: number | null = null;

  // Lista di skill disponibili
  skillsList: string[] = [
    "HTML","CSS","JavaScript","SQL","Python","Project Management",
    "Imbiancaggio","Idraulica","Marketing","Excel","Node.js",
    "React","Photoshop","UX Design","DevOps","SQL Server",
    "Docker","Content Writing","Carpentry","Testing"
  ];

  filterAge?: number;
  filterSkill?: string;
  filterCountry?: string;

  constructor(private userService: UserService) {}

  toggleDetails(userId: number) //Espandi i dettagli user
  {
    this.expandedUserId = this.expandedUserId === userId ? null : userId;
  }

  
  applyFilters() //Richiesta per gli user filtrati
  {
    this.Users = this.userService.getFilteredUsers(
      this.filterAge,
      this.filterSkill,
      this.filterCountry
    );
  }

  clearFilters() //Azzera filtri
  {
    this.filterAge = 0;
    this.filterSkill = '';
    this.filterCountry = '';
    this.Users = this.userService.getAllUsers();
  }

  ngOnInit(): void 
  {
    this.Users = this.userService.getAllUsers(); //Prende tutti user
    this.userService.getCurrentUserObservable().subscribe({ //salvo lo user loggato
      next: (u) => {
        this.user = u;
      }
    });
  }
}
