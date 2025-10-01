import { Routes } from '@angular/router';
import { Registrazione } from './registrazione/registrazione';
import { App } from './app';
import { Home } from './home/home';

export const routes: Routes = [
    { path: 'signUp', component: Registrazione },
    { path: '', component: Home },
];
