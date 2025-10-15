import { Routes } from '@angular/router';
import { Registrazione } from './registrazione/registrazione';
import { Home } from './home/home';
import { Login } from './login/login';
import { UserComponent } from './user-component/user-component';
import { ProjectsComponent } from './projects-component/projects-component';
import { PrivacyComponent } from './privacy-component/privacy-component';
import { Profile } from './profile/profile';

import { AuthGuard } from './service/auth-guard/auth-guard';  // percorso corretto

export const routes: Routes = [
  { path: 'signUp', component: Registrazione },
  { path: 'signIn', component: Login },
  { path: 'home', component: Home },
  { path: 'users', component: UserComponent}, //canActivate: [AuthGuard] },
  { path: 'projects', component: ProjectsComponent, canActivate: [AuthGuard] },
  { path: 'info', component: PrivacyComponent },
  { path: 'profile', component: Profile}, //canActivate: [AuthGuard] },
  { path: '', redirectTo: 'home', pathMatch: 'full' }
];