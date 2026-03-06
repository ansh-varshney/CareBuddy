import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { TokenResponse, User } from '../models/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
    private readonly TOKEN_KEY = 'carebuddy_token';
    private readonly USER_KEY = 'carebuddy_user';

    private _isLoggedIn$ = new BehaviorSubject<boolean>(this.hasToken());
    isLoggedIn$ = this._isLoggedIn$.asObservable();

    constructor(private http: HttpClient, private router: Router) { }

    register(email: string, username: string, password: string, fullName?: string): Observable<TokenResponse> {
        return this.http.post<TokenResponse>(`${environment.apiUrl}/api/auth/register`, {
            email, username, password, full_name: fullName
        }).pipe(tap(res => this.storeToken(res)));
    }

    registerWithProfile(data: Record<string, unknown>): Observable<TokenResponse> {
        return this.http.post<TokenResponse>(`${environment.apiUrl}/api/auth/register`, data)
            .pipe(tap(res => this.storeToken(res as TokenResponse)));
    }

    login(username: string, password: string): Observable<TokenResponse> {
        const form = new FormData();
        form.append('username', username);
        form.append('password', password);
        return this.http.post<TokenResponse>(`${environment.apiUrl}/api/auth/login`, form)
            .pipe(tap(res => this.storeToken(res)));
    }

    logout(): void {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        this._isLoggedIn$.next(false);
        this.router.navigate(['/login']);
    }

    getToken(): string | null {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    getUsername(): string | null {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user).username : null;
    }

    getProfile(): Observable<User> {
        return this.http.get<User>(`${environment.apiUrl}/api/auth/me`);
    }

    private hasToken(): boolean {
        return !!localStorage.getItem(this.TOKEN_KEY);
    }

    private storeToken(res: TokenResponse): void {
        localStorage.setItem(this.TOKEN_KEY, res.access_token);
        localStorage.setItem(this.USER_KEY, JSON.stringify({ username: res.username }));
        this._isLoggedIn$.next(true);
    }
}
