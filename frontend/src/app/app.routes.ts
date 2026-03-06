import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './guards/auth.guard';

export const routes: Routes = [
    { path: '', redirectTo: 'chat', pathMatch: 'full' },
    {
        path: 'login',
        canActivate: [guestGuard],
        loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent),
    },
    {
        path: 'register',
        canActivate: [guestGuard],
        loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent),
    },
    {
        path: 'chat',
        canActivate: [authGuard],
        loadComponent: () => import('./pages/chat/chat.component').then(m => m.ChatComponent),
    },
    {
        path: 'symptoms',
        canActivate: [authGuard],
        loadComponent: () => import('./pages/symptoms/symptoms.component').then(m => m.SymptomsComponent),
    },
    {
        path: 'settings',
        canActivate: [authGuard],
        loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent),
    },
    { path: '**', redirectTo: 'chat' },
];
