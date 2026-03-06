import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
    DashboardStats, ModelInfo, SymptomEntry, SymptomEntryCreate, HealthStatus
} from '../models/models';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private base = environment.apiUrl;

    constructor(private http: HttpClient) { }

    // ── Health ────────────────────────────────────────────
    getHealth(): Observable<HealthStatus> {
        return this.http.get<HealthStatus>(`${this.base}/health`);
    }

    // ── Dashboard ─────────────────────────────────────────
    getDashboardStats(): Observable<DashboardStats> {
        return this.http.get<DashboardStats>(`${this.base}/api/dashboard/stats`);
    }

    // ── Symptoms ──────────────────────────────────────────
    createSymptomEntry(entry: SymptomEntryCreate): Observable<SymptomEntry> {
        return this.http.post<SymptomEntry>(`${this.base}/api/symptoms/`, entry);
    }

    listSymptomEntries(limit = 50, offset = 0): Observable<SymptomEntry[]> {
        return this.http.get<SymptomEntry[]>(`${this.base}/api/symptoms/?limit=${limit}&offset=${offset}`);
    }

    deleteSymptomEntry(id: string): Observable<void> {
        return this.http.delete<void>(`${this.base}/api/symptoms/${id}`);
    }

    extractSymptoms(text: string): Observable<{ symptoms: string[] }> {
        return this.http.post<{ symptoms: string[] }>(`${this.base}/api/symptoms/extract`, { text });
    }

    // ── Settings / Models ─────────────────────────────────
    getModels(): Observable<ModelInfo> {
        return this.http.get<ModelInfo>(`${this.base}/api/settings/models`);
    }

    switchModel(modelName: string): Observable<{ active_model: string }> {
        return this.http.put<{ active_model: string }>(`${this.base}/api/settings/models`, { model_name: modelName });
    }

    getKnowledgeBaseStats(): Observable<Record<string, unknown>> {
        return this.http.get<Record<string, unknown>>(`${this.base}/api/settings/knowledge-base`);
    }
}
