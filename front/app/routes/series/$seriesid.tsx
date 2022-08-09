import { json, LoaderFunction } from '@remix-run/node'
import { Link, Outlet, useLoaderData } from '@remix-run/react'
import { FullSeries } from '~/client';
import { backendClient } from '~/api';

export const loader: LoaderFunction = async ({params}) => {
  const { seriesid } = params;
  const series = await backendClient.series.getSeriesByTitleSeriesByTitleGet(seriesid)
  return json(series)
}

export default function Series() {
  const series = useLoaderData() as unknown as FullSeries
  return (
    <div>
        <h2>{series.name}</h2>
        <Outlet/>
        <ul>
            {series.subseries.sort((a, b) => a.order - b.order).map(subseries => (
            <li key={subseries.id}>{subseries.name}
                <ul>
                    {subseries.episodes.sort((a, b) => a.order - b.order).map(episode => (
                    <li key={episode.id}>
                        <Link to={`${episode.id}`}>{episode.order} - {episode.name}</Link>
                    </li>
                    ))}
                </ul>
            </li>
            ))}
        </ul>
    </div>
  )
}
