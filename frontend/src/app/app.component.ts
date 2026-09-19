import { Component } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { inject } from '@angular/core';
import { LibraryService } from './library.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.component.html'
})
export class AppComponent {
  library = inject(LibraryService);
  router = inject(Router);
  get user() { return this.library.user; }
  logout() { this.library.user = null; this.router.navigate(['/login']); }
}
