import { Routes } from '@angular/router';
import { Registrazione } from './registrazione/registrazione';
import { App } from './app';
import { Home } from './home/home';
import { Login } from './login/login';
import { UserComponent } from './user-component/user-component';
import { ProjectsComponent } from './projects-component/projects-component';

export const routes: Routes = [
    { path: 'signUp', component: Registrazione },
    { path: 'signIn', component: Login },
    { path: 'home', component: Home },
    { path: 'users', component: UserComponent},
    { path: 'project', component: ProjectsComponent},
    { path: '', redirectTo: 'home', pathMatch: 'full' }
];
