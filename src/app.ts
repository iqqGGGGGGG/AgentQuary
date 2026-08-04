import { PropsWithChildren } from 'react'
import Taro, { useLaunch } from '@tarojs/taro'
import { api } from './services/api'
import { setUserState } from './store/user'
import './app.scss'

function App({ children }: PropsWithChildren) {
  useLaunch(() => {
    Taro.login({
      success(loginRes) {
        if (loginRes.code) {
          api.login(loginRes.code).then(res => {
            setUserState({
              openid: res.openid,
              nickname: res.nickname,
              avatar_url: res.avatar_url,
              isLoggedIn: true,
            })
            Taro.setStorageSync('user_openid', res.openid)
          }).catch(err => {
            console.warn('Login failed:', err)
          })
        }
      },
      fail(err) {
        console.warn('wx.login failed:', err)
      },
    })
  })

  return children
}

export default App
