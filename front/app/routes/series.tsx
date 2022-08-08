import { Link, Outlet } from "@remix-run/react";

export default function Series() {
  return (
    <div> 
        <Link to={'/'}>Go back</Link>
      <h2>Series:</h2>
      <Outlet/>
    </div>
  )
}
