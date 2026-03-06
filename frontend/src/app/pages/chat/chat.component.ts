import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { ApiService } from '../../services/api.service';
import { Conversation, URGENCY_LABELS } from '../../models/models';

interface DisplayMessage {
  role: 'user' | 'assistant';
  content: string;
  streaming?: boolean;
  urgency?: number;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="chat-layout">

      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">Conversations</span>
          <button class="btn btn-primary btn-xs" (click)="newConversation()">+ New</button>
        </div>
        <div class="conversation-list">
          <div
            *ngFor="let conv of conversations"
            class="conv-item"
            [class.active]="conv.id === conversationId"
            (click)="loadConversation(conv.id)"
          >
            <span class="conv-title">{{ conv.title }}</span>
            <span *ngIf="conv.urgency_level" class="badge badge-{{ conv.urgency_level }}">
              {{ urgencyLabels[conv.urgency_level] }}
            </span>
          </div>
          <p class="empty-hint" *ngIf="conversations.length === 0">No conversations yet</p>
        </div>
      </aside>

      <!-- Main chat area -->
      <div class="chat-main">

        <!-- Chat header -->
        <div class="chat-header">
          <div class="chat-info">
            <h2>{{ currentTitle }}</h2>
            <span class="badge badge-{{ currentUrgency }}" *ngIf="currentUrgency">
              Urgency: {{ urgencyLabels[currentUrgency] }}
            </span>
          </div>
          <div class="model-selector">
            <label>Model</label>
            <select (change)="onModelChange($event)" [value]="activeModel">
              <option *ngFor="let m of availableModels" [value]="m">{{ m }}</option>
            </select>
          </div>
        </div>

        <!-- Messages -->
        <div class="messages-area" #messagesContainer>
          <div class="welcome" *ngIf="messages.length === 0 && !loading">
            <div class="welcome-icon">🏥</div>
            <h3>Hi, I'm CareBuddy</h3>
            <p>Describe your symptoms or ask a health question to get started.</p>
            <div class="chips">
              <button class="chip" (click)="sendChip('I have a headache and mild fever')">🤒 Headache + Fever</button>
              <button class="chip" (click)="sendChip('I have been feeling very tired lately')">😴 Fatigue</button>
              <button class="chip" (click)="sendChip('My back has been hurting for 3 days')">🚶 Back Pain</button>
            </div>
          </div>

          <div *ngFor="let msg of messages" class="msg-wrapper {{ msg.role }} fade-in">
            <div class="msg-bubble">
              <div class="msg-content" [innerHTML]="formatMessage(msg.content)"></div>
              <span *ngIf="msg.urgency && msg.urgency > 0" class="msg-urgency badge badge-{{ msg.urgency }}">
                {{ urgencyLabels[msg.urgency] }} urgency
              </span>
            </div>
            <div class="msg-avatar">{{ msg.role === 'user' ? '👤' : '🏥' }}</div>
          </div>

          <div class="msg-wrapper assistant fade-in" *ngIf="streamingMsg">
            <div class="msg-bubble">
              <div class="msg-content">{{ streamingMsg }}<span class="cursor pulse">▌</span></div>
            </div>
            <div class="msg-avatar">🏥</div>
          </div>

          <div class="typing-indicator" *ngIf="loading && !streamingMsg">
            <span></span><span></span><span></span>
          </div>
        </div>

