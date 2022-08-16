import type { LinksFunction } from '@remix-run/node'
import { useEffect, useReducer } from 'react'
import type { Caption } from '../client/models/Caption'
import styles from './ClipList.css'

function addLeadingZero(n: number, fixedPrecision = 0): string {
  if (n === 0)
    return '00'

  if (n < 10)
    return `0${n.toFixed(fixedPrecision)}`

  return n.toFixed(fixedPrecision)
}

function formatTime(time: number): string {
  const seconds = time % 60
  const minutes = (time - seconds) / 60 % 60
  const hours = (time - seconds - 60 * minutes) / 60
  return `${hours}:${addLeadingZero(minutes)}:${addLeadingZero(seconds, 2)}`
}

export const links: LinksFunction = () => {
  return [{ rel: 'stylesheet', href: styles }]
}

interface IProps {
  captions: Caption[]
  selectedCaption: Caption
  setSelectedRange: (foo: [Caption, Caption] | undefined) => void
}

type range = [number, number]

const checkIfInRange = (r: range, value: number): boolean => value >= r[0] && value <= r[1]

const reducer = (state: range, action: number): range => {
  const [start, end] = state
  const mid = (start + end) / 2
  if (start > end)
    return [action, action]
  if (action < start)
    return [action, end]
  if (action > end)
    return [start, action]
  if (action <= mid)
    return [action + 1, end]
  if (action > mid)
    return [start, action - 1]
  return state
}

export function ClipList(props: IProps) {
  const { captions, selectedCaption, setSelectedRange } = props
  const [selectedRange, setRange] = useReducer<range>(reducer, [selectedCaption.order, selectedCaption.order])

  useEffect(() => {
    const candidate = captions.filter(c => selectedRange.includes(c.order))
    if (candidate.length === 1)
      setSelectedRange([candidate[0], candidate[0]])
    else if (candidate.length === 2)
      setSelectedRange(candidate as [Caption, Caption])
    else
      setSelectedRange(undefined)
  }, [
    selectedRange, captions, setSelectedRange,
  ])

  return (
    <ul className="clip-list">
      {captions.filter(caption => Math.abs(caption.order - selectedCaption.order) < 5).map((caption) => {
        const isSelected = checkIfInRange(selectedRange, caption.order)
        return (
          <li key={caption.id} className={isSelected ? 'selected' : ''} onClick={() => setRange(caption.order)}>
            <div className="clip-list-header">
              <span>{caption.text}</span>
            </div>
            <div className="clip-list-footer">
              {isSelected ? <i>currently selected</i> : <i>{formatTime(caption.start)} - {formatTime(caption.stop)}</i>}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
