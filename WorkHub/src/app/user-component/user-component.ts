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
export class UserComponent implements OnInit {
  user: User | null = null; // 👈 Utente loggato

  Users!: Observable<User[]>;
  expandedUserId: number | null = null;

  // Lista di skill disponibili
  skillsList: string[] = [
    "HTML","CSS","JavaScript","SQL","Python","Project Management",
    "Imbiancaggio","Idraulica","Marketing","Excel","Node.js",
    "React","Photoshop","UX Design","DevOps","SQL Server",
    "Docker","Content Writing","Carpentry","Testing"
  ];

  // Lista di paesi basata dai tuoi dati
  countriesList: string[] = [
    "Italia","Stati Uniti","Spagna","Germania","Francia","Brasile"
  ];

  filterAge?: number;
  filterSkill?: string;
  filterCountry?: string;

  constructor(private userService: UserService) {}

  toggleDetails(userId: number) {
    this.expandedUserId = this.expandedUserId === userId ? null : userId;
  }

  
  applyFilters() {
      this.Users = this.userService.getFilteredUsers(
        this.filterAge,
        this.filterSkill,
        this.filterCountry
      );
  }
  clearFilters() {
    this.filterAge = 0;
    this.filterSkill = '';
    this.filterCountry = '';
    this.Users = this.userService.getAllUsers();
  }

  ngOnInit(): void {
    this.Users = this.userService.getAllUsers();
    this.userService.getCurrentUserObservable().subscribe({
      next: (u) => {
        this.user = u;
      }
    });
  }
}
