import { json } from '@remix-run/node'
import { Link, Outlet, useLoaderData } from '@remix-run/react'
import { Series, DataService } from '../client'

export const loader = async () => {
  const series = await DataService.getSeriesSeriesGet()
  return json(series)
}

export default function Main() {
  const series = useLoaderData()
  return (
    <div>
      <h1>ClipSelect2</h1>
      <p>Welcome to ClipSelect2, we have like {series.length} things here</p>
      <ol>
        {series.map((s: Series) => (
          <li key={s.id}><Link to={`series/${s.name}`}>{s.name}</Link></li>
        ))}
      </ol>
      <Outlet />
    </div>
  )
}
