import { Component, OnInit } from '@angular/core';
import { App } from '../app';
import { User } from '../models/user.model';

@Component({
  selector: 'app-profile',
  imports: [],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit{

  utente!: User

  constructor(public app: App){}

  ngOnInit(): void {
    this.utente = this.app.current_user_Object
  }
}
