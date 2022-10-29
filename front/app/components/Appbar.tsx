import { Link } from '@remix-run/react';
import styles from './Appbar.css';

export function links() {
  return [{rel: "stylesheet", href: styles}]
}

export function AppBar() {
  return (
    <nav>
      <div className="inner">
        <h1>
          <Link to="/">
            ClipSelect
          </Link>
        </h1>
      </div>
    </nav>
  )
}
