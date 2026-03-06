import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, RouterLink],
    template: `
    <div class="auth-page">
      <div class="auth-card card fade-in">
        <div class="auth-header">
          <div class="auth-logo">🏥</div>
          <h1>Welcome back</h1>
          <p class="auth-subtitle">Sign in to CareBuddy</p>
        </div>

        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <div class="field">
            <label>Username</label>
            <input class="input" formControlName="username" placeholder="Enter username" autocomplete="username"/>
          </div>
          <div class="field">
            <label>Password</label>
            <input class="input" type="password" formControlName="password" placeholder="••••••••" autocomplete="current-password"/>
          </div>

          <div class="error-msg" *ngIf="error">{{ error }}</div>

          <button class="btn btn-primary submit-btn" type="submit" [disabled]="loading || form.invalid">
            <span class="spinner" *ngIf="loading"></span>
            {{ loading ? 'Signing in…' : 'Sign In' }}
          </button>
        </form>

        <p class="auth-footer">
          No account? <a routerLink="/register">Create one</a>
        </p>
      </div>
    </div>
  `,
    styles: [`
    .auth-page {
      min-height: 100%; display: flex; align-items: center; justify-content: center;
      background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,.15) 0%, transparent 70%);
    }
    .auth-card { width: 100%; max-width: 420px; padding: 2.5rem; }
    .auth-header { text-align: center; margin-bottom: 2rem; }
    .auth-logo { font-size: 2.5rem; margin-bottom: .75rem; }
    h1 { font-size: 1.6rem; font-weight: 700; }
    .auth-subtitle { color: var(--text-muted); margin-top: .25rem; }
    .field { margin-bottom: 1.2rem; }
    .field label { display: block; font-size: .85rem; font-weight: 500; margin-bottom: .4rem; color: var(--text-muted); }
    .submit-btn { width: 100%; justify-content: center; margin-top: 1.5rem; padding: .8rem; font-size: 1rem; }
    .auth-footer { text-align: center; margin-top: 1.5rem; font-size: .88rem; color: var(--text-muted); }
    .auth-footer a { color: var(--primary); text-decoration: none; font-weight: 500; }
    .auth-footer a:hover { text-decoration: underline; }
  `]
})
export class LoginComponent {
    form = this.fb.group({
        username: ['', Validators.required],
        password: ['', [Validators.required, Validators.minLength(6)]],
    });
    loading = false;
    error = '';

    constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) { }

    onSubmit() {
        if (this.form.invalid) return;
        this.loading = true; this.error = '';
        const { username, password } = this.form.value;
        this.auth.login(username!, password!).subscribe({
            next: () => this.router.navigate(['/chat']),
            error: (e) => { this.error = e.error?.detail || 'Login failed'; this.loading = false; },
        });
    }
}
