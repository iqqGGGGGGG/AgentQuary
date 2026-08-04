import type { UserState } from '../types/quiz'

let userState: UserState = {
  openid: null,
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

export function getOpenid(): string | null {
  return userState.openid
}

export function isLoggedIn(): boolean {
  return userState.isLoggedIn
}
