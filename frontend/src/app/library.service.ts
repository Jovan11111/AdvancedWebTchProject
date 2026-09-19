import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
export interface User { id: number; firstName: string; lastName: string; email: string; username: string; role: string; }
export interface Book { id: number; title: string; author: string; description: string; isbn: string; imageUrl: string; status?: string; }
export interface Friend { id: number; username: string; firstName: string; lastName: string; }
export interface Profile { user: any; readBooks: Book[]; wantedBooks: Book[]; friends: Friend[]; }
@Injectable({ providedIn: 'root' })
export class LibraryService {
  private http = inject(HttpClient); private api = 'http://127.0.0.1:5000/api';
  get user(): User | null { const value = localStorage.getItem('libraryUser'); return value ? JSON.parse(value) : null; }
  set user(value: User | null) { value ? localStorage.setItem('libraryUser', JSON.stringify(value)) : localStorage.removeItem('libraryUser'); }
  private options() { return { headers: new HttpHeaders({ 'X-User-Id': String(this.user?.id ?? '') }) }; }
  login(username: string, password: string) { return this.http.post<{ user: User }>(`${this.api}/login`, { username, password }); }
  register(data: object) { return this.http.post<{ user: User }>(`${this.api}/register`, data); }
  books() { return this.http.get<Book[]>(`${this.api}/books`, this.options()); }
  book(id: number) { return this.http.get<Book>(`${this.api}/books/${id}`, this.options()); }
  updateStatus(id: number, status: string) { return this.http.put(`${this.api}/books/${id}/status`, { status }, this.options()); }
  profile() { return this.http.get<{ user: User; readBooks: Book[]; wantedBooks: Book[] }>(`${this.api}/profile`, this.options()); }
  changePassword(data: object) { return this.http.put<{ message: string }>(`${this.api}/profile/password`, data, this.options()); }
  addBook(data: FormData) { return this.http.post<Book>(`${this.api}/admin/books`, data, this.options()); }
  deleteBook(id: number) { return this.http.delete(`${this.api}/admin/books/${id}`, this.options()); }
  adminUsers() { return this.http.get<User[]>(`${this.api}/admin/users`, this.options()); }
  deleteUser(id: number) { return this.http.delete(`${this.api}/admin/users/${id}`, this.options()); }
  addFriend(username: string) { return this.http.post<{ friend: Friend }>(`${this.api}/friends`, { username }, this.options()); }
  removeFriend(id: number) { return this.http.delete<{ message: string }>(`${this.api}/friends/${id}`, this.options()); }
  friends() { return this.http.get<Friend[]>(`${this.api}/friends`, this.options()); }
  activities() { return this.http.get<{ username: string; bookTitle: string; status: string; updatedAt: string }[]>(`${this.api}/friends/activities`, this.options()); }
  publicProfile(id: number) { return this.http.get<Profile>(`${this.api}/users/${id}/profile`, this.options()); }
}