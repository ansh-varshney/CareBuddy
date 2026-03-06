// TypeScript interfaces for CareBuddy API models

export interface User {
    id: string;
    email: string;
    username: string;
    full_name?: string;
    created_at: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    username: string;
}

export interface ChatRequest {
    message: string;
    conversation_id?: string;
    model?: string;
}

export interface ChatResponse {
    response: string;
    conversation_id: string;
    model_used: string;
    urgency_level?: number;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    metadata?: Record<string, unknown>;
    created_at: string;
}

export interface Conversation {
    id: string;
    title: string;
    model_used: string;
    urgency_level?: number;
    created_at: string;
    updated_at: string;
    message_count?: number;
    messages?: Message[];
}

export interface SymptomEntry {
    id: string;
    symptoms: string[];
    description?: string;
    severity?: number;
    urgency_assessed?: number;
    body_area?: string;
    recommendation?: string;
    created_at: string;
}

export interface SymptomEntryCreate {
    symptoms: string[];
    description?: string;
    severity?: number;
    body_area?: string;
}

export interface DashboardStats {
    total_conversations: number;
    total_symptom_entries: number;
    urgency_distribution: Record<string, number>;
    recent_conversations: Partial<Conversation>[];
}

export interface ModelInfo {
    active_model: string;
    configured_models: string[];
    installed_models: string[];
}

export interface HealthStatus {
    status: string;
    service: string;
    version: string;
    ollama: {
        status: string;
        available_models: string[];
    };
}

export interface TriageResult {
    symptoms_identified: string[];
    urgency_level: number;
    urgency_reasoning: string;
    recommended_action: string;
    specialist_type?: string;
    follow_up_questions: string[];
    key_concerns: string[];
}

export interface WsChunk {
    type: 'chunk' | 'done' | 'error' | 'title';
    content?: string;
}

export const URGENCY_LABELS: Record<number, string> = {
    1: 'Low',
    2: 'Mild',
    3: 'Moderate',
    4: 'High',
    5: 'Emergency',
};

export const URGENCY_COLORS: Record<number, string> = {
    1: '#22c55e',
    2: '#84cc16',
    3: '#f59e0b',
    4: '#ef4444',
    5: '#7f1d1d',
};
