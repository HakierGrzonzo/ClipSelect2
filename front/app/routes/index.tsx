import type { LinksFunction, LoaderFunction } from "@remix-run/node";
import { json } from "@remix-run/node"; // or cloudflare/deno
import { Link, useLoaderData } from "@remix-run/react";
import { Card, CardLinks } from "../components";
import { backendClient, useFrontend } from "../api";
import { colors } from "../colors";
import type { Series } from "../client/models/Series";

export const links: LinksFunction = () => {
  return [...CardLinks()];
};

export const loader: LoaderFunction = async () => {
  const series = await backendClient.series.getSeriesSeriesGet();
  return json(series);
};

export default function () {
  const series = useLoaderData() as unknown as Series[];
  const {frontendURL} = useFrontend()
  return (
    <article>
      <p>
        ClipSelect allows you to generete gifs from your{' '}
        <em>
          (or rather mine, cause I am the one person running it)
        </em>{' '}
        favorite shows.
      </p>
      <p>
        To start, select any of the {series.length} shows we have on offer!
      </p>
      <div className="tile">
        {series.map((s) => (
          <Link 
            key={s.id} 
            to={`/series/${s.name}`}
            style={{ textDecoration: "none", color: colors.textColor}}
          >
            <Card 
              clickable 
              color={colors.accentColor}
              image={{src: `${frontendURL}/series/${s.id}/cover.jpg`, alt: `Coverart for ${s.name}`}}
            >
              {s.name}
            </Card>
          </Link>
        ))}
      </div>
    </article>
  );
}
