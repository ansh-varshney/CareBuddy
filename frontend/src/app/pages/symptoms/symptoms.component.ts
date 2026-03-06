import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { SymptomEntry } from '../../models/models';

@Component({
    selector: 'app-symptoms',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    template: `
    <div class="page-container symptoms-page">
      <div class="page-header">
        <h1>📋 Symptom Journal</h1>
        <p class="page-subtitle">Track your symptoms over time</p>
      </div>

      <div class="layout">
        <!-- Add form -->
        <div class="card add-card">
          <h2>Log Symptoms</h2>
          <form [formGroup]="form" (ngSubmit)="addEntry()">
            <div class="field">
              <label>Description</label>
              <textarea class="input" formControlName="description" rows="3" placeholder="Describe how you're feeling…"></textarea>
            </div>
            <div class="field">
              <label>Severity (1–10)</label>
              <input class="input" type="number" formControlName="severity" min="1" max="10" placeholder="e.g. 5"/>
            </div>
            <div class="field">
              <label>Body Area <span class="opt">(optional)</span></label>
              <input class="input" formControlName="body_area" placeholder="e.g. head, chest, abdomen"/>
            </div>
            <div class="field" *ngIf="extractedSymptoms.length">
              <label>Extracted Symptoms</label>
              <div class="tags">
                <span class="tag" *ngFor="let s of extractedSymptoms">{{ s }}</span>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-ghost" (click)="extractSymptoms()" [disabled]="extracting || !form.get('description')?.value">
                <span class="spinner" *ngIf="extracting"></span>
                {{ extracting ? 'Extracting…' : '🔍 Extract Symptoms' }}
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="saving">
                <span class="spinner" *ngIf="saving"></span>
                {{ saving ? 'Saving…' : '+ Log Entry' }}
              </button>
            </div>
            <div class="success-msg" *ngIf="successMsg">{{ successMsg }}</div>
          </form>
        </div>

        <!-- Entries list -->
        <div class="entries-list">
          <div class="spinner-wrap" *ngIf="loading"><div class="spinner"></div></div>

          <div *ngIf="!loading && entries.length === 0" class="empty-state card">
            <p>No symptom entries yet. Log your first one!</p>
          </div>

          <div class="card entry-card fade-in" *ngFor="let e of entries">
            <div class="entry-head">
              <div class="entry-tags">
                <span class="tag" *ngFor="let s of e.symptoms">{{ s }}</span>
              </div>
              <button class="btn btn-danger btn-xs" (click)="deleteEntry(e.id)">✕</button>
            </div>
            <p class="entry-desc" *ngIf="e.description">{{ e.description }}</p>
            <div class="entry-meta">
              <span *ngIf="e.severity">Severity: <strong>{{ e.severity }}/10</strong></span>
              <span *ngIf="e.body_area">Area: <strong>{{ e.body_area }}</strong></span>
              <span *ngIf="e.urgency_assessed" class="badge badge-{{ e.urgency_assessed }}">
                AI Urgency: {{ e.urgency_assessed }}/5
              </span>
              <span class="entry-date">{{ e.created_at | date:'MMM d, HH:mm' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .symptoms-page { overflow-y: auto; }
    .page-header { margin-bottom: 1.75rem; }
    .page-header h1 { font-size: 1.6rem; font-weight: 700; }
    .page-subtitle { color: var(--text-muted); margin-top: .25rem; }

    .layout { display: grid; grid-template-columns: 340px 1fr; gap: 1.5rem; }
    @media (max-width: 768px) { .layout { grid-template-columns: 1fr; } }

    .add-card h2 { font-size: 1rem; font-weight: 600; margin-bottom: 1.25rem; }
    .field { margin-bottom: 1rem; }
    .field label { display: block; font-size: .83rem; font-weight: 500; color: var(--text-muted); margin-bottom: .35rem; }
    .opt { font-weight: 400; font-style: italic; }
    .form-actions { display: flex; gap: .75rem; margin-top: 1.25rem; }
    .form-actions .btn { flex: 1; justify-content: center; }

    .tags { display: flex; flex-wrap: wrap; gap: .4rem; }
    .tag { background: rgba(99,102,241,.15); color: var(--primary); padding: .2rem .6rem; border-radius: 999px; font-size: .78rem; font-weight: 500; }

    .spinner-wrap { display: flex; justify-content: center; padding: 2rem; }
    .empty-state { text-align: center; color: var(--text-muted); padding: 2rem; }

    .entries-list { display: flex; flex-direction: column; gap: 1rem; }
    .entry-card { padding: 1.1rem 1.25rem; }
    .entry-head { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; margin-bottom: .6rem; }
    .entry-desc { font-size: .88rem; color: var(--text-muted); margin-bottom: .6rem; line-height: 1.5; }
    .entry-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; font-size: .8rem; color: var(--text-muted); }
    .entry-date { margin-left: auto; }
    .btn-xs { padding: .25rem .55rem; font-size: .75rem; }
  `]
})
export class SymptomsComponent implements OnInit {
    form = this.fb.group({
        description: ['', Validators.required],
        severity: [null as number | null, [Validators.min(1), Validators.max(10)]],
        body_area: [''],
    });
    entries: SymptomEntry[] = [];
    extractedSymptoms: string[] = [];
    loading = true;
    saving = false;
    extracting = false;
    successMsg = '';

    constructor(private fb: FormBuilder, private api: ApiService) { }

    ngOnInit() { this.loadEntries(); }

    loadEntries() {
        this.api.listSymptomEntries().subscribe({
            next: (e) => { this.entries = e; this.loading = false; },
            error: () => { this.loading = false; }
        });
    }

    extractSymptoms() {
        const text = this.form.get('description')?.value;
        if (!text) return;
        this.extracting = true;
        this.api.extractSymptoms(text).subscribe({
            next: (res) => { this.extractedSymptoms = res.symptoms; this.extracting = false; },
            error: () => { this.extracting = false; }
        });
    }

    addEntry() {
        if (this.form.invalid) return;
        this.saving = true;
        const { description, severity, body_area } = this.form.value;
        this.api.createSymptomEntry({
            symptoms: this.extractedSymptoms.length ? this.extractedSymptoms : ['general symptom'],
            description: description || undefined,
            severity: severity || undefined,
            body_area: body_area || undefined,
        }).subscribe({
            next: (entry) => {
                this.entries.unshift(entry);
                this.form.reset();
                this.extractedSymptoms = [];
                this.saving = false;
                this.successMsg = 'Entry logged!';
                setTimeout(() => this.successMsg = '', 3000);
            },
            error: () => { this.saving = false; }
        });
    }

    deleteEntry(id: string) {
        this.api.deleteSymptomEntry(id).subscribe(() => {
            this.entries = this.entries.filter(e => e.id !== id);
        });
    }
}
