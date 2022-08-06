import { json, LoaderFunction } from '@remix-run/node'
import { Link, useLoaderData } from '@remix-run/react'
import { DefaultService, Series } from '../../client'

interface IParams {
  seriesid: string
}

export const loader: LoaderFunction = async ({params}) => {
  const { seriesid } = params;
  const series = await DefaultService.getSeriesSeriesGet()
  return json(series.find(s => s.id === seriesid).subseries)
}

export default function Series() {
  const subSeries = useLoaderData()
  return (
    <p>{JSON.stringify(subSeries)}</p>
  )
}
