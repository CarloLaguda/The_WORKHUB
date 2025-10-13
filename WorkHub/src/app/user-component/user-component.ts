import { Component, Input } from '@angular/core';
import { User } from '../models/user.model';
import { Observable } from 'rxjs';
import { UserService } from '../service/user.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-user-component',
  imports: [CommonModule],
  templateUrl: './user-component.html',
  styleUrl: './user-component.css'
})
export class UserComponent {
  Users!: Observable<User[]>; // il simbolo $ indica che è un Observable
  
  constructor(private usertService: UserService) {}
  
  ngOnInit(): void {
    this.Users = this.usertService.getAllUsers();
    console.log(this.Users)
  }
    
}
