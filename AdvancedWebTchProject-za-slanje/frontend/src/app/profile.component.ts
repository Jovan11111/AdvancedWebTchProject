import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LibraryService, Book, Profile } from './library.service';

@Component({
  standalone: true,
  imports: [FormsModule, RouterLink],
  template: `
    @if (profile) {
      <h1>Moj profil</h1>
      <p>{{ profile.user.firstName }} {{ profile.user.lastName }} | {{ profile.user.email }} | {{ profile.user.username }}</p>

      <h2>Pročitane knjige</h2>
      <ul aria-label="Pročitane knjige">
        @for (book of profile.readBooks; track book.id) {
          <li><a [routerLink]="['/books', book.id]">{{ book.title }}</a></li>
        } @empty { <li>Nema pročitanih knjiga.</li> }
      </ul>

      <h2>Lista želja</h2>
      <ul aria-label="Lista želja">
        @for (book of profile.wantedBooks; track book.id) {
          <li><a [routerLink]="['/books', book.id]">{{ book.title }}</a></li>
        } @empty { <li>Lista želja je prazna.</li> }
      </ul>

      <h2>Prijatelji</h2>
      <ul aria-label="Lista prijatelja">
        @for (friend of profile.friends; track friend.id) {
          <li><a [routerLink]="['/profile/user', friend.id]">{{ friend.username }}</a></li>
        } @empty { <li>Nemaš dodatih prijatelja.</li> }
      </ul>

      <section class="password-section" aria-labelledby="password-heading">
        <h2 id="password-heading">Promena lozinke</h2>
        <form (ngSubmit)="changePassword()" aria-describedby="password-note">
          <p id="password-note">Nova lozinka mora imati najmanje 8 karaktera, veliko slovo i broj.</p>
          <label for="old-password">Stara lozinka</label>
          <input id="old-password" name="oldPassword" type="password" autocomplete="current-password" [(ngModel)]="passwordData.oldPassword" required>
          <label for="new-password">Nova lozinka</label>
          <input id="new-password" name="newPassword" type="password" autocomplete="new-password" [(ngModel)]="passwordData.newPassword" required>
          <label for="confirm-password">Potvrdi novu lozinku</label>
          <input id="confirm-password" name="confirmPassword" type="password" autocomplete="new-password" [(ngModel)]="passwordData.confirmPassword" required>
          <button type="submit">Promeni lozinku</button>
        </form>
        @if (passwordError) { <p class="error-message" role="alert" aria-live="assertive">{{ passwordError }}</p> }
        @if (passwordMessage) { <p class="success-message" role="status" aria-live="polite">{{ passwordMessage }}</p> }
      </section>
    } @else { <p role="status" aria-live="polite">Učitavanje profila...</p> }
  `
})
export class ProfileComponent {
  private library = inject(LibraryService);
  profile?: Profile;
  passwordData = { oldPassword: '', newPassword: '', confirmPassword: '' };
  passwordError = '';
  passwordMessage = '';

  constructor() {
    this.library.profile().subscribe(profile => this.profile = profile as Profile);
  }

  changePassword() {
    this.passwordError = '';
    this.passwordMessage = '';
    this.library.changePassword(this.passwordData).subscribe({
      next: result => {
        this.passwordMessage = result.message;
        this.passwordData = { oldPassword: '', newPassword: '', confirmPassword: '' };
      },
      error: error => this.passwordError = error.error?.message ?? 'Promena lozinke nije uspela.'
    });
  }
}
