import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { ModelInfo } from '../../models/models';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="page-container">
      <div class="page-header">
        <h1>⚙️ Settings</h1>
        <p class="page-subtitle">Configure your CareBuddy experience</p>
      </div>

      <!-- Model Selector -->
      <div class="card settings-card">
        <h2>🤖 LLM Model</h2>
        <p class="desc">Switch the active Ollama model. Changes take effect immediately for new conversations.</p>

        <div class="spinner-wrap" *ngIf="loading"><div class="spinner"></div></div>

        <ng-container *ngIf="!loading && modelInfo">
          <div class="model-grid">
            <div
              *ngFor="let model of modelInfo.installed_models"
              class="model-card"
              [class.active]="model === activeModel"
              (click)="switchModel(model)"
            >
              <div class="model-icon">🧠</div>
              <div class="model-name">{{ model }}</div>
              <div class="model-badge" *ngIf="model === activeModel">Active</div>
              <div class="model-switch" *ngIf="model !== activeModel">Use this</div>
            </div>
          </div>

          <div class="success-msg" *ngIf="switchMsg">{{ switchMsg }}</div>

          <div class="pull-hint" *ngIf="modelInfo.configured_models.length > modelInfo.installed_models.length">
            <p>💡 <strong>Pull more models with Ollama:</strong></p>
            <code *ngFor="let m of missingModels">ollama pull {{ m }}</code>
          </div>
        </ng-container>
      </div>

      <!-- Knowledge Base -->
      <div class="card settings-card">
        <h2>📚 Knowledge Base</h2>
        <p class="desc">Medical reference documents loaded into the RAG vector store.</p>
        <div class="kb-stat" *ngIf="kbStats">
          <span class="kb-num">{{ kbStats['total_documents'] }}</span>
          <span>documents indexed in ChromaDB</span>
        </div>
        <p class="desc" *ngIf="!kbStats">Loading stats…</p>
      </div>

      <!-- API Info -->
      <div class="card settings-card">
        <h2>🔗 API Connection</h2>
        <div class="info-row"><span>Backend URL</span><code>http://localhost:8000</code></div>
        <div class="info-row"><span>Ollama URL</span><code>http://localhost:11434</code></div>
        <div class="info-row"><span>API Docs</span>
          <a href="http://localhost:8000/docs" target="_blank" class="link">Swagger UI ↗</a>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .page-header { margin-bottom: 1.75rem; }
    .page-header h1 { font-size: 1.6rem; font-weight: 700; }
    .page-subtitle { color: var(--text-muted); margin-top: .25rem; }
    .settings-card { margin-bottom: 1.5rem; }
    .settings-card h2 { font-size: 1rem; font-weight: 600; margin-bottom: .5rem; }
    .desc { color: var(--text-muted); font-size: .87rem; margin-bottom: 1.25rem; }
    .spinner-wrap { display: flex; padding: 1rem 0; }
    :host { display: block; height: 100%; overflow-y: auto; }

    .model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
    .model-card {
      border: 2px solid var(--border); border-radius: var(--radius); padding: 1.25rem 1rem;
      text-align: center; cursor: pointer; transition: all var(--transition);
    }
    .model-card:hover { border-color: var(--primary); background: rgba(99,102,241,.05); }
    .model-card.active { border-color: var(--primary); background: rgba(99,102,241,.12); }
    .model-icon { font-size: 1.5rem; margin-bottom: .5rem; }
    .model-name { font-size: .85rem; font-weight: 600; margin-bottom: .4rem; word-break: break-all; }
    .model-badge { background: var(--primary); color: #fff; font-size: .72rem; padding: .15rem .5rem; border-radius: 999px; display: inline-block; }
    .model-switch { color: var(--text-muted); font-size: .75rem; }

    .pull-hint { background: var(--bg-input); border-radius: var(--radius-sm); padding: 1rem; margin-top: 1rem; font-size: .85rem; }
    .pull-hint code { display: block; background: var(--bg); padding: .3rem .6rem; border-radius: 4px; margin-top: .4rem; font-family: monospace; color: var(--accent); }

    .kb-stat { display: flex; align-items: baseline; gap: .6rem; font-size: .9rem; }
    .kb-num { font-size: 2rem; font-weight: 700; color: var(--primary); }

    .info-row { display: flex; align-items: center; justify-content: space-between; padding: .65rem 0; border-bottom: 1px solid var(--border); font-size: .88rem; }
    .info-row:last-child { border: none; }
    .info-row code { background: var(--bg-input); padding: .2rem .5rem; border-radius: 4px; font-family: monospace; color: var(--accent); }
    .link { color: var(--primary); text-decoration: none; font-weight: 500; }
    .link:hover { text-decoration: underline; }
  `]
})
export class SettingsComponent implements OnInit {
    modelInfo: ModelInfo | null = null;
    activeModel = '';
    missingModels: string[] = [];
    kbStats: Record<string, unknown> | null = null;
    loading = true;
    switchMsg = '';

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.api.getModels().subscribe({
            next: (info) => {
                this.modelInfo = info;
                this.activeModel = info.active_model;
                this.missingModels = info.configured_models.filter(
                    m => !info.installed_models.some(im => im.startsWith(m))
                );
                this.loading = false;
            },
            error: () => { this.loading = false; }
        });
        this.api.getKnowledgeBaseStats().subscribe({ next: (s) => this.kbStats = s, error: () => { } });
    }

    switchModel(model: string) {
        if (model === this.activeModel) return;
        this.api.switchModel(model).subscribe({
            next: (res) => {
                this.activeModel = res.active_model;
                this.switchMsg = `✅ Switched to ${model}`;
                setTimeout(() => this.switchMsg = '', 3000);
            },
            error: (e) => {
                this.switchMsg = `❌ ${e.error?.detail || 'Failed to switch model'}`;
                setTimeout(() => this.switchMsg = '', 4000);
            }
        });
    }
}
