import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../environments/environment';
import {
    ChatResponse, Conversation, WsChunk
} from '../models/models';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class ChatService {
    private ws: WebSocket | null = null;
    private _stream$ = new Subject<WsChunk>();
    stream$ = this._stream$.asObservable();

    constructor(private http: HttpClient, private auth: AuthService) { }

    // ── REST (non-streaming) ────────────────────────────────
    sendMessage(message: string, conversationId?: string, model?: string): Observable<ChatResponse> {
        return this.http.post<ChatResponse>(`${environment.apiUrl}/api/chat/`, {
            message,
            ...(conversationId && { conversation_id: conversationId }),
            ...(model && { model }),
        });
    }

    // ── WebSocket (streaming) ───────────────────────────────
    connectStream(conversationId: string): void {
        if (this.ws) this.disconnectStream();
        const token = this.auth.getToken();
        const url = `${environment.wsUrl}/api/chat/ws/${conversationId}${token ? `?token=${token}` : ''}`;
        this.ws = new WebSocket(url);

        this.ws.onmessage = (event) => {
            const chunk: WsChunk = JSON.parse(event.data);
            this._stream$.next(chunk);
        };

        this.ws.onerror = () => {
            this._stream$.next({ type: 'error', content: 'WebSocket error' });
        };

        this.ws.onclose = () => {
            this.ws = null;
        };
    }

    sendStreamMessage(message: string, model?: string): void {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ message, ...(model && { model }) }));
        }
    }

    disconnectStream(): void {
        this.ws?.close();
        this.ws = null;
    }

    isStreamConnected(): boolean {
        return this.ws?.readyState === WebSocket.OPEN;
    }

    // ── Conversation management ─────────────────────────────
    listConversations(): Observable<Conversation[]> {
        return this.http.get<Conversation[]>(`${environment.apiUrl}/api/chat/conversations`);
    }

    getConversation(id: string): Observable<Conversation> {
        return this.http.get<Conversation>(`${environment.apiUrl}/api/chat/conversations/${id}`);
    }

    runTriage(conversationId: string): Observable<unknown> {
        return this.http.post(`${environment.apiUrl}/api/chat/conversations/${conversationId}/triage`, {});
    }
}
