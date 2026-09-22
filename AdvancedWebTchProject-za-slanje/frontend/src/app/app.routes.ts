import { Routes } from '@angular/router';
import { LoginComponent } from './login.component';
import { RegisterComponent } from './register.component';
import { BooksComponent } from './books.component';
import { BookDetailsComponent } from './book-details.component';
import { ProfileComponent } from './profile.component';
import { AdminComponent } from './admin.component';
import { FriendsComponent } from './friends.component';
import { PublicProfileComponent } from './public-profile.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
	{ path: '', redirectTo: 'books', pathMatch: 'full' },
	{ path: 'login', component: LoginComponent },
	{ path: 'register', component: RegisterComponent },
	{ path: 'books', component: BooksComponent, canActivate: [authGuard] },
	{ path: 'books/:id', component: BookDetailsComponent, canActivate: [authGuard] },
	{ path: 'profile', component: ProfileComponent, canActivate: [authGuard] },
	{ path: 'profile/user/:id', component: PublicProfileComponent, canActivate: [authGuard] },
	{ path: 'friends', component: FriendsComponent, canActivate: [authGuard] },
	{ path: 'admin', component: AdminComponent, canActivate: [authGuard] },
	{ path: '**', redirectTo: 'books' },
];
