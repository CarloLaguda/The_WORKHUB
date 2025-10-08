import { Routes } from '@angular/router';
import { Registrazione } from './registrazione/registrazione';
import { App } from './app';
import { Home } from './home/home';
import { Login } from './login/login';

export const routes: Routes = [
    { path: 'signUp', component: Registrazione },
    { path: 'signIn', component: Login },
    { path: 'home', component: Home },
    { path: '', redirectTo: 'home', pathMatch: 'full' }
];
