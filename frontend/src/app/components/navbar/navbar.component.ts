import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  template: `
    <nav class="navbar">
      <a class="brand" routerLink="/chat">
        <span class="brand-icon">🏥</span>
        <span class="brand-name">CareBuddy</span>
      </a>

      <div class="nav-links" *ngIf="auth.isLoggedIn$ | async">
        <a routerLink="/chat"      routerLinkActive="active">💬 Chat</a>
        <a routerLink="/symptoms"  routerLinkActive="active">📋 Symptoms</a>
        <a routerLink="/settings"  routerLinkActive="active">⚙️ Settings</a>
      </div>

      <div class="nav-right">
        <ng-container *ngIf="auth.isLoggedIn$ | async; else loginBtn">
          <span class="username">{{ auth.getUsername() }}</span>
          <button class="btn btn-ghost btn-sm" (click)="auth.logout()">Sign Out</button>
        </ng-container>
        <ng-template #loginBtn>
          <a class="btn btn-primary btn-sm" routerLink="/login">Sign In</a>
        </ng-template>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      display: flex; align-items: center; gap: 1.5rem;
      height: 64px; padding: 0 1.5rem;
      background: var(--bg-card); border-bottom: 1px solid var(--border);
      position: sticky; top: 0; z-index: 100;
    }
    .brand { display: flex; align-items: center; gap: .5rem; text-decoration: none; }
    .brand-icon { font-size: 1.4rem; }
    .brand-name { font-weight: 700; font-size: 1.1rem; color: var(--primary); }
    .nav-links { display: flex; gap: .25rem; flex: 1; }
    .nav-links a {
      padding: .45rem .9rem; border-radius: var(--radius-sm); font-size: .88rem;
      font-weight: 500; color: var(--text-muted); text-decoration: none;
      transition: all var(--transition);
    }
    .nav-links a:hover { color: var(--text); background: var(--bg-input); }
    .nav-links a.active { color: var(--primary); background: rgba(99,102,241,.12); }
    .nav-right { display: flex; align-items: center; gap: .75rem; margin-left: auto; }
    .username { color: var(--text-muted); font-size: .87rem; }
    .btn-sm { padding: .4rem 1rem; font-size: .85rem; }
  `]
})
export class NavbarComponent {
  constructor(public auth: AuthService) { }
}
