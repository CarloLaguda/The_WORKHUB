import { TestBed } from '@angular/core/testing';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { AuthGuard } from './auth-guard';
import { UserService } from '../user.service';
import { of } from 'rxjs';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let userServiceSpy: jasmine.SpyObj<UserService>;
  let routerSpy: jasmine.SpyObj<Router>;

  beforeEach(() => {
    const userServiceMock = jasmine.createSpyObj('UserService', ['getCurrentUserValue']);
    const routerMock = jasmine.createSpyObj('Router', ['createUrlTree']);

    TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        { provide: UserService, useValue: userServiceMock },
        { provide: Router, useValue: routerMock }
      ]
    });

    guard = TestBed.inject(AuthGuard);
    userServiceSpy = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should allow activation if user is logged in', () => {
    userServiceSpy.getCurrentUserValue.and.returnValue({ id: 1, name: 'Test User' } as any);

    const result = guard.canActivate(new ActivatedRouteSnapshot(), {} as RouterStateSnapshot);
    expect(result).toBe(true);
  });

  it('should block activation and redirect if user is not logged in', () => {
    userServiceSpy.getCurrentUserValue.and.returnValue(null);
    const fakeUrlTree = {} as UrlTree;
    routerSpy.createUrlTree.and.returnValue(fakeUrlTree);

    const result = guard.canActivate(new ActivatedRouteSnapshot(), {} as RouterStateSnapshot);
    expect(result).toBe(fakeUrlTree);
    expect(routerSpy.createUrlTree).toHaveBeenCalledWith(['/signIn']);
  });
});
