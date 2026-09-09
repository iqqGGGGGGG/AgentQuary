export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/quiz/quiz',
    'pages/report/report',
    'pages/history/history',
    'pages/profile/profile',
    'pages/wrong-book/wrong-book',
    'pages/preferences/preferences',
    'pages/achievements/achievements',
  ],
  tabBar: {
    color: '#8B7FA3',
    selectedColor: '#7C5CFC',
    backgroundColor: '#FFFFFF',
    borderStyle: 'white',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'assets/tab-icons/home.png',
        selectedIconPath: 'assets/tab-icons/home-active.png',
      },
      {
        pagePath: 'pages/history/history',
        text: '记录',
        iconPath: 'assets/tab-icons/history.png',
        selectedIconPath: 'assets/tab-icons/history-active.png',
      },
      {
        pagePath: 'pages/profile/profile',
        text: '我的',
        iconPath: 'assets/tab-icons/profile.png',
        selectedIconPath: 'assets/tab-icons/profile-active.png',
      },
    ],
  },
  window: {
    navigationBarTitleText: '知识闯关',
    navigationBarBackgroundColor: '#7C5CFC',
    navigationBarTextStyle: 'white',
    backgroundColor: '#FBF7F0',
  },
})
