import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { UserService } from '../user.service';  // aggiorna con il nome corretto

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private userService: UserService, private router: Router) {}
  //PROTEZIONE PER LE ROTTE IN CASO DI FURBETTI
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ):boolean | UrlTree | Observable<boolean | UrlTree> | Promise<boolean | UrlTree> {
    const currentUser = this.userService.getCurrentUserValue();
    if (currentUser) {
      // L'utente è loggato, consenti l'accesso
      return true;
    }

    // L'utente non è loggato, reindirizza al login
    return this.router.createUrlTree(['/signIn']);
  }
}