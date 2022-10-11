import type { ReactNode } from "react";
import styles from "./card.css";

export function links() {
  return [{ rel: "stylesheet", href: styles }];
}
interface Image {
  src: string;
  alt: string;
}

interface IProps {
  children?: ReactNode;
  color: string;
  image?: Image;
  clickable?: boolean;
}

export function Card(props: IProps) {
  return (
    <div
      className={`card ${props.image && "image"} ${
        props.clickable && "clickable"
      }`}
      style={{ borderColor: props.color }}
    >
      {props.image ? (
        <>
          <img {...props.image} />
          <div className="child-content">{props.children}</div>
        </>
      ) : (
        <div className="child-content">{props.children}</div>
      )}
    </div>
  );
}
