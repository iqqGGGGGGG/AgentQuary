const http = require('http')

const examples = [
  { id: 1, title: '十分钟搞懂三国人物关系', category: '历史', description: '人物关系一网打尽' },
  { id: 2, title: '太阳系的八大行星', category: '科学', description: '基础天文速览' },
  { id: 3, title: '常见心理学效应', category: '心理', description: '看完更懂自己' },
  { id: 4, title: '从种子到一杯咖啡', category: '生活', description: '咖啡入门必修' },
]

const questions = [
  { id: 1, type: 'single_choice', question: '太阳系中体积最大的行星是哪一颗？', options: ['地球', '火星', '木星', '金星'], answer: 2, explanation: '木星的体积和质量都是太阳系行星中最大的。' },
  { id: 2, type: 'true_false', question: '太阳是太阳系唯一的恒星。', options: ['正确', '错误'], answer: 0, explanation: '太阳是太阳系中心，也是该系统唯一的恒星。' },
  { id: 3, type: 'single_choice', question: '离太阳最近的行星是哪一颗？', options: ['水星', '金星', '地球', '火星'], answer: 0, explanation: '水星位于太阳系最内侧，平均轨道半径最小。' },
]

function json(response, status, body) {
  response.writeHead(status, {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json; charset=utf-8',
  })
  response.end(JSON.stringify(body))
}

http.createServer((request, response) => {
  if (request.method === 'OPTIONS') return json(response, 204, {})
  if (request.url === '/api/examples') return json(response, 200, { examples })
  if (request.url === '/api/generate' && request.method === 'POST') {
    return json(response, 200, { session_id: `mock-${Date.now()}`, topic: '太阳系基础知识', questions })
  }
  if (request.url === '/api/report' && request.method === 'POST') {
    return json(response, 200, {
      accuracy: 2 / 3,
      correct_count: 2,
      total_count: 3,
      mastered: [questions[0].question, questions[1].question],
      weak: [questions[2].question],
      summary: '你已掌握太阳与主要行星的基础概念，建议再复习行星与太阳的距离顺序。',
      encouragement: '再挑战一次，把最后一个知识点拿下。',
    })
  }
  return json(response, 404, { detail: 'Not found' })
}).listen(8000, '127.0.0.1', () => console.log('Mock API: http://127.0.0.1:8000'))
