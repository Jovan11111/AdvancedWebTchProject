import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { LibraryService } from './library.service';

export const authGuard: CanActivateFn = () => {
  const library = inject(LibraryService);
  return library.user ? true : inject(Router).createUrlTree(['/login']);
};