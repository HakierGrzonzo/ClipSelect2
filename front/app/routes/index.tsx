import { json, LinksFunction, LoaderFunction } from "@remix-run/node"; // or cloudflare/deno
import { Card, CardLinks } from '../components';
import { backendClient } from '../api'
import { colors } from '../colors'
import { Link, useLoaderData } from "@remix-run/react";
import { Series } from "../client/models/Series";

export const links: LinksFunction = () => {
  return [...CardLinks()]
}

export const loader: LoaderFunction = async () => {
  const series = await backendClient.series.getSeriesSeriesGet();
  return json(series)
}

export default function() {
  const series = useLoaderData() as unknown as Series[];
  return <>
    <h1>ClipSelect</h1>
    <article class='tile'>
      {series.map(s => (
        <Link key={s.id} to={`/series/${s.name}`}>
          <Card color={colors.accentColor}>
            {s.name}
          </Card>
        </Link>
      ))}
    </article>
  </>
}
