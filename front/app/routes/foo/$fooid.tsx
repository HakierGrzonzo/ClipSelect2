import { LoaderFunction } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useLoaderData } from "@remix-run/react";

export const loader: LoaderFunction = async({
  params,
}) => {
  console.log('got', params)
  return json(parseInt(params.fooid));
}

export default function Fooid() {
  const data = useLoaderData();
  return (
    <>
      <p>Got {data} for fooid</p>
      <p><Link to={`../${data + 1}`}>Go to {data + 1}</Link></p>
    </>
  )
}
