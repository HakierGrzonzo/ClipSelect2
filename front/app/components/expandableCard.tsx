import type { ReactNode } from 'react'
import { useReducer } from 'react'
import styles from './expandableCard.css'

export function links() {
  return [{ rel: 'stylesheet', href: styles }]
}

interface Image {
  src: string
  alt: string
}

interface IProps {
  children?: ReactNode
  header: ReactNode
  color: string
  image: Image
  expanded?: boolean
}

export function ExpandableCard(props: IProps) {
  const { header, image } = props
  const [expanded, toggleExpanded] = useReducer<boolean>((state: boolean) => !state, props.expanded || false)

  return (
    <div className={`expandable-card ${expanded ? 'expanded' : ''}`}>
        <div onClick={() => toggleExpanded()} className="expandable-card-header">
          <img {...image}/>
          {header}
        </div>
        <div className="expandable-card-content">
          {props.children}
        </div>
    </div>
  )
}
