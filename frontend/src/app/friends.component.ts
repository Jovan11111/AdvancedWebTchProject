import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LibraryService } from './library.service';

@Component({ standalone: true, imports: [FormsModule, RouterLink], template: `<h1>Prijatelji</h1><form (ngSubmit)="follow()" aria-label="Dodavanje prijatelja"><label for="friend-username">Username prijatelja</label><input id="friend-username" name="username" [(ngModel)]="username" required><button type="submit">Pošalji zaprati</button></form>@if (message) {<p role="status" aria-live="polite">{{ message }}</p>}<h2>Aktivnosti prijatelja</h2><ul aria-label="Aktivnosti prijatelja">@for (activity of activities; track activity.username + activity.bookTitle + activity.updatedAt) {<li><strong>{{ activity.username }}</strong> {{ activity.status === 'read' ? 'označio/la je kao pročitanu' : 'želi da pročita' }} knjigu <em>{{ activity.bookTitle }}</em></li>} @empty {<li>Nema aktivnosti prijatelja.</li>}</ul><h2>Lista prijatelja</h2><ul aria-label="Lista prijatelja">@for (friend of friends; track friend.id) {<li class="admin-book-row"><a [routerLink]="['/profile/user', friend.id]">{{ friend.username }}</a><button type="button" (click)="removeFriend(friend.id)">Ukloni</button></li>} @empty {<li>Još nemaš prijatelje.</li>}</ul>` })
export class FriendsComponent {
  private library = inject(LibraryService); username = ''; message = ''; friends: any[] = []; activities: any[] = [];
  constructor() { this.load(); }
  load() { this.library.friends().subscribe(friends => this.friends = friends); this.library.activities().subscribe(activities => this.activities = activities); }
  follow() { this.library.addFriend(this.username).subscribe({ next: result => { this.message = `${result.friend.username} je dodat/a.`; this.username = ''; this.load(); }, error: error => this.message = error.error?.message ?? 'Dodavanje nije uspelo.' }); }
  removeFriend(id: number) { this.library.removeFriend(id).subscribe({ next: result => { this.message = result.message; this.load(); }, error: error => this.message = error.error?.message ?? 'Uklanjanje nije uspelo.' }); }
}