import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="auth-page">
      <div class="auth-card card fade-in">
        <div class="auth-header">
          <div class="auth-logo">🏥</div>
          <h1>Create account</h1>
          <p class="auth-subtitle">Join CareBuddy — your AI health assistant</p>
        </div>

        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <!-- Account section -->
          <div class="section-label">Account Details</div>
          <div class="field-row">
            <div class="field">
              <label>Email *</label>
              <input class="input" type="email" formControlName="email" placeholder="you@example.com"/>
            </div>
            <div class="field">
              <label>Username *</label>
              <input class="input" formControlName="username" placeholder="Choose a username"/>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Full Name</label>
              <input class="input" formControlName="fullName" placeholder="Your name"/>
            </div>
            <div class="field">
              <label>Password *</label>
              <input class="input" type="password" formControlName="password" placeholder="Min. 6 characters"/>
            </div>
          </div>

          <!-- Medical profile section -->
          <div class="section-label" style="margin-top:1.25rem">
            Medical Profile <span class="opt">(optional — enables personalized AI responses)</span>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Age</label>
              <input class="input" type="number" formControlName="age" placeholder="e.g. 28" min="1" max="120"/>
            </div>
            <div class="field">
              <label>Sex</label>
              <select class="input" formControlName="sex">
                <option value="">Select…</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="field">
              <label>Blood Type</label>
              <select class="input" formControlName="blood_type">
                <option value="">Select…</option>
                <option *ngFor="let bt of bloodTypes" [value]="bt">{{ bt }}</option>
              </select>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Weight (kg)</label>
              <input class="input" type="number" formControlName="weight_kg" placeholder="e.g. 70" min="1" max="500"/>
            </div>
            <div class="field">
              <label>Height (cm)</label>
              <input class="input" type="number" formControlName="height_cm" placeholder="e.g. 170" min="30" max="300"/>
            </div>
          </div>
          <div class="field">
            <label>Medical History / Chronic Conditions</label>
            <textarea class="input" formControlName="medical_history" rows="2"
              placeholder="e.g. Diabetes Type 2, Hypertension, Asthma…"></textarea>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Known Allergies</label>
              <input class="input" formControlName="allergies" placeholder="e.g. Penicillin, Peanuts"/>
            </div>
            <div class="field">
              <label>Current Medications</label>
              <input class="input" formControlName="current_medications" placeholder="e.g. Metformin 500mg daily"/>
            </div>
          </div>

          <div class="error-msg" *ngIf="error">{{ error }}</div>

          <button class="btn btn-primary submit-btn" type="submit" [disabled]="loading || form.invalid">
            <span class="spinner" *ngIf="loading"></span>
            {{ loading ? 'Creating account…' : 'Create Account' }}
          </button>
        </form>

        <p class="auth-footer">
          Have an account? <a routerLink="/login">Sign in</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .auth-page {
      min-height: 100%; overflow-y: auto;
      display: flex; align-items: flex-start; justify-content: center;
      padding: 2rem 1rem;
      background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,.15) 0%, transparent 70%);
    }
    .auth-card { width: 100%; max-width: 700px; padding: 2.5rem; }
    .auth-header { text-align: center; margin-bottom: 1.75rem; }
    .auth-logo { font-size: 2.5rem; margin-bottom: .75rem; }
    h1 { font-size: 1.6rem; font-weight: 700; }
    .auth-subtitle { color: var(--text-muted); margin-top: .25rem; font-size: .88rem; }
    .section-label { font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--primary); margin-bottom: .75rem; }
    .opt { font-weight: 400; text-transform: none; letter-spacing: 0; color: var(--text-muted); }
    .field-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: .75rem; margin-bottom: .75rem; }
    .field { margin-bottom: 0; }
    .field label { display: block; font-size: .82rem; font-weight: 500; color: var(--text-muted); margin-bottom: .3rem; }
    textarea.input { resize: vertical; min-height: 60px; margin-bottom: .75rem; }
    .submit-btn { width: 100%; justify-content: center; margin-top: 1.5rem; padding: .8rem; font-size: 1rem; }
    .auth-footer { text-align: center; margin-top: 1.25rem; font-size: .88rem; color: var(--text-muted); }
    .auth-footer a { color: var(--primary); text-decoration: none; font-weight: 500; }
    .auth-footer a:hover { text-decoration: underline; }
  `]
})
export class RegisterComponent {
  bloodTypes = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];

  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    fullName: [''],
    // Medical profile
    age: [null as number | null],
    sex: [''],
    weight_kg: [null as number | null],
    height_cm: [null as number | null],
    blood_type: [''],
    medical_history: [''],
    allergies: [''],
    current_medications: [''],
  });

  loading = false;
  error = '';

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) { }

  onSubmit() {
    if (this.form.invalid) return;
    this.loading = true; this.error = '';
    const v = this.form.value;
    this.auth.registerWithProfile({
      email: v.email!,
      username: v.username!,
      password: v.password!,
      full_name: v.fullName || undefined,
      age: v.age || undefined,
      sex: v.sex || undefined,
      weight_kg: v.weight_kg || undefined,
      height_cm: v.height_cm || undefined,
      blood_type: v.blood_type || undefined,
      medical_history: v.medical_history || undefined,
      allergies: v.allergies || undefined,
      current_medications: v.current_medications || undefined,
    }).subscribe({
      next: () => this.router.navigate(['/chat']),
      error: (e) => { this.error = e.error?.detail || 'Registration failed'; this.loading = false; },
    });
  }
}
