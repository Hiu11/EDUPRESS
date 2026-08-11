import assert from 'node:assert/strict'
import test from 'node:test'

import { formatSafeMarkdown } from '../../utils/safeMarkdown.js'

test('formats strong markdown without producing html strings', () => {
  const [line] = formatSafeMarkdown('Read **this part** carefully')

  assert.deepEqual(line.segments, [
    { text: 'Read ', strong: false },
    { text: 'this part', strong: true },
    { text: ' carefully', strong: false },
  ])
})

test('keeps script tags as escaped Vue text data', () => {
  const payload = '<script>alert("xss")</script> **safe label**'
  const [line] = formatSafeMarkdown(payload)

  assert.equal(line.segments[0].text, '<script>alert("xss")</script> ')
  assert.equal(line.segments[0].strong, false)
  assert.equal(line.segments[1].text, 'safe label')
  assert.equal(line.segments[1].strong, true)
})

test('keeps event handlers and javascript urls as plain text', () => {
  const payload = '<img src=x onerror=alert(1)> [x](javascript:alert(1))'
  const [line] = formatSafeMarkdown(payload)

  assert.equal(line.segments.length, 1)
  assert.equal(line.segments[0].text, payload)
  assert.equal(line.segments[0].strong, false)
})

test('preserves line breaks as separate render lines', () => {
  const lines = formatSafeMarkdown('one\n**two**')

  assert.equal(lines.length, 2)
  assert.equal(lines[0].segments[0].text, 'one')
  assert.deepEqual(lines[1].segments, [{ text: 'two', strong: true }])
})
