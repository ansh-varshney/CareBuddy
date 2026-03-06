import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { DashboardStats, URGENCY_LABELS, URGENCY_COLORS } from '../../models/models';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterLink],
    template: `
    <div class="page-container dash-page">
      <div class="page-header">
        <h1>📊 Health Dashboard</h1>
        <p class="page-subtitle">Your health activity overview</p>
      </div>

      <div class="spinner-wrap" *ngIf="loading"><div class="spinner"></div></div>

      <ng-container *ngIf="!loading && stats">
        <!-- Stat cards -->
        <div class="stat-grid">
          <div class="card stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-val">{{ stats.total_conversations }}</div>
            <div class="stat-label">Conversations</div>
          </div>
          <div class="card stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-val">{{ stats.total_symptom_entries }}</div>
            <div class="stat-label">Symptom Entries</div>
          </div>
          <div class="card stat-card" *ngIf="maxUrgency">
            <div class="stat-icon">⚠️</div>
            <div class="stat-val" [style.color]="urgencyColors[maxUrgency]">
              {{ urgencyLabels[maxUrgency] }}
            </div>
            <div class="stat-label">Highest Urgency Recorded</div>
          </div>
        </div>

        <!-- Urgency distribution -->
        <div class="card section-card" *ngIf="hasUrgencyData">
          <h2>Urgency Distribution</h2>
          <div class="urgency-bars">
            <div
              *ngFor="let item of urgencyItems"
              class="urgency-row"
            >
              <span class="urg-label badge badge-{{ item.level }}">{{ urgencyLabels[item.level] }}</span>
              <div class="bar-track">
                <div class="bar-fill" [style.width.%]="item.pct" [style.background]="urgencyColors[item.level]"></div>
              </div>
              <span class="urg-count">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <!-- Recent conversations -->
        <div class="card section-card">
          <div class="section-head">
            <h2>Recent Conversations</h2>
            <a class="btn btn-ghost btn-sm" routerLink="/chat">+ New Chat</a>
          </div>
          <div class="conv-table" *ngIf="stats.recent_conversations.length; else noConv">
            <div class="conv-row" *ngFor="let c of stats.recent_conversations">
              <span class="conv-title">{{ c.title }}</span>
              <span class="badge badge-{{ c.urgency_level }}" *ngIf="c.urgency_level">
                {{ urgencyLabels[c.urgency_level!] }}
              </span>
              <span class="conv-date">{{ c.updated_at | date:'MMM d, HH:mm' }}</span>
            </div>
          </div>
          <ng-template #noConv>
            <p class="empty">No conversations yet. <a routerLink="/chat">Start one!</a></p>
          </ng-template>
        </div>
      </ng-container>
    </div>
  `,
    styles: [`
    .dash-page { overflow-y: auto; }
    .page-header { margin-bottom: 1.75rem; }
    .page-header h1 { font-size: 1.6rem; font-weight: 700; }
    .page-subtitle { color: var(--text-muted); margin-top: .25rem; }
    .spinner-wrap { display: flex; justify-content: center; padding: 3rem; }

    .stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card { text-align: center; padding: 1.75rem 1.25rem; }
    .stat-icon { font-size: 1.75rem; margin-bottom: .6rem; }
    .stat-val { font-size: 2rem; font-weight: 700; color: var(--primary); }
    .stat-label { color: var(--text-muted); font-size: .82rem; margin-top: .25rem; }

    .section-card { margin-bottom: 1.5rem; }
    .section-card h2 { font-size: 1rem; font-weight: 600; margin-bottom: 1.25rem; }
    .section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
    .section-head h2 { margin: 0; }

    .urgency-bars { display: flex; flex-direction: column; gap: .75rem; }
    .urgency-row { display: flex; align-items: center; gap: 1rem; }
    .urg-label { min-width: 90px; }
    .bar-track { flex: 1; height: 8px; background: var(--bg-input); border-radius: 4px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 4px; transition: width .5s ease; }
    .urg-count { min-width: 24px; text-align: right; font-size: .85rem; color: var(--text-muted); }

    .conv-table { display: flex; flex-direction: column; gap: .5rem; }
    .conv-row { display: flex; align-items: center; gap: .75rem; padding: .6rem .75rem; border-radius: var(--radius-sm); background: var(--bg-input); }
    .conv-title { flex: 1; font-size: .88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .conv-date { color: var(--text-muted); font-size: .8rem; white-space: nowrap; }
    .btn-sm { padding: .4rem 1rem; font-size: .85rem; }
    .empty { color: var(--text-muted); font-size: .88rem; }
    .empty a { color: var(--primary); }
  `]
})
export class DashboardComponent implements OnInit {
    stats: DashboardStats | null = null;
    loading = true;
    urgencyLabels = URGENCY_LABELS;
    urgencyColors = URGENCY_COLORS;
    urgencyItems: { level: number; count: number; pct: number }[] = [];
    maxUrgency: number | undefined;
    hasUrgencyData = false;

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.api.getDashboardStats().subscribe({
            next: (s) => {
                this.stats = s;
                this.buildUrgencyChart(s.urgency_distribution);
                this.loading = false;
            },
            error: () => { this.loading = false; }
        });
    }

    buildUrgencyChart(dist: Record<string, number>) {
        const entries = Object.entries(dist).map(([k, v]) => ({ level: +k, count: v }));
        const max = Math.max(...entries.map(e => e.count), 1);
        this.urgencyItems = entries.map(e => ({ ...e, pct: (e.count / max) * 100 }));
        this.hasUrgencyData = entries.length > 0;
        if (entries.length) this.maxUrgency = Math.max(...entries.map(e => e.level));
    }
}
