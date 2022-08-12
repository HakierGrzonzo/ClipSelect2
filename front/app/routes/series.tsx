import { Link, Outlet } from "@remix-run/react";

export default function() {
  return (
    <>
      <Link to='/'>go back</Link>
      <article>
        <Outlet/>
      </article>
    </>
  )
}
