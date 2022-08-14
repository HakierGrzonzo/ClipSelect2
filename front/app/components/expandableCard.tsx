import { ReactNode, useReducer } from 'react';
import styles from './expandableCard.css'

export function links() {
  return [{rel: 'stylesheet', href: styles}]
}

interface Image {
  src: string;
  alt: string;
}

interface IProps {
  children?: ReactNode;
  header: ReactNode;
  color: string;
  image: Image;
  expanded?: boolean;
}

export function ExpandableCard(props: IProps) {
  const { header, color, image } = props;
  const [expanded, toggleExpanded] = useReducer<boolean>((state: boolean) => !state, props.expanded || false)

  return (
    <a onClick={() => toggleExpanded()} className={`expandable-card ${expanded && 'expanded'}`}>
      <div className='expandable-card-header'>
        <img {...props.image}/>
        {header}
      </div>
      <div className='expandable-card-content'>
        {props.children}
      </div>
    </a>
  )
}
