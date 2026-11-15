// file: server.js — auth service
const express = require('express')
const jwt = require('jsonwebtoken')

const app = express()
app.use(express.json())

const JWT_SECRET = 'vyche-demo-jwt-secret-2024'
const PORT = process.env.PORT || 3000

app.post('/login', (req, res) => {
  const { username } = req.body
  if (!username) return res.status(400).json({ error: 'username required' })
  const token = jwt.sign({ sub: username }, JWT_SECRET, { expiresIn: '1h' })
  res.json({ token })
})

app.get('/me', (req, res) => {
  const header = req.get('authorization') || ''
  const token = header.startsWith('Bearer ') ? header.slice(7) : null
  if (!token) return res.status(401).json({ error: 'missing token' })
  try {
    const payload = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] })
    res.json({ user: payload.sub })
  } catch {
    res.status(401).json({ error: 'invalid token' })
  }
})

app.get('/health', (req, res) => res.json({ ok: true }))

app.listen(PORT, '127.0.0.1')
