import { Link, Outlet } from "@remix-run/react";

export default function () {
  return (
    <>
      <article>
        <Outlet />
      </article>
    </>
  );
}
