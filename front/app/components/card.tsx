import { ReactNode } from 'react';
import styles from './card.css'

export function links() {
  return [{rel: 'stylesheet', href: styles}]
}
interface Image {
  src: string;
  alt: string;
}

interface IProps {
  children: ReactNode;
  color: string;
  image?: Image;
}

export function Card(props: IProps) {
  return (
    <div className={props.image ? 'card image': 'card'} style={{borderColor: props.color}}>
      {props.image ? (
        <>
          <img {...props.image}/>
          <div className='child-content'>{props.children}</div>
        </>
      ) : <div className='child-content'>{props.children}</div>}
    </div>
  )
}