        <!-- Input area -->
        <div class="input-area">
          <textarea
            class="input chat-input"
            [formControl]="msgControl"
            placeholder="Describe your symptoms or ask a health question…"
            rows="2"
            (keydown.enter)="onEnter($any($event))"
          ></textarea>
          <button class="btn btn-stop" *ngIf="loading" (click)="stopGeneration()" title="Stop generating">
            ⏹ Stop
          </button>
          <button class="btn btn-primary send-btn" *ngIf="!loading" (click)="send()" [disabled]="msgControl.invalid">
            Send ↑
          </button>
        </div>
        <p class="disclaimer">⚕️ CareBuddy is an AI assistant and not a substitute for professional medical advice.</p>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; overflow: hidden; }
    .chat-layout { display: flex; height: 100%; }

    /* Sidebar */
    .sidebar { width: 260px; background: var(--bg-card); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
    .sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem; border-bottom: 1px solid var(--border); }
    .sidebar-title { font-weight: 600; font-size: .9rem; }
    .btn-xs { padding: .3rem .75rem; font-size: .8rem; }
    .conversation-list { flex: 1; overflow-y: auto; padding: .5rem; }
    .conv-item { padding: .65rem .85rem; border-radius: var(--radius-sm); cursor: pointer; margin-bottom: .25rem; transition: background var(--transition); }
    .conv-item:hover { background: var(--bg-input); }
    .conv-item.active { background: rgba(99,102,241,.15); }
    .conv-title { display: block; font-size: .85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .empty-hint { color: var(--text-muted); font-size: .82rem; text-align: center; padding: 1rem; }

    /* Chat main */
    .chat-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .chat-header { display: flex; align-items: center; padding: .85rem 1.25rem; border-bottom: 1px solid var(--border); background: var(--bg-card); gap: 1rem; }
    .chat-info { flex: 1; }
    .chat-info h2 { font-size: 1rem; font-weight: 600; }
    .model-selector { display: flex; align-items: center; gap: .5rem; font-size: .85rem; color: var(--text-muted); }
    .model-selector select { background: var(--bg-input); border: 1px solid var(--border); color: var(--text); padding: .35rem .6rem; border-radius: var(--radius-sm); font-size: .85rem; cursor: pointer; }

    /* Messages */
    .messages-area { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
    .welcome { text-align: center; margin: auto; max-width: 400px; }
    .welcome-icon { font-size: 3rem; margin-bottom: 1rem; }
    .welcome h3 { font-size: 1.3rem; font-weight: 600; margin-bottom: .5rem; }
    .welcome p { color: var(--text-muted); font-size: .9rem; }
    .chips { display: flex; flex-wrap: wrap; gap: .5rem; justify-content: center; margin-top: 1.25rem; }
    .chip { background: var(--bg-card); border: 1px solid var(--border); color: var(--text); padding: .45rem 1rem; border-radius: 999px; cursor: pointer; font-size: .82rem; transition: all var(--transition); }
    .chip:hover { border-color: var(--primary); color: var(--primary); }

    .msg-wrapper { display: flex; align-items: flex-end; gap: .6rem; }
    .msg-wrapper.user { flex-direction: row-reverse; }
    .msg-bubble { max-width: 72%; }
    .user .msg-bubble { background: var(--primary); border-radius: 18px 18px 4px 18px; padding: .75rem 1rem; }
    .assistant .msg-bubble { background: var(--bg-card); border: 1px solid var(--border); border-radius: 18px 18px 18px 4px; padding: .75rem 1rem; }
    .msg-content { font-size: .9rem; line-height: 1.65; white-space: pre-wrap; word-break: break-word; }
    .msg-avatar { font-size: 1.3rem; flex-shrink: 0; }
    .msg-urgency { margin-top: .5rem; display: inline-block; }
    .cursor { user-select: none; }

    .typing-indicator { display: flex; gap: 5px; padding: .5rem; }
    .typing-indicator span { width: 8px; height: 8px; background: var(--text-muted); border-radius: 50%; animation: bounce 1.4s ease-in-out infinite; }
    .typing-indicator span:nth-child(2) { animation-delay: .2s; }
    .typing-indicator span:nth-child(3) { animation-delay: .4s; }
    @keyframes bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }

    /* Input */
    .input-area { display: flex; gap: .75rem; padding: 1rem 1.25rem; border-top: 1px solid var(--border); background: var(--bg-card); align-items: flex-end; }
    .chat-input { flex: 1; resize: none; min-height: 54px; max-height: 120px; }
    .send-btn { padding: .65rem 1.4rem; white-space: nowrap; }
    .btn-stop {
      background: rgba(239,68,68,.15); color: var(--danger); border: 1px solid var(--danger);
      padding: .65rem 1.2rem; border-radius: var(--radius-sm); font-size: .9rem; font-weight: 600;
      cursor: pointer; white-space: nowrap; transition: all var(--transition);
    }
    .btn-stop:hover { background: var(--danger); color: #fff; }
    .disclaimer { text-align: center; font-size: .72rem; color: var(--text-muted); padding: .3rem 1rem .6rem; }
  `]
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer') private msgContainer!: ElementRef;

  messages: DisplayMessage[] = [];
  streamingMsg = '';
  loading = false;
  conversationId = '';
  currentTitle = 'New Conversation';
  currentUrgency: number | undefined;
  conversations: Conversation[] = [];
  availableModels: string[] = ['llama3'];
  activeModel = 'llama3';

  msgControl = new FormControl('', [Validators.required, Validators.minLength(2)]);
  urgencyLabels = URGENCY_LABELS;

  private streamSub?: Subscription;
  private shouldScroll = false;

  constructor(
    private chatService: ChatService,
    private apiService: ApiService,
    private route: ActivatedRoute,
    private router: Router,
  ) { }

  ngOnInit() {
    this.loadModels();
    this.loadConversations();
    this.newConversation();
  }

  ngOnDestroy() {
    this.streamSub?.unsubscribe();
    this.chatService.disconnectStream();
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  loadModels() {
    this.apiService.getModels().subscribe({
      next: (info) => {
        this.availableModels = info.installed_models.length ? info.installed_models : info.configured_models;
        this.activeModel = info.active_model;
      },
      error: () => { }
    });
  }

  loadConversations() {
    this.chatService.listConversations().subscribe({
      next: (convs) => this.conversations = convs,
      error: () => { }
    });
  }

  newConversation() {
    this.conversationId = this.generateId();
    this.messages = [];
    this.currentTitle = 'New Conversation';
    this.currentUrgency = undefined;
    this.streamingMsg = '';
    this.chatService.disconnectStream();
    this.chatService.connectStream(this.conversationId);
    this.subscribeToStream();
  }

  loadConversation(id: string) {
    this.chatService.getConversation(id).subscribe(conv => {
      this.conversationId = id;
      this.currentTitle = conv.title;
      this.currentUrgency = conv.urgency_level;
      this.messages = (conv.messages || []).map(m => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: m.content,
        urgency: (m.metadata as Record<string, number>)?.['urgency_level'],
      }));
      this.shouldScroll = true;
      this.chatService.disconnectStream();
      this.chatService.connectStream(id);
      this.subscribeToStream();
    });
  }

  subscribeToStream() {
    this.streamSub?.unsubscribe();
    this.streamSub = this.chatService.stream$.subscribe(chunk => {
      if (chunk.type === 'title') {
        // Backend sent the AI-generated title for this conversation
        this.currentTitle = chunk.content || 'New Conversation';
        this.loadConversations(); // Refresh sidebar
      } else if (chunk.type === 'chunk') {
        this.streamingMsg += chunk.content;
        this.shouldScroll = true;
      } else if (chunk.type === 'done') {
        if (this.streamingMsg) {
          this.messages.push({ role: 'assistant', content: this.streamingMsg });
          this.streamingMsg = '';
        }
        this.loading = false;
        this.shouldScroll = true;
        this.loadConversations();
      } else if (chunk.type === 'error') {
        this.loading = false;
        this.streamingMsg = '';
      }
    });
  }


  send() {
    const msg = this.msgControl.value?.trim();
    if (!msg || this.loading) return;

    this.messages.push({ role: 'user', content: msg });
    this.msgControl.reset();
    this.loading = true;
    this.streamingMsg = '';
    this.shouldScroll = true;

    if (this.chatService.isStreamConnected()) {
      this.chatService.sendStreamMessage(msg, this.activeModel);
    } else {
      // Fallback to REST
      this.chatService.sendMessage(msg, this.conversationId, this.activeModel).subscribe({
        next: (res) => {
          this.messages.push({ role: 'assistant', content: res.response, urgency: res.urgency_level || undefined });
          this.loading = false;
          this.currentUrgency = res.urgency_level || undefined;
          this.shouldScroll = true;
          this.loadConversations();
        },
        error: () => { this.loading = false; }
      });
    }
  }

  stopGeneration() {
    // Append whatever has been streamed so far as a complete message
    if (this.streamingMsg) {
      this.messages.push({
        role: 'assistant',
        content: this.streamingMsg + ' \n\n*[Generation stopped]*',
      });
      this.streamingMsg = '';
    }
    this.loading = false;
    // Reconnect WS for next message
    this.chatService.disconnectStream();
    this.chatService.connectStream(this.conversationId);
    this.subscribeToStream();
    this.shouldScroll = true;
  }

  sendChip(text: string) {
    this.msgControl.setValue(text);
    this.send();
  }

  onEnter(event: KeyboardEvent) {
    if (!event.shiftKey) { event.preventDefault(); this.send(); }
  }

  onModelChange(event: Event) {
    const model = (event.target as HTMLSelectElement).value;
    this.apiService.switchModel(model).subscribe({
      next: (res) => this.activeModel = res.active_model,
      error: () => { }
    });
  }

  formatMessage(content: string): string {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  private scrollToBottom() {
    try {
      const el = this.msgContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    } catch { /* scroll target not yet available */ }
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).slice(2);
  }
}
