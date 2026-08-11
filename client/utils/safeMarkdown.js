export function formatSafeMarkdown(text) {
  return String(text || '')
    .split('\n')
    .map((line, lineIndex) => ({
      id: `line-${lineIndex}`,
      segments: parseStrongSegments(line),
    }))
}

function parseStrongSegments(line) {
  const segments = []
  const pattern = /\*\*(.+?)\*\*/g
  let cursor = 0
  let match

  while ((match = pattern.exec(line)) !== null) {
    if (match.index > cursor) {
      segments.push({ text: line.slice(cursor, match.index), strong: false })
    }

    segments.push({ text: match[1], strong: true })
    cursor = match.index + match[0].length
  }

  if (cursor < line.length || segments.length === 0) {
    segments.push({ text: line.slice(cursor), strong: false })
  }

  return segments
}
