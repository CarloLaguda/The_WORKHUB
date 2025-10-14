import { Component, OnInit } from '@angular/core';
import { App } from '../app';
import { User } from '../models/user.model';
import { UserService } from '../service/user.service';

@Component({
  selector: 'app-profile',
  imports: [],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit{

  utente!: User

  user: User | null = null;

  constructor(private userService: UserService) {}

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
