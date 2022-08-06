import { Link, Outlet } from "@remix-run/react";

export default function Foo() {
  return (
    <div>
        <p>Hello to foo</p>
        <div>
          <Outlet />
        </div>
        <Link to="/">go the fuck back</Link>
    </div>
  )
}
