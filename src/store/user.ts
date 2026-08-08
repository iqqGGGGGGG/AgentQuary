import type { UserState } from '../types/quiz'

let userState: UserState = {
  openid: null,
  access_token: null,
  nickname: '知识探索者',
  avatar_url: null,
  isLoggedIn: false,
}

export function getUserState(): UserState {
  return userState
}

export function setUserState(state: Partial<UserState>) {
  userState = { ...userState, ...state }
}

export function getAccessToken(): string | null {
  return userState.access_token
}

export function isLoggedIn(): boolean {
  return userState.isLoggedIn
}
