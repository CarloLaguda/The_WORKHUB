import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-user-component',
  imports: [CommonModule, FormsModule],
  templateUrl: './user-component.html',
  styleUrl: './user-component.css'
})
export class UserComponent {
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

  ngOnInit(): void {
    this.Users = this.userService.getAllUsers();
  }

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
      this.filterAge = undefined;
      this.filterSkill = undefined;
      this.filterCountry = undefined;
      this.Users = this.userService.getAllUsers();
    }
}
